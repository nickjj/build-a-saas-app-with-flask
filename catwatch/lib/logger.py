import logging
import sys

LOG_LEVEL = None

try:
    from instance import settings

    LOG_LEVEL = settings.LOG_LEVEL
except (ImportError, AttributeError):
    from config import settings

    LOG_LEVEL = settings.LOG_LEVEL

LOGGING_LEVEL = 0
if LOG_LEVEL == 'DEBUG':
    LOGGING_LEVEL = 10
elif LOG_LEVEL == 'INFO':
    LOGGING_LEVEL = 20
elif LOG_LEVEL == 'WARNING':
    LOGGING_LEVEL = 30
elif LOG_LEVEL == 'ERROR':
    LOGGING_LEVEL = 40
elif LOG_LEVEL == 'CRITICAL':
    LOGGING_LEVEL = 50

root = logging.getLogger()
root.setLevel(LOGGING_LEVEL)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(LOGGING_LEVEL)

root.addHandler(stream_handler)
