from sqlalchemy.orm import relationship
from dataclasses import dataclass
from typing import Optional
from app.store.database.sqlalchemy_base import db
from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship



class UserModel(db):
    __tablename__ = 'user'

    vk_id = Column(Integer, primary_key=True)
    score = Column(Integer)
    stock_one = Column(Integer, default=0)
    stock_two = Column(Integer, default=0)
    stock_three = Column(Integer, default=0)
    question_id = Column(BigInteger, ForeignKey("game.game_id", ondelete="CASCADE"))


class GameModel(db):
    __tablename__ = "game"

    game_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    users = relationship("UserModel", backref="aya")    
    number_of_moves = Column(Integer, default=10)


user1 = UserModel(vk_id=124151515, score=50, stock_one=2, stock_two=4, stock_three=6)
user2 = UserModel(score=60, stock_one=1, stock_two=3, stock_three=5)

# Создание экземпляра GameModel
game = GameModel(chat_id=123, number_of_moves=10)

# Добавление пользователей в список пользователей игры
game.users.append(user1)
game.users.append(user2)

print(game.users[0].vk_id)
