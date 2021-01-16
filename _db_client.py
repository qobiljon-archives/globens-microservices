from tools import settings
import psycopg2
import psycopg2.extras as psycopg2_extras

db_conn = psycopg2.connect(
    host='165.246.42.172',
    database='globens_db',
    user='postgres',
    password='postgres'
)

cur = db_conn.cursor(cursor_factory=psycopg2_extras.DictCursor)
with open('static/others.png', 'rb') as r:
    image = r.read()
    cur.execute('insert into "gb_product_category"("name", "pictureBlob", "examples") values (%s,%s,%s)', (
        "Others",
        bytes(image),
        '{"1-1 services", "Delivery"}'
    ))
with open('static/education.png', 'rb') as r:
    image = r.read()
    cur.execute('insert into "gb_product_category"("name", "pictureBlob", "examples") values (%s,%s,%s)', (
        "Education",
        bytes(image),
        '{"Korean language", "Programming languages"}'
    ))
with open('static/consulting.png', 'rb') as r:
    image = r.read()
    cur.execute('insert into "gb_product_category"("name", "pictureBlob", "examples") values (%s,%s,%s)', (
        "Consultation",
        bytes(image),
        '{"Legal matters", "Acquiring visa"}'
    ))
with open('static/vacancies.png', 'rb') as r:
    image = r.read()
    cur.execute('insert into "gb_product_category"("name", "pictureBlob", "examples") values (%s,%s,%s)', (
        "Vacancies",
        bytes(image),
        '{"Assistant chef", "Software engineer", "Help desk support"}'
    ))
cur.close()

db_conn.commit()
db_conn.close()
