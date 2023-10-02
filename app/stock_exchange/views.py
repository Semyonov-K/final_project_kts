from aiohttp_apispec import querystring_schema, request_schema, response_schema, docs
from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp.web import HTTPForbidden, HTTPOk
from app.stock_exchange.schemes import (
    StockIdSchema,
    StockRequestSchema,
    StockResponseSchema
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class StockCreateView(AuthRequiredMixin, View):
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


class StockGetView(AuthRequiredMixin, View):
    @docs(
            tags=["VK Stock Exchange"],
            summary="Получить акцию",
            description="Получить акцию из БД"
    )
    @request_schema(StockIdSchema)
    @response_schema(StockResponseSchema, HTTPOk)
    async def get(self):
        stock_id = self.request.query.get("stock_id")
        stock = await self.store.stockexchange.get_stock(stock_id)
        if stock is None:
            stock = []
        return json_response(data={"stock": StockResponseSchema().dump(stock)})