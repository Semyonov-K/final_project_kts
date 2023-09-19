import random
import typing
from typing import Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(app.store)
        self.logger.info("start polling")
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as response:
            response_body = await response.json()
            data = response_body["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(response_body)

    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=self.server,
                method="",
                params={
                    "act": "a_check",
                    "key": self.key,
                    "wait": 30,
                    "mode": 2,
                    "ts": self.ts,
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)
            self.ts = data["ts"]
        
        return [
            Update(
                type=u['type'],
                object=UpdateObject(
                    message=UpdateMessage(
                        peer_id=u['object']['message']['peer_id'],
                        from_id=u['object']['message']['from_id'],
                        text=u['object']['message']['text'],
                        id=u['object']['message']['id']))) for u in data["updates"] if u['type'] == 'message_new'
        ]
            # raw_updates = data.get("updates", [])
            # updates = []
            # for update in raw_updates:
            #     updates.append(
            #         Update(
            #             type=update["type"],
            #             object=UpdateObject(
            #                 id=update["object"]["id"],
            #                 user_id=update["object"]["user_id"],
            #                 body=update["object"]["body"],
            #             ),
            #         )
            #     )
            # await self.app.store.bots_manager.handle_updates(updates)

    async def send_message(self, group: bool, message: Message) -> None:
        params = {
                "random_id": random.randint(1, 2**32),
                "message": message.text,
                "access_token": self.app.config.bot.token,
            }
        if group is False:
            params["user_id"] = message.user_id
        else:
            params["peer_id"] = message.peer_id

        query = self._build_query(
                host=API_PATH,
                method="messages.send",
                params=params,
            )
        async with self.session.get(query) as response:
            data = await response.json()
            self.logger.info(data)
