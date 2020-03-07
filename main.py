import logging
from logging.handlers import RotatingFileHandler
import threading

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from config.json_configuration_loader import JsonConfiguration
from strategies.advanced_strategy import AdvancedStrategy

APP_LOGGER = logging

def main_loop(configuration, strategy, longpoll):
    APP_LOGGER.info('Server started listening')

    while True:
        try:
            APP_LOGGER.info('Event handling start...')
            for event in longpoll.listen():
                APP_LOGGER.info('Event catched')
                strategy.handle_event(event)
        except Exception as e:
            APP_LOGGER.exception(e)
            APP_LOGGER.info("Reestablishing server")
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
    setup_logger(fileFlag=True)

    # setup configuration
    configuration = JsonConfiguration()
    # setup connection to VK API
    vk_session = vk_api.VkApi(token=configuration.get_api_key())
    session_api = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, configuration.get_group_id(), 100)
    # setup strategy
    strategy = AdvancedStrategy(session_api, APP_LOGGER, configuration)
    
    main_loop(configuration, strategy, longpoll)
