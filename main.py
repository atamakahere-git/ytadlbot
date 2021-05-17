import bot
from const import TOKEN, PORT, HEROKU_APP_NAME

if __name__ == '__main__':
    if TOKEN is None:
        print("Token not found")
    elif PORT is None:
        print("Port not found")
    elif HEROKU_APP_NAME is None:
        print("App name not fount")
    else:
        bot.main()