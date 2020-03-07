import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config.json_configuration_loader


class AdvancedStrategy:

    def __init__(self, session_api, logger, configuration):
        self.__api = session_api
        self.__logger = logger
        self.__configuration = configuration
        self.__usrs_statuses = dict()
        self.__DEFAULT_CHAT_ADD = '2000000002'

    def handle_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_user:
                self.__handle_msg_from_user(event)
            elif event.from_chat and event.message.text != '' and event.message.text[0:2] == '//':
                self.__handle_msg_from_chat(event)
        self.__logger.info('Event handled')

    def __handle_msg_from_user(self, event):
        from_id = event.obj.message[u'from_id']
        # add user_id if not in subscriptions list
        subscriptions_list = self.__configuration.get_chat_description(
            event.message[self.__DEFAULT_CHAT_ADD])
        if from_id not in subscriptions_list.get_subscribers():
            subscriptions_list.add_subscriber(from_id)
            self.__logger.info(
                f'User with id {event.obj.message["from_id"]} saved in {self.__DEFAULT_CHAT_ADD} group')

        # mark message as read
        self.__session_api.messages.markAsRead(
            start_message_id=[event.message['id']],
            peer_id=event.message['peer_id'],
        )
        self.__logger.info(
            f'message from user with id {event.obj.message["from_id"]} marked as read')

    def __handle_msg_from_chat(self, event):
        self.__logger.info('Recieved message from chat')
        self.__logger.info(f'Message is <<{event.message.text}>>')

        # notify subscribed users
        # forward messages not supported by VK API for bots??? W H A T !? :\
        self.__api.messages.send(
            user_ids=self.__configuration.get_chat_description(
                str(event.message.peer_id)).get_subscribers(),
            random_id=0,
            message=event.message.text,
            attachment=self.__reform_attachments(
                event.message.attachments),
        )

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
