import logging
from enum import StrEnum

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


class LogLevel(StrEnum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"


def configure_logging(log_level: str = LogLevel.error) -> None:
    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevel]

    if log_level not in log_levels:
        logging.basicConfig(level=logging.ERROR)
        return

    if log_level == LogLevel.debug:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT_DEBUG)

    logging.basicConfig(level=log_level)
