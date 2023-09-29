import asyncio
import time
import json
info = {'ts': '329', 'updates': [{'group_id': 222363225, 'type': 'message_new', 'event_id': 'c5c49f0e085dfe58f4404c5c6429465a1969b8f6', 'v': '5.131', 'object': {'message': {'date': 1695673885, 'from_id': 51383207, 'id': 0, 'out': 0, 'attachments': [], 'conversation_message_id': 97, 'fwd_messages': [], 'important': False, 'is_hidden': False, 'peer_id': 2000000001, 'random_id': 0, 'text': 'дай ответ'}, 'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback', 'intent_subscribe', 'intent_unsubscribe'], 'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}}}]}
x = info['updates']
y = x[0]
z = y['object']
xyz = z['message']
# print(xyz["from_id"])
#    async def send_message(self, group: bool, message: Message) -> None:
#         params = {
#                 "random_id": random.randint(1, 2**32),
#                 "message": message.text,
#                 "access_token": self.app.config.bot.token,
#                 "keyboard": {
#                     "inline": true,
#                     "buttons": [
#                                     [
#                                         {
#                                             "action": {
#                                                 "type": "text",
#                                                 "label": "Я КрОсавчег"
#                                             }, 
#                                             "color": "primary"
#                                         },
#                                         {
#                                             "action": {
#                                                 "type": "text",
#                                                 "label": "Я обычный"
#                                             },
#                                             "color": "secondary"
#                                         },
#                                         {
#                                             "action": {
#                                                 "type": "text",
#                                                 "label": "Я работаю"
#                                             },
#                                             "color": "positive"
#                                         },
#                                         {
#                                             "action": {
#                                                 "type": "text",
#                                                 "label": "Я не работаю"
#                                             },
#                                             "color": "negative"
#                                         }
#                                     ]
#                                 ]
#                 }
#         }
#         if group is False:
#             params["user_id"] = message.user_id
#         else:
#             params["peer_id"] = message.peer_id

#         query = self._build_query(
#                 host=API_PATH,
#                 method="messages.send",
#                 params=params,
#             )
#         async with self.session.get(query) as response:
#             data = await response.json()
#             self.logger.info(data)
# import asyncio
# import time

# async def timer(timer: int):
#     print('start')
#     await asyncio.sleep(timer)
#     print('done')

# async def main():
#     task_timer = asyncio.create_task(timer(5))
#     print('zapusk')
#     while task_timer.done() is False:
#         print('proverka')
#         await asyncio.sleep(1)

# if __name__ == "__main__":
#     asyncio.run(main())


# button = {
#     "action": {
#         "type": "callback",
#         "payload": json.dumps('iplay'),
#         "label": 'hello'
#     }
# }
# print(button)

# x = {'command': 'iplay'}
# print(x['command'])

x = 1
for i in range(10):
    x = i
print(x)