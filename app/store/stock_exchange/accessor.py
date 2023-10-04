from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.stock_exchange.models import (
    User, UserModel,
    GameScore, GameScoreModel,
    Stock, StockModel,
    Game, GameModel
)
from app.web.app import Application

class StockExchangeAccessor(BaseAccessor):
    async def connect(self, app: Application):
        await self.create_stock(name="BeerBank", price=1000)
        await self.create_stock(name="tAssla", price=1000)
        await self.create_stock(name="CringeCompany", price=1000)

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
            else:
                return None
    

    async def update_user(
            self,
            vk_id: int,
            score: Optional[int] = None,
            stock_one: Optional[int] = None,
            stock_two: Optional[int] = None,
            stock_three: Optional[int] = None,
            stock_one_sell: Optional[int] = None,
            stock_two_sell: Optional[int] = None,
            stock_three_sell: Optional[int] = None,
            stock_one_buy: Optional[int] = None,
            stock_two_buy: Optional[int] = None,
            stock_three_buy: Optional[int] = None
        ) -> Optional[User]:
        async with self.app.database.session() as session:
            query_user = select(UserModel).where(UserModel.vk_id==vk_id)
            result = await session.execute(query_user)
            user = result.scalars().first()
            if user:
                if score:
                    user.score = score
                if stock_one:
                    user.stock_one = stock_one
                if stock_two:
                    user.stock_two = stock_two
                if stock_three:
                    user.stock_three = stock_three
                if stock_one_sell:
                    user.stock_one_sell = stock_one_sell
                if stock_two_sell:
                    user.stock_two_sell = stock_two_sell
                if stock_three_sell:
                    user.stock_three_sell = stock_three_sell
                if stock_one_buy:
                    user.stock_one_sell = stock_one_buy
                if stock_two_buy:
                    user.stock_two_sell = stock_two_buy
                if stock_three_buy:
                    user.stock_three_sell = stock_three_buy
                await session.commit()
                return user.get_object()
            else:
                return None

    async def delete_user(self, vk_id: int) -> None:
        async with self.app.database.session() as session:
            query_user = select(UserModel).where(UserModel.vk_id==vk_id)
            result = await session.execute(query_user)
            user = result.scalars().first()
            if user:
                await session.delete(user)
                await session.commit()

    async def create_gamescore_user_by_vk_id(self, vk_id: int) -> Optional[GameScore]:
        async with self.app.database.session() as session:
            gamescore = GameScoreModel(
                vk_id=vk_id
            )
            session.add(gamescore)
            await session.commit()
            return gamescore.get_object()

    async def get_gamescore_user_by_vk_id(self, vk_id: int) -> Optional[GameScore]:
        async with self.app.database.session() as session:
            query_gamescore = select(GameScoreModel).where(GameScoreModel.vk_id==vk_id)
            result = await session.execute(query_gamescore)
            gamescore = result.scalars().first()
            if gamescore:
                return gamescore.get_object()
            else:
                return None
    
    async def update_gamescore(
            self,
            vk_id: int,
            total_score: Optional[int] = None,
            total_games: Optional[int] = None,
            total_win: Optional[int] = None
        ) -> Optional[GameScore]:
        async with self.app.database.session() as session:
            query_score = select(GameScoreModel).where(GameScoreModel.vk_id==vk_id)
            result = await session.execute(query_score)
            score = result.scalars().first()
            if score:
                if total_score:
                    score.total_score = total_score
                if total_games:
                    score.total_games = total_games
                if total_win:
                    score.total_win = total_win
                await session.commit()
                return score.get_object()
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
    

    async def update_stock(self, stock_id: int, new_price: int) -> Optional[Stock]:
        async with self.app.database.session() as session:
            query_stock = select(StockModel).where(StockModel.stock_id==stock_id)
            result = await session.execute(query_stock)
            stock = result.scalars().first()
            if stock:
                stock.price = new_price
                await session.commit()
                return stock.get_object()
            else:
                return None
    
    async def delete_stock(self, stock_id: int) -> None:
        async with self.app.database.session() as session:
            query_stock = select(StockModel).where(StockModel.stock_id==stock_id)
            result = await session.execute(query_stock)
            stock = result.scalars().first()
            if stock:
                await session.delete(stock)
                await session.commit()


    async def create_game(
        self, chat_id: int
    ) -> Game:
        async with self.app.database.session() as session:
            game = GameModel(chat_id=chat_id, users=[], stocks=[])
            session.add(game)
            await session.commit()
            return game.get_object()


    async def get_game(self, chat_id: int) -> Optional[Game]:
        async with self.app.database.session() as session:
            query_game = select(GameModel).where(GameModel.chat_id==chat_id).options(selectinload(GameModel.users)).options(selectinload(GameModel.stocks))
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
            stock: Optional[Stock],
            number_of_moves: Optional[int]
        ) -> Optional[Game]:
        async with self.app.database.session() as session:
            query_game = select(GameModel).where(GameModel.chat_id==chat_id).options(selectinload(GameModel.users)).options(selectinload(GameModel.stocks))
            if stock:
                query_stock = select(StockModel).where(StockModel.stock_id==stock.stock_id)
                result_stock = await session.execute(query_stock)
                game_stock = result_stock.scalars().first()
            if user:
                query_user = select(UserModel).where(UserModel.vk_id==user.vk_id)
                result_user = await session.execute(query_user)
                game_user = result_user.scalars().first()
            result = await session.execute(query_game)
            game = result.scalars().first()
            if game:
                if user:
                    game.users.append(game_user)
                if stock:
                    game.stocks.append(game_stock)
                if number_of_moves:
                    game.number_of_moves = number_of_moves
                await session.commit()
                return game.get_object()
            else:
                return None

    async def delete_game(self, chat_id: int) -> None:
        async with self.app.database.session() as session:
            query_game = select(GameModel).where(GameModel.chat_id==chat_id).options(selectinload(GameModel.users)).options(selectinload(GameModel.stocks))
            result = await session.execute(query_game)
            game = result.scalars().first()
            if game:
                await session.delete(game)
                await session.commit()
