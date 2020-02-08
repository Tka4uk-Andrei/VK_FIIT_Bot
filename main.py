import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Path to data files
SUBSCRIPTION_ID_FILE_NAME = "data/subscribedIds.txt"
LATEST_MSG_ID_FILE_NAME = "data/latest_msg_id.txt"
CONFIG_FILE_NAME = "data/config.txt"


def reform_attachments(attachments):
    attachment_arr = []
    if attachments.__len__() > 0:
        for attachment in attachments:
            if u'owner_id' in attachment[u'type'] and u'id' in attachment[u'type']:
                if u'access_key' in attachment[u'type']:
                    attachment_arr.append(str(attachment[u'type'] + \
                                              str(attachment[attachment[u'type']][u'owner_id']) + '_' + \
                                              str(attachment[attachment[u'type']][u'id']) + '_' + \
                                              attachment[attachment[u'type']][u'access_key']))
                else:
                    attachment_arr.append(str(attachment[u'type'] + \
                                              str(attachment[attachment[u'type']][u'owner_id']) + '_' + \
                                              str(attachment[attachment[u'type']][u'id'])))
    return attachment_arr


def reform_forward_msg(forward_msgs):
    forward_msg_str = ''
    if forward_msgs.__len__() > 0:
        for i in range(forward_msgs.__len__() - 1):
            # for attachment in attachments:
            forward_msg = forward_msgs[i]
            forward_msg_str = forward_msg_str + str(forward_msg[u'id']) + ','

        forward_msg = forward_msgs[forward_msgs.__len__() - 1]
        forward_msg_str = forward_msg_str + str(forward_msg[u'id'])

    return forward_msg_str


print ('Launching...')

# Read global constants
with open(CONFIG_FILE_NAME, "r") as configs:
    VK_API_KEY = configs.readline()[0:-1]
    VK_VERSION = configs.readline()[0:-1]
    VK_GROUP_ID = configs.readline()

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

while True:
    print ('Server started listening')
    try:
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
                                subscribedIds.write(str(userId) + '\n')

                    # mark message as read
                    sessionApi.messages.markAsRead(start_message_id=[event.message[u'id']],
                                                   peer_id=event.message[u'peer_id'])

                # handle message from group chat
                elif event.from_chat and event.message.text != '' and event.message.text[0:2] == '//':
                    print ('message from chat')
                    # notify subscribed users
                    for userId in connectedIds:
                        # switch 'peer_id' to broadcast list
                        # forward messages not supported by VK API for bots??? W H A T !? :\
                        print(reform_attachments(event.message.attachments))
                        print(reform_forward_msg(event.message.fwd_messages))
                        sessionApi.messages.send(peer_id=userId,
                                                 random_id=0,
                                                 message=event.message.text,
                                                 attachment=reform_attachments(event.message.attachments))
            #                   ,
            #                                                forward_messages=reform_forward_msg(event.message.fwd_messages))

            print ('Event handling ended')
    except Exception as e:
        print (e)
        pass
    print ('The End')
