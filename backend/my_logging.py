import logging


def my_logger():
    LOG_FORMAT = "%(levelname)s:     %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    return logging.getLogger(__name__)
