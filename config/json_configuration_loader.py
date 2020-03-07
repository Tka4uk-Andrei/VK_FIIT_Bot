import json


class ChatDescription:

    def __init__(self, update_callback, chat_info):
        self.__description = chat_info['chat_description']
        self.__chat_id = chat_info['chat_id']
        self.__subscribers = chat_info['subscribers']
        self.__update_callback = update_callback

    def get_description(self):
        return self.__description

    def get_chat_id(self):
        return self.__chat_id

    def get_subscribers(self):
        return self.__subscribers

    def add_subscriber(self, subscriber_id):
        self.__subscribers.append(subscriber_id)
        self.__update_callback()


class JsonConfiguration:

    def __init__(self):
        self.__JSON_FILE_PATH = "data/config.json"

        with open(self.__JSON_FILE_PATH, "r") as json_file:
            json_data = json.load(json_file)
        self.__raw_data = json_data

        self.__config_version = json_data['config_version']
        self.__vk_api_key = json_data['vk_api_key']
        self.__vk_api_version = json_data['vk_api_version']
        self.__group_id = json_data['group_id']

        self.__chats = dict()
        for chat_id in json_data['chats']:
            self.__chats[chat_id] = ChatDescription(self.__update_file,
                                                    json_data['chats'][chat_id])

    def get_config_version(self):
        return self.__config_version

    def get_api_key(self):
        return self.__vk_api_key

    def get_vk_api_version(self):
        return self.__vk_api_key

    def get_group_id(self):
        return self.__group_id

    def get_chat_description(self, chat_id):
        return self.__chats[chat_id]

    def __update_file(self):
        with open(self.__JSON_FILE_PATH, "w") as json_file:
            json.dump(self.__raw_data, json_file, indent=4)