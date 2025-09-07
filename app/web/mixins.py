from aiohttp_session import get_session
from aiohttp.abc import StreamResponse
from aiohttp.web_exceptions import HTTPUnauthorized


class AuthRequiredMixin:
    async def _iter(self) -> StreamResponse:
        cookies = getattr(self.request, "cookies", None)
        if cookies is None:
            raise HTTPUnauthorized
        try:
            print(cookies["AIOHTTP_SESSION"])
        except Exception:
            raise HTTPUnauthorized
        return await super(AuthRequiredMixin, self)._iter()

    async def get_session(self):
        # Возвращает объект сессии
        return await get_session(self.request)

    async def clear_user_session(self):
        # Очищает сессию пользователя
        session = await self.get_session()
        session.invalidate()