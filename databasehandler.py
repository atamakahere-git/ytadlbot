import os
import sqlite3


def start_dbhandler() -> sqlite3.Connection or bool:
    try:
        os.remove('AudioDB.db-journal')
    except FileNotFoundError:
        pass
    conn = sqlite3.connect("AudioDB.db", check_same_thread=False)
    if conn:
        conn.execute("CREATE TABLE IF NOT EXISTS Audios("
                     "yt_link TEXT PRIMARY KEY,"
                     "msg_id INTEGER)")

        return conn
    return False


def check_in_db(url, conn) -> int or None:
    cursor = conn.execute("SELECT msg_id from Audios where yt_link = ?", (url,))
    row = cursor.fetchall()
    if len(row) > 0:
        return int(row[0][0])
    return None


def add_to_db(url: str, msg_id: int, conn: sqlite3.Connection):
    conn.execute("INSERT INTO Audios(yt_link,msg_id)"
                 "VALUES (?,?)", (url, msg_id))
