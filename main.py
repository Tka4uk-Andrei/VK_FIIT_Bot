import logging
from logging.handlers import RotatingFileHandler
import threading

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from config.legacy_configuration_loader import LegacyConfigurationLoader

APP_LOGGER = logging


def reform_attachments(attachments):
    attachment_arr = []
    if attachments:
        for attachment in attachments:
            if 'owner_id' in attachment['type'] and 'id' in attachment['type']:
                type = attachment['type']
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


def main_loop(configuration):
    # setup connection to VK API
    vk_session = vk_api.VkApi(token=configuration.get_api_key())
    session_api = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, configuration.get_group_id(), 100)

    APP_LOGGER.info('Server started listening')

    while True:
        try:
            for event in longpoll.listen():
                APP_LOGGER.info('Event handling start...')
                if event.type == VkBotEventType.MESSAGE_NEW:
                    # handle message from user
                    if event.from_user:

                        # add user_id if not in subscriptions list
                        from_id = event.obj.message[u'from_id']
                        APP_LOGGER.info(f'message from user with id {event.obj.message["from_id"]} recieved')
                        if from_id not in configuration.get_subscriber_ids():
                            configuration.add_group_id(from_id)
                            configuration.save_subscriber_ids()
                            APP_LOGGER.info(f'user with id {event.obj.message["from_id"]} saved')

                        # mark message as read
                        session_api.messages.markAsRead(
                            start_message_id=[event.message['id']],
                            peer_id=event.message['peer_id'],
                        )
                        APP_LOGGER.info(f'message from user with id {event.obj.message["from_id"]} marked as read')

                    # handle message from group chat
                    elif event.from_chat and event.message.text != '' and event.message.text[0:2] == '//':
                        APP_LOGGER.info('message from chat')
                        # notify subscribed users
                        for userId in configuration.get_subscriber_ids:
                            
                            APP_LOGGER.info(reform_attachments(event.message.attachments))
                            APP_LOGGER.info(reform_forward_msg(event.message.fwd_messages))
                            
                            # TODO switch 'peer_id' to broadcast list
                            # forward messages not supported by VK API for bots??? W H A T !? :\
                            session_api.messages.send(
                                peer_id=userId,
                                random_id=0,
                                message=event.message.text,
                                attachment=reform_attachments(event.message.attachments),
                            )

                APP_LOGGER.info('Event handling ended')
        except Exception as e:
            APP_LOGGER.exception(e)
            pass


def setup_logger():
    global APP_LOGGER

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

    log_file = 'server.log'

    my_handler = RotatingFileHandler(
        log_file,
        mode='a',
        maxBytes=(5 * 1024 * 1024),
        backupCount=2,
        encoding=None,
        delay=False
    )

    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)

    APP_LOGGER = logging.getLogger('root')
    APP_LOGGER.setLevel(logging.INFO)

    APP_LOGGER.addHandler(my_handler)


if __name__ == '__main__':
    setup_logger()
    # why we need thread?
    main_tread = threading.Thread(target=main_loop, args=(LegacyConfigurationLoader()))
    main_tread.start()
