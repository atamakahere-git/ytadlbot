import os
from const import TOKEN, PORT, HEROKU_APP_NAME
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from helper import get_links_from_text, pretty_url_string
from downloader import download_from_url


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"Hello {update.effective_user.first_name}, I'm youtube audio downloader bot! "
                              f"send me any youtube url and I'll download it for you!")


def help_bot(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"Simply send the url, share from youtube app this bot is smart enough to extract urls "
                              f"from given text and download multiple audio!\n\nCommands available :\n/d or /download :"
                              f" download audio with the provided url\n/help : Help message")


def download(update: Update, context: CallbackContext) -> None:
    cmd = update.message.text.strip().split(" ")
    if len(cmd) < 2:
        update.message.reply_text(f"Invalid command usage, please send url along with download command!")
    elif len(cmd) > 2:
        update.message.reply_text(f"Invalid command usage, please provide single along with download command!")
    else:
        yt_url_msg = update.message.reply_text("Downloading ....")
        download_url(update, context, update.message.text.split(' ')[1])
        context.bot.delete_message(message_id=yt_url_msg.message_id, chat_id=yt_url_msg.chat_id)


def download_url(update: Update, context: CallbackContext, url: str) -> None:
    audio_meta = download_from_url(url, update.message.chat.id)
    if audio_meta:
        if audio_meta['status']:
            chat_id = update.message.chat.id
            audio_file = open(audio_meta['file'], 'rb')
            audio_thumb = requests.get(audio_meta['thumb']).content
            try:
                context.bot.send_audio(chat_id=chat_id, audio=audio_file, title=audio_meta['title'], thumb=audio_thumb,
                                       performer=audio_meta['author'], timeout=120)
            except:
                update.message.reply_text("Unable to upload file")
            audio_file.close()
            os.remove(audio_meta['file'])
        else:
            update.message.reply_text(audio_meta['err'])
            return
    else:
        update.message.reply_text("Invalid youtube url!")


def extract_url_download(update: Update, context: CallbackContext):
    received_text = update.message.text
    yt_urls = get_links_from_text(received_text)
    yt_urls_msg = update.message.reply_text(pretty_url_string(yt_urls), disable_web_page_preview=True)
    if len(yt_urls) > 0:
        for url in yt_urls:
            download_url(update, context, url)
        context.bot.delete_message(message_id=yt_urls_msg.message_id, chat_id=yt_urls_msg.chat_id)


def main() -> None:
    try:
        updater = Updater(TOKEN)
    except:
        print("Token is incorrect")
        exit(1)

    # Command handlers
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_bot))
    updater.dispatcher.add_handler(CommandHandler('download', download, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('d', download, run_async=True))

    # Message handler
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, extract_url_download, run_async=True))

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url="https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))


if __name__ == '__main__':
    main()
