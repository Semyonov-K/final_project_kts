from typing import Optional
from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.stock_exchange.models import (
    User, UserModel,
    GameScore, GameScoreModel,
    Stock, StockModel,
    Game, GameModel
)


class StockExchangeAccessor(BaseAccessor):
    async def create_user(self, vk_id: int, first_name: str, last_name: str) -> User:
        async with self.app.database.session() as session:
            user = UserModel(
                vk_id=vk_id,
                first_name=first_name,
                last_name=last_name)
            session.add(user)
            await session.commit()
            return user.get_object()


    async def get_user_by_vk_id(self, vk_id: int) -> Optional[User]:
        async with self.app.database.session() as session:
            query = select(UserModel).where(UserModel.vk_id==vk_id)
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                return user.get_object()
            


    # async def get_game_score(self, vk_id: int) -> Optional[GameScore]:
    #     async with self.app.database.session() as session:
    #         query = select(GameScoreModel).where(GameScoreModel.vk_id==vk_id)
    #         result = await session.execute(query)
    #         game_score = result.scalars().first()
    #         if game_score:
    #             return game_score.get_object()


    async def create_stock(self, name: str, price: Optional[int]=1000) -> Stock:
        async with self.app.database.session() as session:
            stock = StockModel(
                name=name,
                price=price)
            session.add(stock)
            await session.commit()
            return stock.get_object()


    async def get_stock(self, stock_id: int) -> Optional[Stock]:
        async with self.app.database.session() as session:
            query = select(StockModel).where(StockModel.stock_id==stock_id)
            result = await session.execute(query)
            stock = result.scalars().first()
            if stock:
                return stock.get_object()


    async def create_game(
        self, chat_id: int, list_users: list[User], list_stocks: list[Stock]
    ) -> Game:
        async with self.app.database.session() as session:
            game = GameModel(chat_id=chat_id)
            game.users.extend(list_users)
            game.stocks.extend(list_stocks)
            session.add(game)
            await session.commit()
            return game.get_object()


    async def get_game(self, chat_id) -> Optional[Game]:
        async with self.app.database.session() as session:
            query = select(GameModel).where(GameModel.chat_id==chat_id)
            result = await session.execute(query)
            game = result.scalars().first()
            if game:
                return game.get_object()
