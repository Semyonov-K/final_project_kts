from typing import Optional
from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.bot.models import ChatModel, Chat


class ChatModelAccessor(BaseAccessor):
    async def create_chat(self, chat_id: int) -> Chat:
        async with self.app.database.session() as session:
            chat = ChatModel(
                chat_id=chat_id
            )
            session.add(chat)
            await session.commit()
            return chat.get_object()

    async def get_chat_by_chat_id(self, chat_id: int) -> Optional[Chat]:
        async with self.app.database.session() as session:
            query_chat = select(ChatModel).where(ChatModel.chat_id==chat_id)
            result = await session.execute(query_chat)
            chat = result.scalars().first()
            if chat:
                return chat.get_object()
            else:
                return None

    async def update_chat_in_db(self, chat_id: int, new_chat: Chat) -> Optional[Chat]:
        async with self.app.database.session() as session:
            query_chat = select(ChatModel).where(ChatModel.chat_id==chat_id)
            result = await session.execute(query_chat)
            chat = result.scalars().first()
            if chat:
                chat.start_bot = new_chat.start_bot
                chat.pregame = new_chat.pregame
                chat.early_timer_ = new_chat.early_timer_
                chat.timer = new_chat.timer
                chat.game = new_chat.game
                chat.endgame = new_chat.endgame
                await session.commit()
                return chat.get_object()
            else:
                return None
