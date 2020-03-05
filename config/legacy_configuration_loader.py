import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

class LegacyConfigurationLoader:

    def __init__(self):
        # Paths to configuration files
        self.__SUBSCRIPTION_ID_FILE_NAME = "data/subscribed_ids.txt"
        self.__LATEST_MSG_ID_FILE_NAME = "data/latest_msg_id.txt"
        self.__CONFIG_FILE_NAME = "data/config.txt"

        # read api_key and group_id
        with open(self.__CONFIG_FILE_NAME, "r") as configs:
            lines = configs.read().splitlines()
            self.__api_key = lines[0]
            self.__group_id = int(lines[2])

        # read subscriber_ids
        with open(self.__SUBSCRIPTION_ID_FILE_NAME, "r") as user_ids:
            self._subscriber_ids = [int(lne) for lne in user_ids]

        # read message id from where you should start (not used information)
        # why it's required?
        with open(self.__LATEST_MSG_ID_FILE_NAME, "r") as msg_id:
            self._message_ids = [int(lne) for lne in msg_id]


    def get_subscriber_ids(self):
        return self._subscriber_ids


    def save_subscriber_ids(self, ids = None):
        if (ids == None):
            ids = self._subscriber_ids
        self._subscriber_ids = ids
        with open(self.__SUBSCRIPTION_ID_FILE_NAME, "a") as f:
            for i in self._subscriber_ids:
                f.write(f'{i}')


    def get_api_key(self):
        return self.__api_key

    def get_group_id(self):
        return self.__group_id
