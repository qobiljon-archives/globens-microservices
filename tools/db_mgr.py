from psycopg2 import extras as psycopg2_extras
from datetime import datetime
from tools import settings
from tools import utils
import psycopg2


# region commons
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


# region user management
def get_user(email=None, user_id=None, session_key=None):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)
    if email is not None:
        cur.execute('select * from "gb_user" where "email" = %s;', (
            email,
        ))
    elif user_id is not None:
        cur.execute('select * from "gb_user" where "id" = %s;', (
            user_id,
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


# endregion


# region business page management
def get_business_page_ids(gb_user):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    # step 1 : get user's jobs (from vacancies table)
    cur.execute('select * from "gb_job" where "user_id"=%s;', (
        gb_user['id'],
    ))
    gb_job = cur.fetchall()

    # step 2 : get unique campaigns related of the jobs/vacancies
    business_page_ids = set()
    for gb_job in gb_job:
        cur.execute('select "id" from "gb_business_page" where "id" = %s;', (
            gb_job['business_page_id'],
        ))
        business_page_ids.add(cur.fetchone()[0])

    cur.close()
    return list(business_page_ids)


def get_business_page(business_page_id):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    cur.execute('select * from "gb_business_page" where "id" = %s;', (
        business_page_id,
    ))
    gb_business_page = cur.fetchone()

    cur.close()
    return gb_business_page


def get_user_role_in_business_page(gb_user, gb_business_page):
    cur = get_db_connection().cursor()

    cur.execute('select "role" from "gb_job" where "user_id" = %s and "business_page_id" = %s;', (
        gb_user['id'],
        gb_business_page['id'],
    ))
    gb_job = cur.fetchone()

    cur.close()
    return "consumer" if gb_job is None else gb_job[0]


def create_business_page(gb_user, title, picture_blob):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    # create a large business page
    cur.execute('insert into "gb_business_page"("title", "type", "pictureBlob") values (%s,%s,%s) returning "id";', (
        title,
        'large business',
        psycopg2.Binary(picture_blob)
    ))
    business_page_id = cur.fetchone()[0]

    # create business owner job position for the business page
    cur.execute('insert into gb_job("title", "role", "business_page_id") values (%s,%s,%s) returning "id";', (
        'Business owner',
        'business owner',
        business_page_id
    ))
    business_owner_job_id = cur.fetchone()[0]

    # map the user with the business owner vacancy (empty job position)
    cur.execute('update gb_job set "user_id" = %s where "id" = %s;', (
        gb_user['id'],
        business_owner_job_id
    ))

    cur.close()
    get_db_connection().commit()


def get_business_page_job_ids(gb_business_page):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    cur.execute('select "id" from "gb_job" where "business_page_id" = %s;', (
        gb_business_page['id'],
    ))
    job_ids = [job_id[0] for job_id in cur.fetchall()]

    cur.close()
    return job_ids


def get_business_page_product_ids(gb_business_page):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    cur.execute('select "id" from "gb_product" where "business_page_id" = %s;', (
        gb_business_page['id'],
    ))
    product_ids = [product_id[0] for product_id in cur.fetchall()]

    cur.close()
    return product_ids


# endregion


# region product management
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


def get_product(product_id):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)
    cur.execute('select * from "gb_product" where "id" = %s;', (
        product_id,
    ))
    gb_product = cur.fetchone()

    cur.close()
    return gb_product


# endregion


# region job/vacancy management
def create_vacant_job(gb_user, gb_business_page, title):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    cur.execute('insert into gb_job("title", "role", "business_page_id") values (%s,%s,%s) returning "id";', (
        title,
        'employee',
        gb_business_page['id']
    ))
    new_job_id = cur.fetchone()[0]

    cur.execute('insert into "gb_job_log"("timestamp", "action", "job_id", "user_id") values (%s,%s,%s,%s);', (
        datetime.now(),
        'create',
        new_job_id,
        gb_user['id']
    ))

    cur.close()
    get_db_connection().commit()


def get_next_k_vacant_jobs(previous_vacant_job_id, k, filter_details):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    if filter_details.useFilter:
        if previous_vacant_job_id is None:
            cur.execute('select * from "gb_job" where "user_id" is null and "title" like %s order by "id" limit %s;', (
                f'%{filter_details.filterText}%',
                k
            ))
        else:
            cur.execute('select * from "gb_job" where "id" > %s and "user_id" is null and "title" like %s order by "id" limit %s;', (
                previous_vacant_job_id,
                f'%{filter_details.filterText}%',
                k
            ))
    else:
        if previous_vacant_job_id is None:
            cur.execute('select * from "gb_job" where "user_id" is null order by "id" limit %s;', (
                k
            ))
        else:
            cur.execute('select * from "gb_job" where "id" > %s and "user_id" is null order by "id" limit %s;', (
                previous_vacant_job_id,
                k
            ))
    gb_vacancies = cur.fetchall()

    cur.close()
    return gb_vacancies


def get_job(job_id):
    cur = get_db_connection().cursor(cursor_factory=psycopg2_extras.DictCursor)

    cur.execute('select * from "gb_job" where "id" = %s;', (
        job_id,
    ))
    gb_job = cur.fetchone()

    cur.close()
    return gb_job
# endregion
