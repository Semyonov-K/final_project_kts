from dataclasses import dataclass
from typing import Optional
from app.store.database.sqlalchemy_base import db
from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship


@dataclass
class Chat:
    chat_id: int
    start_game: bool
    pregame: bool
    timer: str
    game: bool


class ChatModel(db):
    __tablename__ = 'chat'

    chat_id = Column(Integer, primary_key=True)
    start_game = Column(Boolean, default=False)
    pregame = Column(Boolean, default=False)
    timer = Column(String, default='None')
    game = Column(Boolean, default=False)

    def get_object(self) -> Chat:
        return Chat(
            chat_id=self.chat_id,
            start_game=self.start_game,
            pregame=self.pregame,
            timer=self.timer,
            game=self.game
        )

