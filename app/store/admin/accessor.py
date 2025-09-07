import typing
from hashlib import sha256

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        # TODO: создать админа по данным в config.yml здесь
        try:
            if not self.app.database.admins:
                admin_email = self.app.config.admin.email
                admin_password = self.app.config.admin.password
                admin = await self.create_admin(email=admin_email, password=admin_password)
                self.logger.debug(f"{admin.email} is connected")
        except Exception as e:
            self.logger.exception(e)

    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        hashed_password = sha256(password.encode()).hexdigest()
        admin = Admin(1, email=email, password=hashed_password)
        self.app.database.admins.append(admin)
        return admin