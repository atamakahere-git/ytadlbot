import bot
from const import HEROKU_APP_NAME, POLLING, PORT, TOKEN

if __name__ == "__main__":
    if TOKEN is None:
        print("Token not found")
    elif PORT is None and not POLLING:
        print("Port not found")
    elif HEROKU_APP_NAME is None and not POLLING:
        print("App name not found")
    else:
        bot.main()
