from dataclasses import dataclass
from typing import Optional
from app.store.database.sqlalchemy_base import db
from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship


@dataclass
class Chat:
    chat_id: int
    start_bot: bool
    pregame: bool
    early_timer_: bool
    timer: str
    game: bool
    endgame: bool


class ChatModel(db):
    __tablename__ = 'chat'

    chat_id = Column(Integer, primary_key=True)
    start_bot = Column(Boolean, default=False)
    pregame = Column(Boolean, default=False)
    early_timer_ = Column(Integer, default=0)
    timer = Column(String, default='None')
    game = Column(Boolean, default=False)
    endgame = Column(Boolean, default=False)

    @property
    def early_timer(self):
        return self.early_timer_

    @early_timer.setter
    def early_timer(self, value):
        if value < 0:
            self.early_timer_ = 0
        else:
            self.early_timer_ = value

    def get_object(self) -> Chat:
        return Chat(
            chat_id=self.chat_id,
            start_bot=self.start_bot,
            pregame=self.pregame,
            early_timer_=self.early_timer_,
            timer=self.timer,
            game=self.game,
            endgame=self.endgame
        )

