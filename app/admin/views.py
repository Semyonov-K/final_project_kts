from aiohttp.web import HTTPForbidden, HTTPOk
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, HTTPOk)
    async def post(self):
        email = self.data.get("email")
        password = self.data.get("password")
        admin = await self.store.admins.get_by_email(email)
        if admin is None or admin.is_password_valid(password) is None:
            raise HTTPForbidden
        response_data = AdminSchema().dump(admin)
        session = await new_session(request=self.request)
        session["admin"] = response_data
        return json_response(data=response_data)


class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminSchema, HTTPOk)
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
