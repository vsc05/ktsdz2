import typing

from app.store.vk_api.dataclasses import Message

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

    async def handle_updates(self, updates: list):
        """
        Обрабатывает список обновлений, полученных от VK API.
        """
        for update in updates:
            # Проверяем, что это новое входящее сообщение
            if update.type == 'message_new':
                # Получаем ID пользователя и текст сообщения
                user_id = update.object.message.id
                incoming_message_text = update.object.message.text

                if incoming_message_text.strip() != '':
                    response_message_text = 'Спасибо за ваше сообщение! Ваше обращение обрабатывается.'
                    message = Message(user_id,response_message_text)
                    await self.app.store.vk_api.send_message(message)