import typing
import asyncio
from logging import getLogger

from app.store.vk_api.dataclasses import Message, Update
from app.store.stock_exchange.accessor import StockExchangeAccessor as sea
from app.store.bot.text import RULES_OF_GAME, START_GAME
from app.store.vk_api.keyboard import BUTTON, INLINE_BUTTON, BUTTON_IN_GAME

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")
        self.game = False

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
        for update in updates:
            text = update.object.message.text
            from_id = update.object.message.from_id
            peer_id = update.object.message.peer_id
            if peer_id == from_id:
                group = False
                text_msg="Извините, но я работаю только в беседах!"
                await self.sendler(peer_id, from_id, text_msg, group, keyboard='')
                continue
            group = True
            if text == 'Старт бота':
                if self.game is False:
                    text_msg='Здравствуйте, давайте поиграем?'
                    keyboard = BUTTON
                    await self.sendler(peer_id, from_id, text_msg, group, keyboard)
            if text == '[club222363225|@club222363225] Правила игры':
                text_msg=RULES_OF_GAME
                keyboard = BUTTON
                if self.game is True:
                    keyboard = BUTTON_IN_GAME
                await self.sendler(peer_id, from_id, text_msg, group, keyboard)
            if text == '[club222363225|@club222363225] Моя статистика':
                stats = await sea.get_score_user_by_vk_id(self, vk_id=from_id)
                keyboard = BUTTON
                if self.game is True:
                    keyboard = BUTTON_IN_GAME
                if stats is None:
                    text_msg='У вас пока нет статистики :('
                    await self.sendler(peer_id, from_id, text_msg, group, keyboard)
                else:
                    await self.sendler(peer_id, from_id, stats, group, keyboard)
            if text == '[club222363225|@club222363225] Старт игры!':
                if self.game is False:
                    self.game = True
                    text_msg=START_GAME
                    await self.sendler(peer_id, from_id, 'Подготовка игры', group, BUTTON_IN_GAME)
                    await self.sendler(peer_id, from_id, text_msg, group, INLINE_BUTTON)
                    list_users = asyncio.create_task(self.pregame(updates))
                    try:
                        # Ожидаем завершения второй корутины с таймаутом 30 секунд
                        result = await asyncio.wait_for(list_users, timeout=30)
                        # Распечатываем значение, которое вернула вторая корутина
                        print(result)
                    except asyncio.TimeoutError:
                        # В случае превышения таймаута, отменяем вторую корутину и выводим сообщение об ошибке
                        list_users.cancel()
                        print("Таймаут истек")
                    print(list_users)

    async def pregame(self, updates: list[Update]):
        count_users = 0
        list_users = []
        for update in updates:
            text = update.object.message.text
            from_id = update.object.message.from_id
            if text == '[club222363225|@club222363225] Я играю':
                count_users += 1
                list_users.append(from_id)
        return list_users
