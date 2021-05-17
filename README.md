# Youtube Audio Downloader Bot
A Telegram bot written in python that downloads music from youtube and send it into the chat.

## Working
The bot filter out all the youtube urls from the received message and send the downloaded audio back to the user.


## Requirements
1. [Pafy](https://pythonhosted.org/Pafy/)
2. [python-telegram-bot](https://python-telegram-bot.org/)
3. media-tag
4. urlextract
5. requests

## Deploy the bot
Create a bot on telegram using [@botfather](t.me/botfather)  
Create an app on [heroku](https://dashboard.heroku.com/) 
Set env variables in heroku app
- BOT_TOKEN = your bot api token
- HEROKU_APP_NAME = name of your heroku app

Deploy the bot [read here](https://devcenter.heroku.com/articles/getting-started-with-python)

## Future plans
1. Playlist download option