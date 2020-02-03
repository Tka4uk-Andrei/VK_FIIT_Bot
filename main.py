import vk_api
import json
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Global constants
VK_API_KEY = "28f2396ab6b6ca0d2cbc63caec4561b3b3005aeab6d89f0432578344fe0b181409b77e043302013be1655"
VK_VERSION = "5.103"
VK_GROUP_ID = "club191500224"

print ('Launching...')

vkSession = vk_api.VkApi(token=VK_API_KEY)
sessionApi = vkSession.get_api()
longpoll = VkBotLongPoll(vkSession, 191500224)

print ('Server started listening')
for event in longpoll.listen():
    print ('1')
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_user:
            print ('message from user')
            # vk.messages.send(
            #     user_id=event.user_id,
            #     message='Hello user and world'
            # )
        elif event.from_group:
            print ('message from group')
            # vk.messages.send(
            #     chat_id=event.chat_id,
            #     message='Hello chat and world'
            # )
        elif event.from_chat:
            print ('message from chat')
            # vk.messages.send(
            #     chat_id=event.chat_id,
            #     message='Hello chat and world'
            # )
    print ('2')

print ('The End')
