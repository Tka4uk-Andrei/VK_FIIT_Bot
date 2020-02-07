import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Global constants
VK_API_KEY = "28f2396ab6b6ca0d2cbc63caec4561b3b3005aeab6d89f0432578344fe0b181409b77e043302013be1655"
VK_VERSION = "5.103"
VK_GROUP_ID = "club191500224"

# Path to data files
SUBSCRIPTION_ID_FILE_NAME = "data/subscribedIds.txt"
LATEST_MSG_ID_FILE_NAME = "data/latest_msg_id.txt"

print ('Launching...')

vkSession = vk_api.VkApi(token=VK_API_KEY)
sessionApi = vkSession.get_api()
longpoll = VkBotLongPoll(vkSession, 191500224, 100)

connectedIds = []
# read added early ids from file
with open(SUBSCRIPTION_ID_FILE_NAME, "r") as subscribedIds:
    for line in subscribedIds:
        connectedIds.append(int(line))

messageCounter = 0
# read message id from where you should start
with open(LATEST_MSG_ID_FILE_NAME, "r") as msgId:
    for line in msgId:
        messageCounter = int(line)

print ('Server started listening')
for event in longpoll.listen():
    print ('Event handling start...')
    if event.type == VkBotEventType.MESSAGE_NEW:
        # handle message from subscribed user
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

            # mark message as read
            sessionApi.messages.markAsRead(start_message_id=[event.message[u'id']], peer_id=event.message[u'peer_id'])

        # handle message from
        elif event.from_chat:
            print ('message from chat')
            # notify subscribed users
            for userId in connectedIds:
                sessionApi.messages.send(peer_id=userId, random_id=messageCounter, message='Check conference')
                

    print ('Event handling ended')

print ('The End')
