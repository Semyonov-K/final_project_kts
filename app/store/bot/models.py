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
    prepare_players: bool
    timer: str
    game: bool
    endgame: bool


class ChatModel(db):
    __tablename__ = 'chat'

    chat_id = Column(Integer, primary_key=True)
    start_bot = Column(Boolean, default=False)
    pregame = Column(Boolean, default=False)
    prepare_players = Column(Boolean, default=False)
    timer = Column(String, default='None')
    game = Column(Boolean, default=False)
    endgame = Column(Boolean, default=False)

    def get_object(self) -> Chat:
        return Chat(
            chat_id=self.chat_id,
            start_bot=self.start_bot,
            pregame=self.pregame,
            prepare_players=self.prepare_players,
            timer=self.timer,
            game=self.game,
            endgame=self.endgame
        )

