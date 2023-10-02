from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema, AdminSchemaData
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchemaData, 200)
    async def post(self):
        data = await self.request.json()
        admin = await self.store.admins.get_by_email(data['email'])
        if not admin:
            raise HTTPForbidden
        response_data = AdminSchemaData().dump(admin)
        session = await new_session(request=self.request)
        session['admin_data'] = response_data
        return json_response(data=response_data)


class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminSchemaData, 200)
    async def get(self):
        return json_response(data=AdminSchemaData().dump(self.request.admin))
