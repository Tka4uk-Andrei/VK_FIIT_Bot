import logging
from logging.handlers import RotatingFileHandler
import threading

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from config.legacy_configuration_loader import LegacyConfigurationLoader
from strategies.legacy_strategy import LegacyStrategy

APP_LOGGER = logging

def main_loop(configuration):
    # setup connection to VK API
    vk_session = vk_api.VkApi(token=configuration.get_api_key())
    session_api = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, configuration.get_group_id(), 100)

    APP_LOGGER.info('Server started listening')
    strategy = LegacyStrategy(session_api, APP_LOGGER, configuration)

    while True:
        try:
            for event in longpoll.listen():
                APP_LOGGER.info('Event handling start...')
                strategy.handle_event(event)
        except Exception as e:
            APP_LOGGER.exception(e)
            pass


def setup_logger(fileFlag):
    global APP_LOGGER

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

    log_file = 'server.log'

    if (fileFlag):
        my_handler = RotatingFileHandler(
            log_file,
            mode='a',
            maxBytes=(5 * 1024 * 1024),
            backupCount=2,
            encoding=None,
            delay=False
        )
    else:
        my_handler = logging.StreamHandler()

    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)

    APP_LOGGER = logging.getLogger('root')
    APP_LOGGER.setLevel(logging.INFO)
    APP_LOGGER.addHandler(my_handler)


if __name__ == '__main__':
    setup_logger(True)
    main_loop(LegacyConfigurationLoader())
    # why we need thread?
    # main_tread = threading.Thread(target=main_loop, args=([LegacyConfigurationLoader()]))
    # main_tread.start()
