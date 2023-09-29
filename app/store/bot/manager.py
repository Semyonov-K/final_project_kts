import typing
import asyncio
from logging import getLogger

from app.store.vk_api.dataclasses import Message, Update
from app.store.stock_exchange.accessor import StockExchangeAccessor as sea
from app.store.bot.text import RULES_OF_GAME, START_GAME, SHOWBAR_INPLAY
from app.store.vk_api.keyboard import BUTTON, BUTTON_IN_GAME, BUTTON_PREGAME
from app.store.vk_api.dataclasses import UpdateEvent

if typing.TYPE_CHECKING:
    from app.web.app import Application


TIME_OF_BIG_TIMER = 10


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.group = None
        self.bot = None
        self.logger = getLogger("handler")
        self.start_bot = False
        self.pregame_ = False
        self.timer_ = None
        self.game_ = False
        self.list_user = []


    async def timer(self, timer: int):
        print('start timer')
        await asyncio.sleep(timer)
        self.timer_ = "done"
        print("end timer")
        group = True
        text_msg = 'Время закончилось! Идет формирование списка игроков.'
        peer_id = self.group
        from_id = peer_id
        await self.sendler(peer_id, from_id, text_msg, group, BUTTON_IN_GAME)


    async def sendler(self, peer_id: int, from_id: int, text: str, group: bool, keyboard: str):
        await self.app.store.vk_api.send_message(
                    message=Message(
                        peer_id=peer_id,
                        user_id=from_id,
                        text=text
                    ),
                    group=group,
                    keyboard=keyboard
                )
    
    async def start_menu(self, updates: list[Update]):
        if self.game_ is True:
            await self.game(updates)
        if self.timer_ == 'done':
            self.timer_ = None
            self.pregame_ = False
            self.game_ = True
            await self.game(updates)
        if self.pregame_ is True:
            await self.pregame(updates)
        for update in updates:
            if update.type == "message_event":
                continue
            text = update.object.message.text
            from_id = update.object.message.from_id
            peer_id = update.object.message.peer_id
            if peer_id == from_id:
                group = False
                text_msg="Извините, но я работаю только в беседах!"
                await self.sendler(peer_id, from_id, text_msg, group, keyboard='')
                continue
            group = True
            if text == "Старт бота":
                if self.start_bot is False:
                    text_msg="Здравствуйте, давайте поиграем?"
                    keyboard = BUTTON
                    await self.sendler(peer_id, from_id, text_msg, group, keyboard)
            if text == "[club222363225|@club222363225] Правила игры":
                text_msg=RULES_OF_GAME
                keyboard = BUTTON
                if self.start_bot is True and self.pregame_ is False:
                    keyboard = BUTTON_IN_GAME
                if self.start_bot is True and self.pregame_ is True:
                    keyboard = BUTTON_PREGAME
                
                await self.sendler(peer_id, from_id, text_msg, group, keyboard)
            if text == '[club222363225|@club222363225] Моя статистика':
                stats = await sea.get_score_user_by_vk_id(self, vk_id=from_id)
                keyboard = BUTTON
                if self.start_bot is True and self.pregame_ is False:
                    keyboard = BUTTON_IN_GAME
                if self.start_bot is True and self.pregame_ is True:
                    keyboard = BUTTON_PREGAME
                if stats is None:
                    text_msg="У вас пока нет статистики :("
                    await self.sendler(peer_id, from_id, text_msg, group, keyboard)
                else:
                    await self.sendler(peer_id, from_id, stats, group, keyboard)
            if text == "[club222363225|@club222363225] Старт игры!":
                if self.start_bot is False:
                    self.group = peer_id
                    self.start_bot = True
                    group = True
                    text_msg=START_GAME
                    await self.sendler(peer_id, from_id, text_msg, group, BUTTON_PREGAME)
                    self.pregame_ = True
                    asyncio.create_task(self.timer(TIME_OF_BIG_TIMER))


    async def pregame(self, updates: list[Update]):
        for update in updates:
            if isinstance(update, UpdateEvent):
                payload = update.event_object.event_message.payload
                peer_id = update.event_object.event_message.peer_id
                user_id = update.event_object.event_message.user_id
                event_id = update.event_object.event_message.event_id
                if payload["command"] == "iplay":
                    self.list_user.append(user_id)
                    await self.app.store.vk_api.send_event_message(
                        event_id=event_id,
                        peer_id=peer_id,
                        user_id=user_id,
                        event_data=SHOWBAR_INPLAY
                    )

    async def game(self, model_of_game, updates):
        group = True
        text_msg = 'Игра началась!'
        peer_id = self.group
        from_id = peer_id
        await self.sendler(peer_id, from_id, text_msg, group, BUTTON_IN_GAME)
        users = list(set(self.list_user))

        
