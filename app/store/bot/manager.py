import typing
import asyncio
import time
import threading
from typing import Optional
from logging import getLogger

from app.store.vk_api.dataclasses import Message, Update
from app.store.stock_exchange.accessor import StockExchangeAccessor as SEA
from app.bot.text import RULES_OF_GAME, START_GAME
from app.store.vk_api.keyboard import SHOWBAR_SELL_THREE, SHOWBAR_SELL_TWO, SHOWBAR_SELL_ONE, SHOWBAR_BUY_THREE, SHOWBAR_BUY_TWO, SHOWBAR_BUY_ONE, BUTTON, BUTTON_IN_GAME, BUTTON_PREGAME, SHOWBAR_INPLAY, SHOWBAR_ALREADY_ADD, SHOWBAR_SKIPPED, HIDDEN_KEYBOARD, BUTTON_IN_GAME_WITH_STOCKS, BUTTON_INLINE_IN_GAME, SHOWBAR_NOINGAME, SHOWBAR_NOBUY, SHOWBAR_NOSELL, SHOWBAR_COUNT_STOCK

from app.store.vk_api.dataclasses import UpdateEvent
from app.store.bot.accessor import ChatModelAccessor as CMA
from app.bot.models import Chat
from app.stock_exchange.models import Game, User
from app.stock_exchange.st_exc_logic import calculate_price_change

if typing.TYPE_CHECKING:
    from app.web.app import Application

# BIG TIMER и GAME ДОЛЖНЫ ОТЛИЧАТЬСЯ!
TIME_OF_BIG_TIMER = 10
TIME_OF_GAME = 5
in_memory_for_skipped = {}


