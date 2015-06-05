import logging
import sys

root = logging.getLogger()
root.setLevel(logging.INFO)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)

root.addHandler(stream_handler)
