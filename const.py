import os
from logger import start_logger

TOKEN = os.environ.get('BOT_TOKEN', None)
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', None)
PASS_HASH = os.environ.get('PASS_HASH', None)
# only enable pooling for testing on local machine, Heroku will only work on webhook method
POOLING = os.environ.get('POOLING', False)

# start the logger
LOGGER = start_logger()
