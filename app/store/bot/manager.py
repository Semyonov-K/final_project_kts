import typing
import asyncio
from logging import getLogger

from app.store.vk_api.dataclasses import Message, Update
from app.store.stock_exchange.accessor import StockExchangeAccessor as SEA
from app.store.bot.text import RULES_OF_GAME, START_GAME
from app.store.vk_api.keyboard import BUTTON, BUTTON_IN_GAME, BUTTON_PREGAME, SHOWBAR_INPLAY, SHOWBAR_ALREADY_ADD
from app.store.vk_api.dataclasses import UpdateEvent
from app.store.bot.accessor import ChatModelAccessor as CMA
from app.store.bot.models import Chat
from app.stock_exchange.models import Game

if typing.TYPE_CHECKING:
    from app.web.app import Application


TIME_OF_BIG_TIMER = 10


class BotManager:
    """Класс, отвечающий за обработку сообщений и ход игры.
    """
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")
    
    async def handler_group(self, updates: list[Update]):
        for update in updates:
            if isinstance(update, UpdateEvent):
                peer_id = update.event_object.event_message.peer_id
            if isinstance(update, Update):
                peer_id = update.object.message.peer_id
            chat = await CMA.get_chat_by_chat_id(chat_id=peer_id)
            if chat:
                await self.handler_lock(chat=chat, updates=updates)
            if chat is None:
                new_chat = await CMA.create_chat(chat_id=peer_id)
                await self.handler_lock(chat=new_chat, updates=updates)

    async def handler_lock(self, chat: Chat, updates: list[Update]):
        if chat.game is True:
            await self.stock_exchange(chat, updates)
        if chat.timer == 'done':
            chat.timer = None
            chat.pregame = False
            chat.game = True
            await CMA.update_chat_in_db(chat)
        if chat.pregame is True:
            game = SEA.get_game(chat_id=chat.chat_id)
            if game is None:
                game = SEA.create_game(
                    chat_id=chat.chat_id
                )
            await self.prepare_stocks(game)
            await self.prepare_players(game, updates)
        await self.start_menu(chat, updates)

    async def start_timer(self, chat: Chat, timer: int):
        await asyncio.sleep(timer)
        chat.timer = "done"
        await CMA.update_chat_in_db(chat)
        text_msg = 'Время закончилось! Идет формирование списка игроков.'
        await self.sendler(chat.chat_id, chat.chat_id, text_msg, BUTTON_IN_GAME)
        await asyncio.sleep(2)

    async def sendler(self, peer_id: int, from_id: int, text: str, keyboard: str):
        await self.app.store.vk_api.send_message(
                    peer_id=peer_id,
                    message=Message(
                        peer_id=peer_id,
                        user_id=from_id,
                        text=text
                    ),
                    keyboard=keyboard
                )
    
    async def start_menu(self, chat: Chat, updates: list[Update]):
        for update in updates:

            if update.type == "message_event":
                continue

            text = update.object.message.text
            from_id = update.object.message.from_id
            peer_id = update.object.message.peer_id

            if text == "Старт бота":
                if chat.start_game is False:
                    text_msg="Здравствуйте, давайте поиграем?"
                    keyboard = BUTTON
                    await self.sendler(peer_id, from_id, text_msg, keyboard)

            if text == "[club222363225|@club222363225] Правила игры":
                text_msg=RULES_OF_GAME
                keyboard = BUTTON
                if chat.start_game is True and chat.pregame is False:
                    keyboard = BUTTON_IN_GAME
                if chat.start_game is True and chat.pregame is True:
                    keyboard = BUTTON_PREGAME
                await self.sendler(peer_id, from_id, text_msg, keyboard)

            if text == '[club222363225|@club222363225] Моя статистика':
                stats = await SEA.get_gamescore_user_by_vk_id(self, vk_id=from_id)
                keyboard = BUTTON
                if chat.start_game is True and chat.pregame is False:
                    keyboard = BUTTON_IN_GAME
                if chat.start_game is True and chat.pregame is True:
                    keyboard = BUTTON_PREGAME
                if stats is None:
                    text_msg="У вас пока нет статистики :("
                    await self.sendler(peer_id, from_id, text_msg, keyboard)
                else:
                    await self.sendler(peer_id, from_id, stats, keyboard)

            if text == "[club222363225|@club222363225] Старт игры!":
                if chat.start_game is False:
                    chat.start_game = True
                    chat.pregame = True
                    new_chat = await CMA.update_chat_in_db(chat)
                    text_msg=START_GAME
                    await self.sendler(peer_id, from_id, text_msg, BUTTON_PREGAME)
                    await asyncio.create_task(self.start_timer(new_chat, TIME_OF_BIG_TIMER))
    
    async def prepare_stocks(self, new_game: Game):
        if len(new_game.stocks) >= 3:
            return
        for stock_id in range(3):
            stock = await SEA.get_stock(stock_id)
            new_stock = await SEA.create_stock(name=stock.name, price=stock.price)
            await SEA.update_game(chat_id=new_game.chat_id, stock=new_stock)

    async def prepare_players(self, new_game: Game, updates: list[Update]):
        for update in updates:
            if isinstance(update, UpdateEvent):
                payload = update.event_object.event_message.payload
                peer_id = update.event_object.event_message.peer_id
                user_id = update.event_object.event_message.user_id
                event_id = update.event_object.event_message.event_id
                if payload["command"] == "iplay":
                    if user_id in new_game.users:
                        await self.app.store.vk_api.send_event_message(
                            event_id=event_id,
                            peer_id=peer_id,
                            user_id=user_id,
                            event_data=SHOWBAR_ALREADY_ADD
                        )
                    else:
                        await SEA.update_game(chat_id=new_game.chat_id, user=user_id)
                        await self.app.store.vk_api.send_event_message(
                            event_id=event_id,
                            peer_id=peer_id,
                            user_id=user_id,
                            event_data=SHOWBAR_INPLAY
                        )

    async def stock_exchange(self, chat, updates):
        pass
