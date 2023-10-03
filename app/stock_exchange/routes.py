import typing

from app.stock_exchange.views import StockCreateView, StockGetView, ChatGetView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/stex.add_stock", StockCreateView)
    app.router.add_view("/stex.stock", StockGetView)
    app.router.add_view("/chat.view", ChatGetView)