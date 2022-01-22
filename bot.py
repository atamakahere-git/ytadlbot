from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from const import TOKEN, PORT, HEROKU_APP_NAME, POLLING, LOGGER, DBHANDLER, OPEN_CHANNEL_USERNAME
from databasehandler import check_in_db, add_to_db
from helper import *
from logger import log
from ytadllib import YTADL, FileDownloadError, FileSizeExceeded, UnableToDownload


OWNER_CHAT_ID = 0


def start(update: Update, context: CallbackContext) -> None:
    """Command handler to send start message"""
    log(update, LOGGER)
    update.message.reply_text(f"Hello {update.effective_user.first_name}, I'm youtube audio downloader bot! "
                              f"send me any youtube url and I'll download it for you!")


def help_bot(update: Update, context: CallbackContext) -> None:
    """Command handler for sending help message"""
    log(update, LOGGER)
    update.message.reply_text(f"Use telegram inline bot @vid to search youtube video and send me the link\n"
                              f"Type '@vid Video name' in msg and click on appropriate youtube video\n")


def donate(update: Update, context: CallbackContext) -> None:
    """Command handler for sending help message"""
    log(update, LOGGER)
    update.message.reply_text(f"Visit @donateatamaka to donate me")


def download_url(update: Update, context: CallbackContext, url: str) -> None:
    """Function to download and send single youtube url downloaded audio file. Sends appropriate error message to
    user """
    log(update, LOGGER)
    audio = None
    title = ''
    artist = ''
    try:
        audio = YTADL(url, url_only=False)
        if '-' in audio.pafy_obj.title:
            title = audio.pafy_obj.title.split('-')[1].strip()
            artist = audio.pafy_obj.title.split('-')[0].strip()

    except ValueError:
        update.message.reply_text("Invalid URL")

    if audio:
        if OPEN_CHANNEL_USERNAME:
            db_status = check_in_db(audio.url, DBHANDLER)
            if db_status:
                try:
                    context.bot.forward_message(chat_id=update.effective_chat.id,
                                                from_chat_id=OPEN_CHANNEL_USERNAME,
                                                message_id=db_status)
                    return
                except Exception as e:
                    print("Msg not found on channel")
    try:
        audio.processor_url()
    except FileSizeExceeded:
        update.message.reply_text("File size limit exceeded")
        return

    try:
        audio.download()
    except FileDownloadError:
        update.message.reply_text("Unable to download file")
        return
    except UnableToDownload:
        update.message.reply_text("Unable to download file")
        return

    if OPEN_CHANNEL_USERNAME:
        try:
            msg = context.bot.send_audio(chat_id=OPEN_CHANNEL_USERNAME,
                                         audio=audio.audio_file,
                                         title=title,
                                         thumb=audio.thumbnail,
                                         performer=artist,
                                         duration=get_sec(audio.pafy_obj.duration),
                                         timeout=60)
            context.bot.forward_message(chat_id=update.effective_chat.id,
                                        from_chat_id=OPEN_CHANNEL_USERNAME,
                                        message_id=msg.message_id)
            try:
                add_to_db(audio.url, msg.message_id, DBHANDLER)
            except Exception as e:
                print(e)
                print("DB not working")
        except Exception as e:
            print(e)
            print("Upload to open channel failed")
            context.bot.send_audio(chat_id=update.message.chat_id,
                                   audio=audio.audio_file,
                                   title=title,
                                   thumb=audio.thumbnail,
                                   performer=artist,
                                   duration=get_sec(audio.pafy_obj.duration),
                                   timeout=60)
    else:
        context.bot.send_audio(chat_id=update.message.chat_id,
                               audio=audio.audio_file,
                               title=title,
                               thumb=audio.thumbnail,
                               performer=artist,
                               duration=get_sec(audio.pafy_obj.duration),
                               timeout=60)


def extract_url_download(update: Update, context: CallbackContext) -> None:
    """Extract YouTube urls from the random text send to the bot and starts downloading and sending from url"""
    received_text = update.message.text
    yt_urls = get_links_from_text(received_text)
    yt_urls_msg = update.message.reply_text(pretty_url_string(yt_urls), disable_web_page_preview=True)
    if len(yt_urls) > 0:
        for url in yt_urls:
            if 'list=' in url:
                download_playlist_url(update, context, url)
            else:
                try:
                    download_url(update, context, url)
                except FileSizeExceeded:
                    update.message.reply_text("File size exceeded")
        context.bot.delete_message(message_id=yt_urls_msg.message_id, chat_id=yt_urls_msg.chat_id)


def download_playlist_url(update: Update, context: CallbackContext, pl_link: str) -> None:
    """Extract YouTube urls from the playlist url send to the bot and starts downloading and sending each file"""
    pl_link = get_pl_link_from_url(pl_link)
    yt_urls = get_yt_links_from_pl(pl_link)
    yt_urls_msg = update.message.reply_text(pretty_url_string(yt_urls), disable_web_page_preview=True)
    if len(yt_urls) > 0:
        for url in yt_urls:
            download_url(update, context, url)
        context.bot.delete_message(message_id=yt_urls_msg.message_id, chat_id=yt_urls_msg.chat_id)


def main() -> None:
    updater = None
    try:
        updater = Updater(TOKEN)
    except Exception:
        print("Token is incorrect")
        exit(1)
    # Command handlers
    updater.dispatcher.add_handler(CommandHandler('start', start, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('help', help_bot, run_async=True))
    updater.dispatcher.add_handler(CommandHandler('donate', donate, run_async=True))
    # Message handler
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, extract_url_download, run_async=True))
    # Polling method to test on local machine
    if POLLING:
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
