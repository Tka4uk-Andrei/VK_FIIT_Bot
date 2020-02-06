import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Global constants
VK_API_KEY = "28f2396ab6b6ca0d2cbc63caec4561b3b3005aeab6d89f0432578344fe0b181409b77e043302013be1655"
VK_VERSION = "5.103"
VK_GROUP_ID = "club191500224"

SUBSCRIPTION_ID_FILE_NAME = "data/subscribedIds.txt"

print ('Launching...')

vkSession = vk_api.VkApi(token=VK_API_KEY)
sessionApi = vkSession.get_api()
longpoll = VkBotLongPoll(vkSession, 191500224, 100)

connectedIds = []
# read added early ids from file
with open(SUBSCRIPTION_ID_FILE_NAME, "r") as subscribedIds:
    for line in subscribedIds:
        connectedIds.append(int(line))


print ('Server started listening')
for event in longpoll.listen():
    print ('Event handling start...')
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_user:
            # receive users id
            fromId = event.obj.message[u'from_id']
            print ('message from user with id ' + str(event.obj.message[u'from_id']) + ' received')

            # if from_id is new, we'll add it to special list, then write updated info to file
            if not (fromId in connectedIds):
                print('new user connected / record added')
                connectedIds.append(fromId)
                with open(SUBSCRIPTION_ID_FILE_NAME, "w") as subscribedIds:
                    for userId in connectedIds:
                        subscribedIds.write(str(userId))

            # sessionApi.message.send()

        elif event.from_chat:
            print ('message from chat')
            # vk.messages.send(
            #     chat_id=event.chat_id,
            #     message='Hello chat and world'
            # )
    print ('Event handling ended')

print ('The End')
