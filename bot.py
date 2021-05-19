import hashlib
import os
import requests
from telegram import Update, Message
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from const import TOKEN, PORT, HEROKU_APP_NAME, POOLING, LOGGER, PASS_HASH, DBHANDLER, OPEN_CHANNEL_USERNAME
from downloader import download_from_url
from helper import *
from databasehandler import check_in_db, add_to_db
from logger import log

OWNER_CHAT_ID = 0


def start(update: Update, context: CallbackContext) -> None:
    """Command handler to send start message"""
    log(update, LOGGER)
    update.message.reply_text(f"Hello {update.effective_user.first_name}, I'm youtube audio downloader bot! "
                              f"send me any youtube url and I'll download it for you!")


def help_bot(update: Update, context: CallbackContext) -> None:
    """Command handler for sending help message"""
    log(update, LOGGER)
    update.message.reply_text(f"Simply send the url, share from youtube app this bot is smart enough to extract urls "
                              f"from given text and download multiple audio!\n\nCommands available :\n/d or /download :"
                              f" download audio with the provided url\n/pldl : Download playlist from its url\n/about "
                              f": about the developer\n/help : Help message")


def download(update: Update, context: CallbackContext) -> None:
    """Command handler for /download or /d command, Receives the text, splits it into parts and tries to retrieve
    youtube urls from it , sends error message to user"""
    cmd = update.message.text.strip().split(" ")
    if len(cmd) < 2:
        update.message.reply_text(f"Invalid command usage, please send url along with download command!")
        return
    if len(cmd) > 2:
        update.message.reply_text(f"Invalid command usage, please provide single along with download command!")
        return
    url = cmd[1]
    if not is_yt_url(url):
        update.message.reply_text(f"URL id not correct, please check the link")
        return
    else:
        yt_url_msg = update.message.reply_text("Downloading ....")
        download_url(update, context, url)
        context.bot.delete_message(message_id=yt_url_msg.message_id, chat_id=yt_url_msg.chat_id)


def download_url(update: Update, context: CallbackContext, url: str) -> None:
    """Function to download and send single youtube url downloaded audio file. Sends appropriate error message to
    user """
    log(update, LOGGER)
    url = refine_yt_url(url)
    if OPEN_CHANNEL_USERNAME:
        db_status = check_in_db(url, DBHANDLER)
        if db_status:
            context.bot.forward_message(chat_id=update.effective_chat.id,
                                        from_chat_id=OPEN_CHANNEL_USERNAME,
                                        message_id=db_status)
            return
    audio_meta = download_from_url(url, update.message.chat.id)
    if audio_meta:
        if audio_meta['status']:
            chat_id = update.message.chat.id
            audio_file = open(audio_meta['file'], 'rb')
            audio_thumb = requests.get(audio_meta['thumb']).content
            try:
                if OPEN_CHANNEL_USERNAME:
                    msg = context.bot.send_audio(chat_id=OPEN_CHANNEL_USERNAME,
                                                 audio=audio_file,
                                                 title=audio_meta['title'],
                                                 thumb=audio_thumb,
                                                 performer=audio_meta['author'],
                                                 duration=audio_meta['duration'],
                                                 timeout=120)
                    context.bot.forward_message(chat_id=update.effective_chat.id,
                                                from_chat_id=OPEN_CHANNEL_USERNAME,
                                                message_id=msg.message_id)
                    add_to_db(url, msg.message_id, DBHANDLER)
                else:
                    context.bot.send_audio(chat_id=chat_id,
                                           audio=audio_file,
                                           title=audio_meta['title'],
                                           thumb=audio_thumb,
                                           performer=audio_meta['author'],
                                           duration=audio_meta['duration'],
                                           timeout=120)
            except Exception as e:
                update.message.reply_text("Unable to upload file")
            audio_file.close()
            os.remove(audio_meta['file'])
        else:
            update.message.reply_text(audio_meta['err'])
            return
    else:
        update.message.reply_text("Invalid youtube url!")


