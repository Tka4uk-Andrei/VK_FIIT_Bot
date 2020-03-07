import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config.legacy_configuration_loader


class LegacyStrategy:

    def __init__(self, session_api, logger, legacy_config):
        self.__session_api = session_api
        self.__logger = logger
        self.__configuration = legacy_config

    def __reform_attachments(self, attachments):
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

    def __reform_forward_msg(self, forward_msgs):
        forward_msg = str()
        if forward_msgs:
            for msg in forward_msgs[:-1]:
                forward_msg = f'{msg}{msg["id"]} ,'

            forward_msg = f'{forward_msgs[-1]}{forward_msg["id"]}'

        return forward_msg

    def handle_event(self, event):

        if event.type == VkBotEventType.MESSAGE_NEW:
            # handle message from user
            if event.from_user:
                # add user_id if not in subscriptions list
                from_id = event.obj.message[u'from_id']
                self.__logger.info(
                    f'message from user with id {event.obj.message["from_id"]} recieved')
                if from_id not in self.__configuration.get_subscriber_ids():
                    self.__configuration.add_group_id(from_id)
                    self.__configuration.save_subscriber_ids()
                    self.__logger.info(
                        f'user with id {event.obj.message["from_id"]} saved')

                # mark message as read
                self.__session_api.messages.markAsRead(
                    start_message_id=[event.message['id']],
                    peer_id=event.message['peer_id'],
                )
                self.__logger.info(
                    f'message from user with id {event.obj.message["from_id"]} marked as read')

            # handle message from group chat
            elif event.from_chat and event.message.text != '' and event.message.text[0:2] == '//':
                self.__logger.info('message from chat')
                # notify subscribed users
                # for userId in :

                self.__logger.info(self.__reform_attachments(
                    event.message.attachments))
                self.__logger.info(self.__reform_forward_msg(
                    event.message.fwd_messages))

                # TODO switch 'peer_id' to broadcast list
                # forward messages not supported by VK API for bots??? W H A T !? :\
                self.__session_api.messages.send(
                    user_ids=self.__configuration.get_subscriber_ids(),
                    random_id=0,
                    message=event.message.text,
                    attachment=self.__reform_attachments(
                        event.message.attachments),
                )

                self.__logger.info('Event handling ended')