class BotManager:
    """Класс, отвечающий за обработку сообщений и ход игры."""
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")

    async def handler_group(self, updates: list[Update]):
        """Принимает все входящие события, получает или
        создаёт модель чата с замками, регулирующими ход игры.
        """
        for update in updates:
            if isinstance(update, UpdateEvent):
                peer_id = update.event_object.event_message.peer_id
            if isinstance(update, Update):
                peer_id = update.object.message.peer_id
            chat = await CMA.get_chat_by_chat_id(self, chat_id=peer_id)
            if chat:
                await self.handler_lock(chat=chat, updates=updates)
            if chat is None:
                new_chat = await CMA.create_chat(self, chat_id=peer_id)
                await self.handler_lock(chat=new_chat, updates=updates)

    async def handler_lock(self, chat: Chat, updates: list[Update]):
        """Обработчик замков. Регулирует ход игры."""
        await self.start_menu(chat, updates)
        if chat.timer == "round":
            await self.update_stock_exchange(chat=chat, updates=updates)

    async def start_timer(self, chat: Chat, timer: int, updates: list[Update]):
        """Таймер."""
        if timer == TIME_OF_GAME:
            chat.timer = "round"
            await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
        real_timer = timer
        for _ in range(real_timer):
            real_timer -= 1
            await asyncio.sleep(1)
            game = await SEA.get_game(self, chat_id=chat.chat_id)
            if game is None:
                continue
            if game.game_id not in in_memory_for_skipped:
                in_memory_for_skipped[game.game_id] = []
            if len(game.users) == len(in_memory_for_skipped[game.game_id]):
                await self.handler_round(chat=chat, updates=updates)
                real_timer = 0
        if timer == TIME_OF_GAME:
            chat = await CMA.get_chat_by_chat_id(self, chat_id=chat.chat_id)
            if chat.early_timer_ > 0 or chat.endgame is True:
                chat.early_timer_ -= 1
                await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
                return
            chat.timer = "roundend"
            await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
            await self.handler_round(chat=chat, updates=updates)
        if timer == TIME_OF_BIG_TIMER:
            chat.game = True
            chat.pregame = False
            await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
            text_msg = "Подготовка к игре"
            await self.sendler(chat.chat_id, chat.chat_id, text_msg, BUTTON_IN_GAME_WITH_STOCKS)
            await self.stock_exchange(chat=chat, updates=updates)

    async def sendler(self, peer_id: int, from_id: int, text: str, keyboard: Optional[str]):
        """Корутина, отправляющая сообщения."""
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
        """Основное меню, обрабатывает все действия, которые связаны
        с конкретным игроком. Также запускает игру.
        """
        for update in updates:
            if isinstance(update, UpdateEvent):
                payload = update.event_object.event_message.payload
                peer_id = update.event_object.event_message.peer_id
                user_id = update.event_object.event_message.user_id
                event_id = update.event_object.event_message.event_id
                user = await SEA.get_user_by_vk_id(self, vk_id=user_id)
                if payload["command"] == "iplay":
                    game = await SEA.get_game(self, chat_id=chat.chat_id)
                    if game is None:
                        game = await SEA.create_game(
                            self,
                            chat_id=chat.chat_id
                        )
                        for stock_id in range(1, 4):
                            stock = await SEA.get_stock(self, stock_id)
                            new_stock = await SEA.create_stock(self, name=stock.name, price=stock.price)
                            await SEA.update_game(self, chat_id=chat.chat_id, stock=new_stock, user=None, number_of_moves=None)
                    lst_user = []
                    for suser in game.users:
                        lst_user.append(suser.vk_id)
                    if user_id in lst_user:
                            await self.app.store.vk_api.send_event_message(
                                event_id=event_id,
                                peer_id=peer_id,
                                user_id=user_id,
                                event_data=SHOWBAR_ALREADY_ADD
                            )
                    else:
                        if user is None:
                            user = await SEA.create_user(self, vk_id=user_id)
                        await SEA.update_game(self, chat_id=game.chat_id, user=user, stock=None, number_of_moves=None)
                        await self.app.store.vk_api.send_event_message(
                            event_id=event_id,
                            peer_id=peer_id,
                            user_id=user_id,
                            event_data=SHOWBAR_INPLAY
                        )
                if payload["command"] == "stock_one":
                    if user is None:
                        continue
                    SHOWBAR_STOCK = SHOWBAR_COUNT_STOCK.replace("У вас 0 акции!", f"У вас {user.stock_one} акции")
                    await self.app.store.vk_api.send_event_message(
                                event_id=event_id,
                                peer_id=peer_id,
                                user_id=user_id,
                                event_data=SHOWBAR_STOCK
                            )
                if payload["command"] == "stock_two":
                    if user is None:
                        continue
                    SHOWBAR_STOCK = SHOWBAR_COUNT_STOCK.replace("У вас 0 акции!", f"У вас {user.stock_two} акции")
                    await self.app.store.vk_api.send_event_message(
                                event_id=event_id,
                                peer_id=peer_id,
                                user_id=user_id,
                                event_data=SHOWBAR_STOCK
                            )
                if payload["command"] == "stock_three":
                    if user is None:
                        continue
                    SHOWBAR_STOCK = SHOWBAR_COUNT_STOCK.replace("У вас 0 акции!", f"У вас {user.stock_three} акции")
                    await self.app.store.vk_api.send_event_message(
                                event_id=event_id,
                                peer_id=peer_id,
                                user_id=user_id,
                                event_data=SHOWBAR_STOCK
                            )
                if payload["command"] == "my_score":
                    if user is None:
                        continue
                    SHOWBAR_STOCK = SHOWBAR_COUNT_STOCK.replace("У вас 0 акции!", f"Ваш счёт {user.score}")
                    await self.app.store.vk_api.send_event_message(
                                event_id=event_id,
                                peer_id=peer_id,
                                user_id=user_id,
                                event_data=SHOWBAR_STOCK
                            )
                if payload["command"] == "endgame":
                    if user is None:
                        continue
                    game = await SEA.get_game(self, chat_id=chat.chat_id)
                    if game is None:
                        continue
                    for del_user in game.users:
                        await SEA.delete_user(self, del_user.vk_id)
                    for del_stock in game.stocks:
                        await SEA.delete_stock(self, del_stock.stock_id)
                    await SEA.delete_game(self, chat_id=chat.chat_id)
                    chat.endgame = False
                    chat.game = False
                    chat.pregame= False
                    chat.timer = "None"
                    chat.early_timer_ = 0
                    await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
                    text_msg=f"Игра закончена по просьбе @{user_id}"
                    keyboard = BUTTON
                    await self.sendler(chat.chat_id, chat.chat_id, text_msg, keyboard)
                continue

            text = update.object.message.text
            from_id = update.object.message.from_id
            peer_id = update.object.message.peer_id

            if text == "Старт бота":
                if chat.start_bot is False:
                    chat.start_bot = True
                    await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
                    text_msg="Здравствуйте, давайте поиграем?"
                    keyboard = BUTTON
                    await self.sendler(peer_id, peer_id, text_msg, keyboard)

            if text == "[club222363225|@club222363225] Правила игры":
                text_msg=RULES_OF_GAME
                keyboard = BUTTON
                if chat.game is True:
                    keyboard = BUTTON_IN_GAME_WITH_STOCKS
                if chat.pregame is True:
                    keyboard = BUTTON_PREGAME
                await self.sendler(peer_id, from_id, text_msg, keyboard)

            if text == '[club222363225|@club222363225] Моя статистика':
                stats = await SEA.get_gamescore_user_by_vk_id(self, vk_id=from_id)
                if stats:
                    text_msg=f"""Ваш ID: {stats.vk_id}
                    Всего очков: {stats.total_score}
                    Всего игр: {stats.total_games}
                    Всего побед: {stats.total_win}
                    """
                keyboard = BUTTON
                if chat.game is True:
                    keyboard = BUTTON_IN_GAME_WITH_STOCKS
                if chat.pregame is True:
                    keyboard = BUTTON_PREGAME
                if stats is None:
                    text_msg="У вас пока нет статистики :("
                await self.sendler(peer_id, from_id, text_msg, keyboard)

            if text == "[club222363225|@club222363225] Старт игры!":
                chat.pregame = True
                await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
                text_msg=START_GAME
                await self.sendler(chat.chat_id, chat.chat_id, text_msg, BUTTON_PREGAME)
                asyncio.create_task(self.start_timer(chat=chat, timer=TIME_OF_BIG_TIMER, updates=updates))

    async def prefinal_message(self, chat: Chat, text_msg: str, bad: Optional[bool]=False):
        """Корутина, которая отвечает за досрочное завершение игры. Также
        отправляет сообщение сообщение об завершении.
        """
        if bad is True:
            await SEA.delete_game(self, chat_id=chat.chat_id)
        await self.sendler(
                peer_id=chat.chat_id,
                from_id=chat.chat_id,
                text=text_msg,
                keyboard=BUTTON
        )
        chat.start_bot = False
        chat.pregame = False
        chat.timer = "None"
        chat.game = False
        if bad is True:
            chat.early_timer_ = 0
        await CMA.update_chat_in_db(
            self,
            chat_id=chat.chat_id,
            new_chat=chat
        )

    async def stock_exchange(self, chat: Chat, updates: list[Update]):
        """Старт каждого раунда игры."""
        game = await SEA.get_game(self, chat_id=chat.chat_id)
        if game is None:
            text_msg = "Что-то пошло не так :("
            await self.prefinal_message(chat=chat, text_msg=text_msg, bad=True)
            return
        # if len(game.users) < 2 and game.number_of_moves == 1:
        #     text_msg = "К сожалению, игра не состоится. Недостаточное количество игроков (минимум: 2)"
        #     await self.prefinal_message(chat=chat, text_msg=text_msg, bad=True)
        #     return
        # if len(game.users) < 2:
        #     text_msg = "В игре есть абсолютный победитель!"
        #     await self.prefinal_message(chat=chat, text_msg=text_msg, bad=False)
        #     chat.endgame = True
        #     await self.endgame(chat=chat, updates=updates)
        #     return
        if game.number_of_moves > 5:
            text_msg = "Последняя сессия сыграна. Определяем победителя."
            await self.prefinal_message(chat=chat, text_msg=text_msg, bad=False)
            chat.endgame = True
            await self.endgame(chat=chat, updates=updates)
            return
        if game.number_of_moves == 1:
            text_msg = "Игра началась!"
            await self.sendler(
                peer_id=chat.chat_id,
                from_id=chat.chat_id,
                text=text_msg,
                keyboard=BUTTON_IN_GAME_WITH_STOCKS
            )
        text_msg = f"""Сессия {game.number_of_moves} из 10. 
        Акция 1: {game.stocks[0].name}, цена: {game.stocks[0].price}.
        Акция 2: {game.stocks[1].name}, цена: {game.stocks[1].price}.
        Акция 3: {game.stocks[2].name}, цена: {game.stocks[2].price}.
        Время на ход: {TIME_OF_GAME} секунд."""
        BUTTON_PROCESS = BUTTON_INLINE_IN_GAME
        BUTTON_PROCESS = BUTTON_PROCESS.replace("Купить 1", f"Купить {game.stocks[0].name}")
        BUTTON_PROCESS = BUTTON_PROCESS.replace("Купить 2", f"Купить {game.stocks[1].name}")
        BUTTON_PROCESS = BUTTON_PROCESS.replace("Купить 3", f"Купить {game.stocks[2].name}")
        BUTTON_PROCESS = BUTTON_PROCESS.replace("Продать 1", f"Продать {game.stocks[0].name}")
        BUTTON_PROCESS = BUTTON_PROCESS.replace("Продать 2", f"Продать {game.stocks[1].name}")
        BUTTON_PROCESS = BUTTON_PROCESS.replace("Продать 3", f"Продать {game.stocks[2].name}")
        await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
        await self.sendler(
            peer_id=chat.chat_id,
            from_id=chat.chat_id,
            text=text_msg,
            keyboard=BUTTON_PROCESS)
        asyncio.create_task(self.start_timer(chat=chat, timer=TIME_OF_GAME, updates=updates))

    async def check_user(self, game: Game, user_id: int, event_id: int, peer_id: int, event_data: str):
        """Проверка, что игрок находится в списке игроков"""
        user_exists = any(user.vk_id == user_id for user in game.users)
        if user_exists is False:
            await self.app.store.vk_api.send_event_message(
                event_id=event_id,
                peer_id=peer_id,
                user_id=user_id,
                event_data=event_data
            )
            return False

    async def check_buy(self, game: Game, stock_number: int, vk_id: int, event_id: int, peer_id: int):
        """Проверка, что игрок может купить акцию."""
        stock = game.stocks[stock_number].price
        user = await SEA.get_user_by_vk_id(self, vk_id=vk_id)
        result_buy = user.score - stock
        if result_buy >= 0:
            if stock_number == 0:
                stock_one=user.stock_one + 1
                stock_one_buy=user.stock_one_buy + 1
                await SEA.update_user(
                    self,
                    vk_id=vk_id,
                    score=result_buy,
                    stock_one=stock_one,
                    stock_one_buy=stock_one_buy
                )
                if result_buy == 0:
                    await SEA.set_null_stock(self, vk_id, score=True)
            if stock_number == 1:
                stock_two=user.stock_two + 1
                stock_two_buy=user.stock_two_buy + 1
                await SEA.update_user(
                    self,
                    vk_id=vk_id,
                    score=result_buy,
                    stock_two=stock_two,
                    stock_two_buy=stock_two_buy
                )
                if result_buy == 0:
                    await SEA.set_null_stock(self, vk_id, score=True)
            if stock_number == 2:
                stock_three=user.stock_three + 1
                stock_three_buy=user.stock_three_buy + 1
                await SEA.update_user(
                    self,
                    vk_id=vk_id,
                    score=result_buy,
                    stock_three=stock_three,
                    stock_three_buy=stock_three_buy
                )
                if result_buy == 0:
                    await SEA.set_null_stock(self, vk_id, score=True)
        else:
            await self.app.store.vk_api.send_event_message(
                event_id=event_id,
                peer_id=peer_id,
                user_id=vk_id,
                event_data=SHOWBAR_NOBUY
            )

    async def check_sell(self, game: Game, stock_number: int, vk_id: int, event_id: int, peer_id: int):
        """Проверка, что игрок может продать акцию."""
        stock = game.stocks[stock_number].price
        user = await SEA.get_user_by_vk_id(self, vk_id=vk_id)
        if stock_number == 0:
            check_stock = user.stock_one
            if check_stock > 0:
                new_score = user.score + stock
                all_stock_one = check_stock - 1
                if all_stock_one == 0:
                    await SEA.set_null_stock(self, vk_id, stock_one=True)
                new_stock_sell_one = user.stock_one_sell + 1
                await SEA.update_user(self, vk_id, score=new_score, stock_one=int(all_stock_one), stock_one_sell=new_stock_sell_one)
                user = await SEA.get_user_by_vk_id(self, vk_id=vk_id)        
        user = await SEA.get_user_by_vk_id(self, vk_id=vk_id)
        if stock_number == 1:
            check_stock = user.stock_two
            if check_stock > 0:
                new_score = user.score + stock
                all_stock_two = check_stock - 1
                if all_stock_two == 0:
                    await SEA.set_null_stock(self, vk_id, stock_two=True)
                new_stock_sell_two = user.stock_two_sell + 1
                await SEA.update_user(self, vk_id, score=new_score, stock_two=all_stock_two, stock_two_sell=new_stock_sell_two)
        if stock_number == 2:
            check_stock = user.stock_three
            if check_stock > 0:
                new_score = user.score + stock
                all_stock_three = check_stock - 1
                if all_stock_three == 0:
                    await SEA.set_null_stock(self, vk_id, stock_three=True)
                new_stock_sell_three = user.stock_three_sell + 1
                await SEA.update_user(self, vk_id, score=new_score, stock_three=all_stock_three, stock_three_sell=new_stock_sell_three)
        if check_stock == 0:
            await self.app.store.vk_api.send_event_message(
                event_id=event_id,
                peer_id=peer_id,
                user_id=vk_id,
                event_data=SHOWBAR_NOSELL
            )

    async def update_stock_exchange(self, chat: Chat, updates:list[Update]):
        """Обработка кнопок в ходе игры."""
        for update in updates:
            game = await SEA.get_game(self, chat_id=chat.chat_id)
            if isinstance(update, UpdateEvent):
                payload = update.event_object.event_message.payload
                peer_id = update.event_object.event_message.peer_id
                user_id = update.event_object.event_message.user_id
                event_id = update.event_object.event_message.event_id

                if payload["command"] == "buy_one":
                    user_exists = await self.check_user(game, user_id, event_id, peer_id, SHOWBAR_NOINGAME)
                    if user_exists is False:
                        continue
                    await self.check_buy(game, 0, user_id, event_id, peer_id)
                    await self.app.store.vk_api.send_event_message(
                        event_id=event_id,
                        peer_id=peer_id,
                        user_id=user_id,
                        event_data=SHOWBAR_BUY_ONE
                    )
                    continue

                if payload["command"] == "buy_two":
                    user_exists = await self.check_user(game, user_id, event_id, peer_id, SHOWBAR_NOINGAME)
                    if user_exists is False:
                        continue
                    await self.check_buy(game, 1, user_id, event_id, peer_id)
                    await self.app.store.vk_api.send_event_message(
                        event_id=event_id,
                        peer_id=peer_id,
                        user_id=user_id,
                        event_data=SHOWBAR_BUY_TWO
                    )
                    continue

                if payload["command"] == "buy_three":
                    user_exists = await self.check_user(game, user_id, event_id, peer_id, SHOWBAR_NOINGAME)
                    if user_exists is False:
                        continue
                    await self.check_buy(game, 2, user_id, event_id, peer_id)
                    await self.app.store.vk_api.send_event_message(
                        event_id=event_id,
                        peer_id=peer_id,
                        user_id=user_id,
                        event_data=SHOWBAR_BUY_THREE
                    )
                    continue

                if payload["command"] == "sell_one":
                    user_exists = await self.check_user(game, user_id, event_id, peer_id, SHOWBAR_NOINGAME)
                    if user_exists is False:
                        continue
                    await self.check_sell(game, 0, user_id, event_id, peer_id)
                    await self.app.store.vk_api.send_event_message(
                        event_id=event_id,
                        peer_id=peer_id,
                        user_id=user_id,
                        event_data=SHOWBAR_SELL_ONE
                    )
                    continue
                    
                if payload["command"] == "sell_two":
                    user_exists = await self.check_user(game, user_id, event_id, peer_id, SHOWBAR_NOINGAME)
                    if user_exists is False:
                        continue
                    await self.check_sell(game, 1, user_id, event_id, peer_id)
                    await self.app.store.vk_api.send_event_message(
                        event_id=event_id,
                        peer_id=peer_id,
                        user_id=user_id,
                        event_data=SHOWBAR_SELL_TWO
                    )
                    continue

                if payload["command"] == "sell_three":
                    user_exists = await self.check_user(game, user_id, event_id, peer_id, SHOWBAR_NOINGAME)
                    if user_exists is False:
                        continue
                    await self.check_sell(game, 2, user_id, event_id, peer_id)
                    await self.app.store.vk_api.send_event_message(
                        event_id=event_id,
                        peer_id=peer_id,
                        user_id=user_id,
                        event_data=SHOWBAR_SELL_THREE
                    )
                    continue

                if payload["command"] == "skipped" or payload["command"] == "iamready":
                    user_exists = await self.check_user(game, user_id, event_id, peer_id, SHOWBAR_NOINGAME)
                    if user_exists is False:
                        continue
                    if user_id not in in_memory_for_skipped[game.game_id]:
                        in_memory_for_skipped[game.game_id].append(user_id)
                        await self.app.store.vk_api.send_event_message(
                            event_id=event_id,
                            peer_id=peer_id,
                            user_id=user_id,
                            event_data=SHOWBAR_SKIPPED
                        )

    async def handler_round(self, chat: Chat, updates: list[Update]):
        """Обработчик итогов. Производит подсчет и формирует новые цены."""
        game = await SEA.get_game(self, chat_id=chat.chat_id)
        if game is None:
            return
        if len(game.users) == len(in_memory_for_skipped[game.game_id]):
            in_memory_for_skipped.clear()
            chat.timer = "roundend"
            chat.early_timer_ += 1
            await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
            text_msg = "Все игроки проголосовали за конец сессии! Идет завершение сессии."
            await self.sendler(chat.chat_id, chat.chat_id, text_msg, BUTTON_IN_GAME_WITH_STOCKS)
        nom = game.number_of_moves + 1
        transactions_stock_one = 0
        transactions_stock_two = 0
        transactions_stock_three = 0
        for user in game.users:
            transactions_stock_one += user.stock_one_buy
            transactions_stock_one -= user.stock_one_sell
            transactions_stock_two += user.stock_two_buy
            transactions_stock_two -= user.stock_two_sell
            transactions_stock_three += user.stock_three_buy
            transactions_stock_three -= user.stock_three_sell
            await SEA.update_user(
                self,
                vk_id=user.vk_id,
                stock_one_buy=0,
                stock_one_sell=0,
                stock_two_buy=0,
                stock_two_sell=0,
                stock_three_buy=0,
                stock_three_sell=0
            )

        new_price_one = game.stocks[0].price + transactions_stock_one * 0.01
        minran = -25 + transactions_stock_one
        maxran = 25 + transactions_stock_one
        done_new_price_one = await calculate_price_change(new_price_one, minran, maxran)
        await SEA.update_stock(self, game.stocks[0].stock_id, done_new_price_one)
        new_price_two = game.stocks[1].price + transactions_stock_two * 0.01
        minran = -25 + transactions_stock_two
        maxran = 25 + transactions_stock_two
        done_new_price_two = await calculate_price_change(new_price_two, minran, maxran)
        await SEA.update_stock(self, game.stocks[1].stock_id, done_new_price_two)
        new_price_three = game.stocks[2].price + transactions_stock_three * 0.01
        minran = -25 + transactions_stock_two
        maxran = 25 + transactions_stock_three
        done_new_price_three = await calculate_price_change(new_price_three, minran, maxran)
        await SEA.update_stock(self, game.stocks[2].stock_id, done_new_price_three)
        await SEA.update_game(self, chat_id=chat.chat_id, number_of_moves=nom, user=None, stock=None)
        chat.timer = "None"
        text_msg = "Обработка результатов!"
        await self.sendler(chat.chat_id, chat.chat_id, text_msg, BUTTON_IN_GAME_WITH_STOCKS)
        await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
        await asyncio.sleep(3)
        await self.stock_exchange(chat=chat, updates=updates)

    async def endgame(self, chat: Chat, updates: list[Update]):
        """Корутина, отвечающая за конец игры. Подводит статистику,
        удаляет законченную игру."""
        await asyncio.sleep(5)
        game = await SEA.get_game(self, chat_id=chat.chat_id)
        win_score = 0
        win_user = 0
        for user in game.users:
            if user.score > win_score:
                win_score = user.score
                win_user = user.vk_id
        text_msg = f"У нас есть победитель! Поздравляем @{win_user}"
        await self.sendler(
                peer_id=chat.chat_id,
                from_id=chat.chat_id,
                text=text_msg,
                keyboard=BUTTON_IN_GAME
        )
        for user in game.users:
            gamescore = await SEA.get_gamescore_user_by_vk_id(self, user.vk_id)
            if gamescore is None:
                gamescore = await SEA.create_gamescore_user_by_vk_id(self, user.vk_id)
            fin_user = await SEA.get_user_by_vk_id(self, user.vk_id)
            new_total_score = gamescore.total_score + fin_user.score
            new_total_games = gamescore.total_games + 1
            new_total_win = gamescore.total_win
            if user.vk_id == win_user:
                new_total_win = gamescore.total_win + 1
            await SEA.update_gamescore(
                self,
                vk_id=user.vk_id,
                total_score=new_total_score,
                total_games=new_total_games,
                total_win=new_total_win
            )
        text_msg = f"Мы обновили статистику! Вы можете ее просмотреть."
        await self.sendler(
                peer_id=chat.chat_id,
                from_id=chat.chat_id,
                text=text_msg,
                keyboard=BUTTON_IN_GAME
        )
        text_msg = f"Завершаю игру."
        await self.sendler(
                peer_id=chat.chat_id,
                from_id=chat.chat_id,
                text=text_msg,
                keyboard=BUTTON
        )
        for del_user in game.users:
            await SEA.delete_user(self, del_user.vk_id)
        for del_stock in game.stocks:
            await SEA.delete_stock(self, del_stock.stock_id)
        await SEA.delete_game(self, chat_id=chat.chat_id)
        chat.start_bot = False
        chat.pregame = False
        chat.timer = 'None'
        chat.game = False
        chat.endgame = False
        await CMA.update_chat_in_db(self, chat_id=chat.chat_id, new_chat=chat)
