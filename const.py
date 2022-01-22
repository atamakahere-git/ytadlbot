import os
from logger import start_logger
from databasehandler import start_dbhandler

TOKEN = os.environ.get('BOT_TOKEN', None)
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', None)
PASS_HASH = os.environ.get('PASS_HASH', None)
# only enable pooling for testing on local machine, Heroku will only work on webhook method
POLLING = os.environ.get('POOLING', False)
OPEN_CHANNEL_USERNAME = os.environ.get('OPEN_CHANNEL_USERNAME', None)
# Database connection urls
USER_DB = os.environ.get('USER_DB', None)
AUDIO_DB = os.environ.get('AUDIO_DB', None)

# start the logger
LOGGER = start_logger(user_db=USER_DB)
DBHANDLER = start_dbhandler(audio_db=AUDIO_DB)
