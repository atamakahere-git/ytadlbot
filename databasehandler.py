import psycopg2
import urllib.parse as urlparse


def start_dbhandler(audio_db: str) -> bool:
    result = urlparse.urlparse(audio_db)
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


def add_to_db(url: str, msg_id: int, conn):
    conn.execute("INSERT INTO Audios(yt_link,msg_id)"
                 "VALUES (?,?)", (url, msg_id))
