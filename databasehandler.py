import urllib.parse as urlparse

import psycopg2

STATUS = False


def start_dbhandler(audio_db: str):
    global STATUS
    try:
        result = urlparse.urlparse(audio_db)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
    except Exception as e:
        print(e)
        print("DB url is not valid")
        STATUS = False
        return None
    try:
        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        STATUS = True
    except Exception as e:
        print(e)
        print("Connection establishment failed")
        STATUS = False
        return None
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("CREATE TABLE IF NOT EXISTS Audios("
                        "yt_link TEXT PRIMARY KEY,"
                        "msg_id INTEGER)")
        except Exception as e:
            print(e)
            print("Table creation failed")
            STATUS = False
            return None
        conn.commit()
        return conn
    return False


def check_in_db(url, conn) -> int or None:
    if STATUS:
        cur = conn.cursor()
        row = []
        try:
            cur.execute("SELECT msg_id from Audios where yt_link = {}".format("'" + url + "'"))
            row = cur.fetchall()
        except Exception as e:
            print(e)
            print("Can't run find command!")

        if len(row) > 0:
            return int(row[0][0])
        else:
            return None
    return None


def add_to_db(url: str, msg_id: int, conn):
    if STATUS:
        cur = conn.cursor()
        cur.execute("INSERT INTO Audios(yt_link,msg_id)"
                    "VALUES ({},{}) ON CONFLICT UPDATE msg_id = {}".format("'" + url + "'", msg_id, msg_id))
        conn.commit()
    else:
        print("DB is not active cannot add the entry!")
