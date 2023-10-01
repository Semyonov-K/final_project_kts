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
    async def create_user(self, vk_id: int) -> User:
        async with self.app.database.session() as session:
            user = UserModel(
                vk_id=vk_id
            )
            session.add(user)
            await session.commit()
            return user.get_object()


    async def get_user_by_vk_id(self, vk_id: int) -> Optional[User]:
        async with self.app.database.session() as session:
            query_user = select(UserModel).where(UserModel.vk_id==vk_id)
            result = await session.execute(query_user)
            user = result.scalars().first()
            if user:
                return user.get_object()


    async def get_gamescore_user_by_vk_id(self, vk_id: int) -> Optional[GameScore]:
        async with self.app.database.session() as session:
            query_gamescore = select(GameScoreModel).where(GameScoreModel.vk_id==vk_id)
            result = await session.execute(query_gamescore)
            gamescore = result.scalars().first()
            if gamescore:
                return gamescore.get_object()
            else:
                return None


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
            query_stock = select(StockModel).where(StockModel.stock_id==stock_id)
            result = await session.execute(query_stock)
            stock = result.scalars().first()
            if stock:
                return stock.get_object()
            else:
                return None


    async def create_game(
        self, chat_id: int,
    ) -> Game:
        async with self.app.database.session() as session:
            game = GameModel(chat_id=chat_id)
            session.add(game)
            await session.commit()
            return game.get_object()


    async def get_game(self, chat_id: int) -> Optional[Game]:
        async with self.app.database.session() as session:
            query_game = select(GameModel).where(GameModel.chat_id==chat_id)
            result = await session.execute(query_game)
            game = result.scalars().first()
            if game:
                return game.get_object()
            else:
                return None
    

    async def update_game(
            self,
            chat_id: int,
            user: Optional[User],
            stock: Optional[Stock]
        ) -> Optional[Game]:
        async with self.app.database.session() as session:
            query_game = select(GameModel).where(GameModel.chat_id==chat_id)
            result = await session.execute(query_game)
            game = result.scalars().first()
            if game:
                if user:
                    game.users.append(user)
                if stock:
                    game.stock.append(stock)
                await session.commit()
                return game.get_object()
            else:
                return None