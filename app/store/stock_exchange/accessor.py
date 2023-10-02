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
    

    async def update_user(
            self,
            vk_id: int,
            score: Optional[int],
            stock_one: Optional[int],
            stock_two: Optional[int],
            stock_three: Optional[int],
            stock_one_sell: Optional[int],
            stock_two_sell: Optional[int],
            stock_three_sell: Optional[int],
            stock_one_buy: Optional[int],
            stock_two_buy: Optional[int],
            stock_three_buy: Optional[int]
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
            total_score: Optional[int],
            total_games: Optional[int],
            total_win: Optional[int]
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
            stock: Optional[Stock],
            number_of_moves: Optional[int]
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
                if number_of_moves:
                    game.number_of_moves = number_of_moves
                await session.commit()
                return game.get_object()
            else:
                return None

    async def delete_game(self, chat_id: int) -> None:
        async with self.app.database.session() as session:
            game = await session.query(GameModel).filter_by(chat_id=chat_id).first()
            if game:
                session.delete(game)
                await session.commit()
