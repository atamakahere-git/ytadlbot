import psycopg2
import urllib.parse as urlparse
from telegram import Update

STATUS = False
SQL_BASE_CMD = ''' INSERT INTO Users(chat_id,first_name,last_name,username,s_cmd,h_cmd,d_cmd)
              VALUES(?,?,?,?,?,?,?) '''
SQL_UPDATE_CMD = '''UPDATE Users
SET {} = {}
WHERE chat_id = ?;'''


def start_logger(user_db: str):
    global STATUS
    result = urlparse.urlparse(user_db)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    conn = psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )
    if conn:
        STATUS = True
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Users("
                    "chat_id INTEGER PRIMARY KEY,"
                    "first_name TEXT,"
                    "last_name TEXT,"
                    "username TEXT,"
                    "s_cmd INTEGER,"
                    "h_cmd INTEGER,"
                    "d_cmd INTEGER)")
        conn.commit()
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
    cur = conn.cursor()
    try:
        cur.execute(SQL_BASE_CMD, (chat_id, f"'{first_name}'", f"'{last_name}'", f"'{username}'", 0, 0, 0))
    except Exception as e:
        print(e)
        try:
            if cmd == 'start':
                cur.execute(SQL_UPDATE_CMD.format('s_cmd', 's_cmd+1'), (chat_id,))
            elif cmd == 'help':
                cur.execute(SQL_UPDATE_CMD.format('h_cmd', 'h_cmd+1'), (chat_id,))
            else:
                cur.execute(SQL_UPDATE_CMD.format('d_cmd', 'h_cmd+1'), (chat_id,))
        except:
            print(f"Unable to log : {chat_id}")

    conn.commit()
