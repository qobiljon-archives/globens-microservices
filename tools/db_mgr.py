from psycopg2 import extras as psycopg2_extras
from datetime import datetime
from tools import settings
from tools import utils
import psycopg2


# region initializing and terminating db connection
def get_db_connection():
    if settings.db_conn is None:
        settings.db_conn = psycopg2.connect(
            host=settings.db_settings['host'],
            database=settings.db_settings['database'],
            user=settings.db_settings['user'],
            password=settings.db_settings['password']
        )
        print('database initialized', settings.db_conn)
    return settings.db_conn


def end():
    get_db_connection().close()


# endregion


def get_user(email=None, session_key=None):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)
    if email is not None:
        cur.execute('select * from "gb_user" where "email" = %s;', (
            email,
        ))
    elif session_key is not None:
        cur.execute('select * from "gb_user" where "sessionKey" = %s;', (
            session_key,
        ))
    gb_user = cur.fetchone()
    cur.close()
    return gb_user


def create_or_update_user(email, name, picture, tokens):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    session_key = utils.md5(value=f'{email}{utils.now_us()}')
    if get_user(email=email) is not None:
        cur.execute(
            'update "gb_user" set name = %s, "picture" = %s, "pictureBlob" = %s, "tokens" = %s, "sessionKey" = %s where "email"=%s;',
            (
                name,
                picture,
                utils.load_picture_bytes(picture=picture),
                tokens,
                session_key,
                email
            ))
    else:
        cur.execute(
            'insert into "gb_user"("email", "name", "picture","pictureBlob","tokens","sessionKey") values (%s,%s,%s,%s,%s,%s);',
            (
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


def get_business_page(business_page_id):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    cur.execute('select * from "gb_business_page" where "id" = %s;', (
        business_page_id,
    ))
    gb_business_page = cur.fetchone()

    cur.close()
    return gb_business_page


def get_business_pages(gb_user):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    # step 1 : get user's jobs (from vacancies table)
    cur.execute('select * from "gb_vacancy" where "user_id"=%s;', (
        gb_user['id'],
    ))
    gb_vacancies = cur.fetchall()

    # step 2 : get unique campaigns related of the jobs/vacancies
    res = []
    for gb_vacancy in gb_vacancies:
        cur.execute('select * from "gb_business_page" where "id" = %s;', (
            gb_vacancy['business_page_id'],
        ))
        gb_business_page = cur.fetchone()
        tp = (gb_business_page, gb_vacancy)
        if tp not in res:
            res += [tp]

    cur.close()
    return res


def create_business_page(gb_user, title, picture_blob):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    # create an individual/small business page
    cur.execute('insert into "gb_business_page"("title", "type", "pictureBlob") values (%s,%s,%s) returning "id";', (
        title,
        'large business',
        psycopg2.Binary(picture_blob)
    ))
    business_page_id = cur.fetchone()[0]

    # create business owner vacancy/position for the business page
    cur.execute('insert into "gb_vacancy"("title", "role", "business_page_id") values (%s,%s,%s) returning "id";', (
        'Business owner',
        'business owner',
        business_page_id
    ))
    business_owner_vacancy_id = cur.fetchone()[0]

    # map the user with the business owner vacancy/position
    cur.execute('update "gb_vacancy" set "user_id" = %s where "id" = %s;', (
        gb_user['id'],
        business_owner_vacancy_id
    ))

    cur.close()
    get_db_connection().commit()


def get_products(gb_business_page):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    cur.execute('select * from "gb_product" where "business_page_id" = %s;', (
        gb_business_page['id'],
    ))
    gb_products = cur.fetchall()

    cur.close()
    return gb_products


def create_product(gb_user, gb_business_page, name, picture_blob):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    cur.execute('insert into "gb_product"("name", "pictureBlob", "business_page_id") values (%s,%s,%s) returning "id";', (
        name,
        picture_blob,
        gb_business_page['id']
    ))
    new_product_id = cur.fetchone()[0]

    cur.execute('insert into "gb_product_log"("timestamp", "action", "product_id", "user_id") values (%s,%s,%s,%s);', (
        datetime.now(),
        'create',
        new_product_id,
        gb_user['id']
    ))

    cur.close()
    get_db_connection().commit()
