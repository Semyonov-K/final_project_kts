from dataclasses import dataclass
from typing import Optional
from app.store.database.sqlalchemy_base import db
from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship


@dataclass
class User:
    user_id: int
    vk_id: int
    first_name: str
    last_name: str


class UserModel(db):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    game_score_id = Column(Integer, ForeignKey('game_score.score_id', ondelete="CASCADE"), nullable=False)

    def get_object(self) -> User:
        return User(
            user_id=self.user_id,
            vk_id=self.vk_id,
            first_name=self.first_name,
            last_name=self.last_name
        )


@dataclass
class GameScore:
    score_id: int
    total_score: int
    total_games: int
    total_win: int
    user: User


class GameScoreModel(db):
    __tablename__ = 'game_score'

    score_id = Column(Integer, primary_key=True)
    total_score = Column(Integer, default=0)
    total_games = Column(Integer, default=0)
    total_win = Column(Integer, default=0)
    user = relationship("UserModel", backref="game_score", uselist=False)

    def get_object(self) -> GameScore:
        return GameScore(
            score_id=self.score_id,
            total_score=self.total_score,
            total_games=self.total_games,
            total_win=self.total_win,
            user=self.user.user_id # Здесь возможна ошибка?
        )


class Stock:
    stock_id: int
    name: str
    price: int


class StockModel(db):
    __tablename__ = "stock"

    stock_id = Column(Integer, primary_key=True)
    name = Column(String(20))
    price = Column(Integer, nullable=False)

    def get_object(self) -> Stock:
        return Stock(
            stock_id=self.stock_id,
            name=self.name,
            price=self.price
        )
