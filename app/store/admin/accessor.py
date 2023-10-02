import typing
import bcrypt
import base64
from sqlalchemy import select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        admin = await self.get_by_email(email=self.app.config.admin.email)
        if admin is None:
            await self.create_admin(
                email=app.config.admin.email,
                password=app.config.admin.password
            )

    async def get_by_email(self, email: str) -> Admin | None:
        async with self.app.database.session() as session:
            query = select(AdminModel).where(AdminModel.email == email)
            result = await session.execute(query)
            admin = result.scalars().first()
            if admin:
                return admin.get_object()

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session() as session:
            admin = AdminModel(
                email=email,
                password=self._password_hasher(password)
            )
            session.add(admin)
            await session.commit()
            return admin.get_object()

    @staticmethod
    def _password_hasher(raw_password: str) -> str:
        hash_binary = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
        encoded = base64.b64encode(hash_binary)
        return encoded.decode("utf-8")
