from typing import Optional
from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.store.bot.models import ChatModel, Chat


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
                chat.start_game = new_chat.start_game
                chat.pregame = new_chat.pregame
                chat.timer = new_chat.timer
                chat.game = new_chat.game
                await session.commit()
                return chat.get_object()
            else:
                return None
