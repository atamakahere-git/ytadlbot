import urllib.parse as urlparse

import psycopg2
from telegram import Update

STATUS = False
SQL_BASE_CMD = ''' INSERT INTO Users(chat_id,first_name,last_name,username,usage)
              VALUES({},{},{},{},{}) '''
SQL_UPDATE_CMD = '''UPDATE Users
SET usage = usage + 1
WHERE chat_id = {};'''


def start_logger(user_db: str):
    global STATUS
    result = urlparse.urlparse(user_db)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    try:
        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
    except Exception as e:
        print(e)
        print("Connection establishment failed")
        STATUS = False
        return None
    if conn:
        STATUS = True
        cur = conn.cursor()
        try:
            cur.execute("CREATE TABLE IF NOT EXISTS Users("
                        "chat_id INTEGER PRIMARY KEY,"
                        "first_name TEXT,"
                        "last_name TEXT,"
                        "username TEXT,"
                        "usage INTEGER DEFAULT 0)")
        except Exception as e:
            print(e)
            print("Table creation failed")
            STATUS = False
            return None
        conn.commit()
        return conn
    return None


def log(update: Update, conn):
    global STATUS
    if not STATUS:
        print("DB is not connected, cannot log!")
        return
    global SQL_BASE_CMD, SQL_UPDATE_CMD
    chat_id = update.effective_chat.id
    first_name = update.effective_chat.first_name
    last_name = update.effective_chat.last_name
    username = update.effective_chat.username
    cur = conn.cursor()
    try:
        cur.execute(
            SQL_BASE_CMD.format(chat_id,
                                "'" + first_name + "'",
                                "'" + last_name + "'",
                                "'" + username + "'",
                                0))
    except Exception:
        try:
            cur.execute(SQL_UPDATE_CMD.format(chat_id))
        except Exception as e:
            print(e)
            print(f"Update failed for {chat_id}")

    conn.commit()
