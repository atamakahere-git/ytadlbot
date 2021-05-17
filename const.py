import os

TOKEN = os.environ.get('BOT_TOKEN', None)
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', None)
