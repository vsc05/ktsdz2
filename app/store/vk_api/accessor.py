import typing
from urllib.parse import urlencode, urljoin

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"
# Настройки VK API
VK_API_URL = 'https://api.vk.com/method/'


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        # TODO: добавить создание aiohttp ClientSession,
        #  получить данные о long poll сервере с помощью метода groups.getLongPollServer
        #  вызвать метод start у Poller
        self.session = ClientSession()
        self.poller = Poller(store=self.app.store.vk_api)
        await self._get_long_poll_service()
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        # TODO: закрыть сессию и завершить поллер
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()
        self.session = None
        self.poller = None

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        """
        Получить параметры Long Poll сервера и сохранить их в состоянии accessor'а.
        """
        params = {
            'access_token': self.app.config.bot.token,
            'group_id': self.app.config.bot.group_id,
            'v': API_VERSION
        }
        response = await self.session.get(VK_API_URL + 'groups.getLongPollServer', params=params)
        response_data = await response.json()
        if 'response' in response_data:
            self.key = response_data['response']['key']
            self.server = response_data['response']['server']
            self.ts = response_data['response']['ts']

    async def poll(self):
        """
        Отправить Long Poll запрос и вернуть список Update.
        """
        params = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': 25
        }
        response = await self.session.get(self.server, params=params)
        response_data = await response.json()
        updates = response_data.get('updates', [])
        self.ts = response_data.get('ts', self.ts)
        return updates

    async def send_message(self, message: Message) -> None:
        """
        Отправить сообщение через VK API.
        """
        params = {
            'access_token': self.token,
            'user_id': message.user_id,
            'message': message.text,
            'random_id': 0,  # Используйте реальный уникальный id для каждого сообщения
            'v': API_VERSION
        }
        await self.session.post(VK_API_URL + 'messages.send', params=params)