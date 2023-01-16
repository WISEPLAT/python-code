import configparser
import logging


def init_settings():
    config = configparser.ConfigParser()

    config.read('settings.ini')
    logging.debug("Config loaded: {}".format(config.items()))
    return config


robot_settings = init_settings()


def settings():
    return robot_settings
