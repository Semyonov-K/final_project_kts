from aiohttp_apispec import querystring_schema, request_schema, response_schema, docs
from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp.web import HTTPForbidden, HTTPOk
from app.stock_exchange.schemes import (
    UserRequestSchema,
    UserResponseSchema,
    UserIdSchema,
    GameIdSchema,
    GameRequestSchema,
    GameResponseSchema,
    GameScoreResponseSchema,
    StockIdSchema,
    StockRequestSchema,
    StockResponseSchema
)
from app.web.app import View
# from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class UserAddView(View):
    @docs(
            tags=["VK Stock Exchange"],
            summary="Добавить пользователя",
            description="Добавить пользователя в игру"
    )
    @request_schema(UserRequestSchema)
    @response_schema(UserResponseSchema, HTTPOk)
    async def post(self):
        vk_id = self.data.get("vk_id")
        first_name = self.data.get("first_name")
        last_name = self.data.get("last_name")
        user = await self.store.stockexchange.create_user(
            vk_id=vk_id,
            first_name=first_name,
            last_name=last_name,
        )
        return json_response(data=UserResponseSchema().dump(user))


class UserScoreView(View):
    @docs(
            tags=["VK Stock Exchange"],
            summary="Просмотр пользователя с его статистикой",
            description="Просмотр пользователя и его статистики"
    )
    @request_schema(UserIdSchema)
    @response_schema(UserResponseSchema, HTTPOk)
    async def get(self):
        vk_id = self.request.query.get("vk_id")
        user = await self.store.stockexchange.get_user_by_vk_id(vk_id=vk_id)
        return json_response(data=UserResponseSchema().dump(user))


class StockCreateView(View):
    @docs(
            tags=["VK Stock Exchange"],
            summary="Добавить акцию",
            description="Добавить акцию в игру"
    )
    @request_schema(StockRequestSchema)
    @response_schema(StockResponseSchema, HTTPOk)
    async def post(self):
        name = self.data.get("name")
        price = self.data.get("price", None)
        stock = await self.store.stockexchange.create_stock(
            name=name,
            price=price
        )
        return json_response(data=StockResponseSchema().dump(stock))


class GameCreateView(View):
    @docs(
            tags=["VK Stock Exchange"],
            summary="Создать игру",
            description="Создать игру"
    )
    @request_schema(GameRequestSchema)
    @response_schema(GameResponseSchema, HTTPOk)
    async def post(self):
        chat_id = self.data.get("chat_id")
        list_users = self.data.get("list_users")
        list_stocks = self.data.get("list_stocks")
        game = await self.store.stockexchange.create_game(
            chat_id=chat_id,
            list_users=list_users,
            list_stocks=list_stocks
        )
        return json_response(data=GameResponseSchema().dump(game))
