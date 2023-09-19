import typing
from logging import getLogger

from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            from_id = update.object.message.from_id
            peer_id = update.object.message.peer_id
            if peer_id == from_id:
                group = False
            else:
                group = True
            await self.app.store.vk_api.send_message(
                    message=Message(
                        peer_id=peer_id,
                        user_id=from_id,
                        text="Привет",
                    ),
                    group=group
                )
