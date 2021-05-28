import bot
from const import TOKEN, PORT, HEROKU_APP_NAME, POOLING

if __name__ == '__main__':
    if TOKEN is None:
        print("Token not found")
    elif PORT is None and not POOLING:
        print("Port not found")
    elif HEROKU_APP_NAME is None and not POOLING:
        print("App name not found")
    else:
        bot.main()
