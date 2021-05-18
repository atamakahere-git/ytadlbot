import sqlite3
import os
from telegram import Update

STATUS = False
SQL_BASE_CMD = ''' INSERT INTO Users(chat_id,first_name,last_name,username,s_cmd,h_cmd,d_cmd)
              VALUES(?,?,?,?,?,?,?) '''
SQL_UPDATE_CMD = '''UPDATE Users
SET {} = {}
WHERE chat_id = ?;'''


def start_logger() -> sqlite3.Connection or bool:
    global STATUS
    os.remove('UserData.db-journal')
    conn = sqlite3.connect("UserData.db", check_same_thread=False)
    if conn:
        STATUS = True
        conn.execute("CREATE TABLE IF NOT EXISTS Users("
                     "chat_id INTEGER PRIMARY KEY,"
                     "first_name TEXT,"
                     "last_name TEXT,"
                     "username TEXT,"
                     "s_cmd INTEGER,"
                     "h_cmd INTEGER,"
                     "d_cmd INTEGER)")

        return conn
    return False


def log(update: Update, conn):
    global STATUS
    if not STATUS:
        return
    global SQL_BASE_CMD, SQL_UPDATE_CMD
    chat_id = update.effective_chat.id
    first_name = update.effective_chat.first_name
    last_name = update.effective_chat.last_name
    username = update.effective_chat.username
    cmd = update.message.text.split(' ')[0][1:]
    try:
        conn.execute(SQL_BASE_CMD, (chat_id, f"'{first_name}'", f"'{last_name}'", f"'{username}'", 0, 0, 0))
    except sqlite3.IntegrityError:
        try:
            if cmd == 'start':
                conn.execute(SQL_UPDATE_CMD.format('s_cmd', 's_cmd+1'), (chat_id,))
            elif cmd == 'help':
                conn.execute(SQL_UPDATE_CMD.format('h_cmd', 'h_cmd+1'), (chat_id,))
            else:
                conn.execute(SQL_UPDATE_CMD.format('d_cmd', 'h_cmd+1'), (chat_id,))
        except:
            print(f"Unable to log : {chat_id}")

    conn.commit()
