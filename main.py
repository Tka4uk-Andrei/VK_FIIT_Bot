import logging

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Path to data files
SUBSCRIPTION_ID_FILE_NAME = "data/subscribedIds.txt"
LATEST_MSG_ID_FILE_NAME = "data/latest_msg_id.txt"
CONFIG_FILE_NAME = "data/config.txt"


def reform_attachments(attachments):
    attachment_arr = []
    if attachments:
        for attachment in attachments:
            if 'owner_id' in attachment['type'] and 'id' in attachment['type']:
                tpe = attachment['type']
                att = f'{type}{attachment[type]["owner_id"]}_{attachment[type]["id"]}'
                if 'access_key' in attachment['type']:
                    att += f'_{attachment[type]["access_key"]}'

                attachment_arr.append(att)

    return attachment_arr


def reform_forward_msg(forward_msgs):
    forward_msg = str()
    if forward_msgs:
        for msg in forward_msgs[:-1]:
            forward_msg = f'{msg}{msg["id"]} ,'

        forward_msg = f'{forward_msgs[-1]}{forward_msg["id"]}'

    return forward_msg


print ('Launching...')


def load_settings():
    with open(CONFIG_FILE_NAME, "r") as configs:
        api_key = configs.readline()[0:-1]
        group_id = configs.readline()

    vk_session = vk_api.VkApi(token=api_key)
    session_api = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id, 100)

    return session_api, longpoll


def get_subscribers():
    with open(SUBSCRIPTION_ID_FILE_NAME, "r") as user_ids:
        return [int(lne) for lne in user_ids]

def get_messages_ids():
    messageCounter = 0
    # read message id from where you should start
    with open(LATEST_MSG_ID_FILE_NAME, "r") as msg_id:
        return [int(lne) for lne in msg_id]


def main_loop(connected_ids, session_api, longpoll):
    while True:
        logging.info('Server started listening')
        try:
            for event in longpoll.listen():
                logging.info('Event handling start...')
                if event.type == VkBotEventType.MESSAGE_NEW:
                    # handle message from subscribed user
                    if event.from_user:
                        # receive users id
                        from_id = event.obj.message[u'from_id']
                        logging.info(f'message from user with id {event.obj.message["from_id"]} received')

                        # if from_id is new, we'll add it to special list, then write updated info to file
                        if from_id not in connected_ids:
                            logging.info('new user connected / record added')
                            with open(SUBSCRIPTION_ID_FILE_NAME, "a") as f:
                                f.write(f'\n{from_id}')

                        # mark message as read
                        session_api.messages.markAsRead(
                            start_message_id=[event.message['id']],
                            peer_id=event.message['peer_id'],
                        )

                    # handle message from group chat
                    elif event.from_chat and event.message.text != '' and event.message.text[0:2] == '//':
                        logging.info('message from chat')
                        # notify subscribed users
                        for userId in connected_ids:
                            # switch 'peer_id' to broadcast list
                            # forward messages not supported by VK API for bots??? W H A T !? :\
                            logging.info(reform_attachments(event.message.attachments))
                            logging.info(reform_forward_msg(event.message.fwd_messages))

                            session_api.messages.send(
                                peer_id=userId,
                                random_id=0,
                                message=event.message.text,
                                attachment=reform_attachments(event.message.attachments),
                            )

                logging.info('Event handling ended')
        except Exception as e:
            logging.exception(e)

        logging.info('Server stopped')


if __name__ == '__main__':
    logging.basicConfig(filename="server.log", level=logging.INFO)
    main_loop(get_subscribers(), load_settings())
