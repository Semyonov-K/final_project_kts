from dataclasses import dataclass
from typing import Optional, List
from app.store.database.sqlalchemy_base import db
from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship


@dataclass
class User:
    vk_id: int
    score: int
    stock_one: int
    stock_two: int
    stock_three: int
    stock_one_sell: int
    stock_two_sell: int
    stock_three_sell: int
    stock_one_buy: int
    stock_two_buy: int
    stock_three_buy: int


class UserModel(db):
    __tablename__ = 'user'

    vk_id = Column(Integer, primary_key=True)
    score = Column(Integer, default=10000)
    stock_one = Column(Integer, default=0)
    stock_two = Column(Integer, default=0)
    stock_three = Column(Integer, default=0)
    stock_one_buy = Column(Integer, default=0)
    stock_two_buy = Column(Integer, default=0)
    stock_three_buy = Column(Integer, default=0)
    stock_one_sell = Column(Integer, default=0)
    stock_two_sell = Column(Integer, default=0)
    stock_three_sell = Column(Integer, default=0)
    game_user_id = Column(BigInteger, ForeignKey("game.game_id", ondelete="CASCADE"))
    game_user = relationship("GameModel")

    def get_object(self) -> User:
        return User(
            vk_id=self.vk_id,
            score=self.score,
            stock_one=self.stock_one,
            stock_two=self.stock_two,
            stock_three=self.stock_three,
            stock_one_sell=self.stock_one_sell,
            stock_two_sell=self.stock_two_sell,
            stock_three_sell=self.stock_three_sell,
            stock_one_buy=self.stock_one_buy,
            stock_two_buy=self.stock_two_buy,
            stock_three_buy=self.stock_three_buy
        )


@dataclass
class GameScore:
    score_id: int
    vk_id: int
    total_score: int
    total_games: int
    total_win: int


class GameScoreModel(db):
    __tablename__ = 'game_score'

    score_id = Column(Integer, primary_key=True, autoincrement=True )
    vk_id = Column(Integer)
    total_score = Column(Integer, default=0)
    total_games = Column(Integer, default=0)
    total_win = Column(Integer, default=0)


    def get_object(self) -> GameScore:
        return GameScore(
            score_id=self.score_id,
            vk_id=self.vk_id,
            total_score=self.total_score,
            total_games=self.total_games,
            total_win=self.total_win,
        )


@dataclass
class Stock:
    stock_id: int
    name: str
    price: int


class StockModel(db):
    __tablename__ = "stock"

    stock_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    price = Column(Integer, default=1000)
    game_stock_id = Column(BigInteger, ForeignKey("game.game_id", ondelete="CASCADE"))
    game_stock = relationship("GameModel")

    def get_object(self) -> Stock:
        return Stock(
            stock_id=self.stock_id,
            name=self.name,
            price=self.price
        )


@dataclass
class Game:
    game_id: int
    chat_id: int
    users: list[User]
    stocks: list[Stock]
    number_of_moves: int


class GameModel(db):
    __tablename__ = "game"

    game_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer)
    users = relationship("UserModel")
    stocks = relationship("StockModel")
    number_of_moves = Column(Integer, default=1)

    def get_object(self) -> Game:
        return Game(
            game_id=self.game_id,
            chat_id=self.chat_id,
            users=self.users,
            stocks=self.stocks,
            number_of_moves=self.number_of_moves,
        )
