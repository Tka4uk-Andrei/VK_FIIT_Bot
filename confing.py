class ConfigurationType:

    def __init__(self):
        self.type = ""
        self.set_legacy()

    def set_json(self):
        self.type = "json"

    def set_legacy(self):
        self.type = "legacy"

    def get_config_type(self):
        return self.type


class Configuration:

    def __init__(self, config_type):
        # Path to data files
        SUBSCRIPTION_ID_FILE_NAME = "data/subscribedIds.txt"
        LATEST_MSG_ID_FILE_NAME = "data/latest_msg_id.txt"
        CONFIG_FILE_NAME = "data/config.txt"

        # Read global constants
        with open(CONFIG_FILE_NAME, "r") as configs:
            VK_API_KEY = configs.readline()[0:-1]
            VK_VERSION = configs.readline()[0:-1]
            VK_GROUP_ID = configs.readline()

        # read added early ids from file
        with open(SUBSCRIPTION_ID_FILE_NAME, "r") as subscribedIds:
            for line in subscribedIds:
                connectedIds.append(int(line))

        # read message id from where you should start
        with open(LATEST_MSG_ID_FILE_NAME, "r") as msgId:
            for line in msgId:
                messageCounter = int(line)