def extract_url_download(update: Update, context: CallbackContext) -> None:
    """Extract youtube urls from the random text send to the bot and starts downloading and sending from url"""
    received_text = update.message.text
    yt_urls = get_links_from_text(received_text)
    yt_urls_msg = update.message.reply_text(pretty_url_string(yt_urls), disable_web_page_preview=True)
    if len(yt_urls) > 0:
        for url in yt_urls:
            if 'list=' in url:
                download_playlist_url(update, context, url)
            else:
                download_url(update, context, url)
        context.bot.delete_message(message_id=yt_urls_msg.message_id, chat_id=yt_urls_msg.chat_id)


def download_playlist(update: Update, context: CallbackContext) -> None:
    """Extract youtube urls from the playlist url send to the bot and starts downloading and sending each file"""
    log(update, LOGGER)
    pl_link = update.message.text.split(' ')
    if len(pl_link) < 2:
        update.message.reply_text("Please provide playlist url with this command")
        return
    if len(pl_link) > 2:
        update.message.reply_text("Please provide only 1 link \n Proper usage : /pldl youtube-playlist-url")
        return
    pl_link = pl_link[1]
    if 'list=' not in pl_link:
        update.message.reply_text("Please provide valid playlist url")
        return
    pl_link = get_pl_link_from_url(pl_link)
    if pl_link == '':
        update.message.reply_text("Unable to resolve playlist url")
        return
    yt_urls = get_yt_links_from_pl(pl_link)
    yt_urls_msg = update.message.reply_text(pretty_url_string(yt_urls), disable_web_page_preview=True)
    if len(yt_urls) > 0:
        for url in yt_urls:
            download_url(update, context, url)
        context.bot.delete_message(message_id=yt_urls_msg.message_id, chat_id=yt_urls_msg.chat_id)


def download_playlist_url(update: Update, context: CallbackContext, pl_link: str) -> None:
    """Extract youtube urls from the playlist url send to the bot and starts downloading and sending each file"""
    pl_link = get_pl_link_from_url(pl_link)
    yt_urls = get_yt_links_from_pl(pl_link)
    yt_urls_msg = update.message.reply_text(pretty_url_string(yt_urls), disable_web_page_preview=True)
    if len(yt_urls) > 0:
        for url in yt_urls:
            download_url(update, context, url)
        context.bot.delete_message(message_id=yt_urls_msg.message_id, chat_id=yt_urls_msg.chat_id)


def my_chat_id(update: Update, context: CallbackContext):
    update.message.reply_text(f"Your chat id : {update.effective_chat.id}")


def set_owner_id(update: Update, context: CallbackContext):
    """Use to set owner chat id by providing password"""
    password = update.message.text.split(" ")
    if len(password) != 2:
        return
    password = password[1].strip()
    phash = hashlib.sha256((password + TOKEN).encode()).hexdigest()
    if phash == PASS_HASH:
        global OWNER_CHAT_ID
        OWNER_CHAT_ID = update.message.chat_id
        update.message.reply_text(f"Owner chat id set to : {OWNER_CHAT_ID}")
        context.bot.send_message(chat_id=OWNER_CHAT_ID, text="TEST")
        return


def send_db(update: Update, context: CallbackContext):
    """Send the database to the user"""
    if update.effective_chat.id == OWNER_CHAT_ID:
        context.bot.send_document(chat_id=OWNER_CHAT_ID, filename='UserData.db',
                                  document=open('UserData.db', 'rb').read())


def main() -> None:
    updater = None
    try:
        updater = Updater(TOKEN)
    except Exception:
        print("Token is incorrect")
        exit(1)
    # Command handlers
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_bot))
    updater.dispatcher.add_handler(CommandHandler('download', download, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('d', download, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('dlpl', download_playlist, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('download_playlist', download_playlist, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('mychatid', my_chat_id, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('setownerid', set_owner_id))
    updater.dispatcher.add_handler(CommandHandler('rcdata', send_db))

    # Message handler
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, extract_url_download, run_async=True))
    # Pooling method to test on local machine
    if POOLING:
        updater.start_polling()
    else:
        # webhook method for heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN,
                              webhook_url="https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
    updater.idle()
    LOGGER.close()
    DBHANDLER.close()


if __name__ == '__main__':
    main()
