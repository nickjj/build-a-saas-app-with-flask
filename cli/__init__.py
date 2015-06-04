import logging
import sys

from config import settings

root = logging.getLogger()
root.setLevel(settings.LOG_LEVEL)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(settings.LOG_LEVEL)

root.addHandler(stream_handler)
