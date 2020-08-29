from psycopg2 import extras as psycopg2_extras
from tools import settings
from tools import utils
import psycopg2

conn = None


# region initializing and terminating db connection
def get_db_connection():
    if settings.db_conn is None:
        settings.db_conn = psycopg2.connect(
            host='165.246.42.172',
            database='globens_db',
            user='postgres',
            password='postgres'
        )
        print('database initialized', settings.db_conn)
    return settings.db_conn


def end():
    get_db_connection().close()


# endregion


def get_user(email):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)
    cur.execute('select * from "gb_user" where "email" = %s;', (
        email,
    ))
    gb_user = cur.fetchone()
    cur.close()
    return gb_user


def user_exists(email):
    return get_user(email=email) is not None


def create_or_update_user(email, name, picture, tokens):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    session_key = utils.md5(value=f'{email}{utils.now_us()}')
    if user_exists(email=email):
        cur.execute('update "gb_user" set name = %s, "picture" = %s, "pictureBlob" = %s, "tokens" = %s, "sessionKey" = %s where "email"=%s;', (
            name,
            picture,
            utils.load_picture_bytes(picture=picture),
            tokens,
            session_key,
            email
        ))
    else:
        cur.execute('insert into "gb_user"("email", "name", "picture","pictureBlob","tokens","sessionKey") values (%s,%s,%s,%s,%s,%s);', (
            email,
            name,
            picture,
            utils.load_picture_bytes(picture=picture),
            tokens,
            session_key
        ))

    cur.close()
    get_db_connection().commit()
    return get_user(email=email), session_key
