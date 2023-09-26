info = {'ts': '329', 'updates': [{'group_id': 222363225, 'type': 'message_new', 'event_id': 'c5c49f0e085dfe58f4404c5c6429465a1969b8f6', 'v': '5.131', 'object': {'message': {'date': 1695673885, 'from_id': 51383207, 'id': 0, 'out': 0, 'attachments': [], 'conversation_message_id': 97, 'fwd_messages': [], 'important': False, 'is_hidden': False, 'peer_id': 2000000001, 'random_id': 0, 'text': 'дай ответ'}, 'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback', 'intent_subscribe', 'intent_unsubscribe'], 'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}}}]}
x = info['updates']
y = x[0]
z = y['object']
xyz = z['message']
print(xyz["from_id"])