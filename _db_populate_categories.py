from tools import settings
import psycopg2
import psycopg2.extras as psycopg2_extras
import json

db_conn = psycopg2.connect(
    host=settings.db_settings['host'],
    database=settings.db_settings['database'],
    user=settings.db_settings['user'],
    password=settings.db_settings['password']
)

cur = db_conn.cursor(cursor_factory=psycopg2_extras.DictCursor)
with open('static/others.png', 'rb') as r:
    image = r.read()
    cur.execute('insert into "gb_product_category"("name", "pictureBlob", "examples") values (%s,%s,%s)', (
        json.dumps({'en': 'Others', 'ru': 'Прочие', 'uz': 'Boshqalar', 'kr': '기타'}),
        bytes(image),
        json.dumps({'en': ["1-1 services", "Delivery"], 'ru': ['', ''], 'uz': ['', ''], 'kr': ['1-1 서비스', '배달']})
    ))
with open('static/education.png', 'rb') as r:
    image = r.read()
    cur.execute('insert into "gb_product_category"("name", "pictureBlob", "examples") values (%s,%s,%s)', (
        json.dumps({'en': 'Education', 'ru': 'Обучение', 'uz': "Ta'lim", 'kr': '교육'}),
        bytes(image),
        json.dumps({'en': ["Korean language", "Programming languages"], 'ru': ['Корейский язык', 'Языки программирования'], 'uz': ['Koreys tili', 'Dasturlash tillari'], 'kr': ['한국어', '개발 언어']})
    ))
with open('static/consulting.png', 'rb') as r:
    image = r.read()
    cur.execute('insert into "gb_product_category"("name", "pictureBlob", "examples") values (%s,%s,%s)', (
        json.dumps({'en': 'Consultation', 'ru': 'Консультации', 'uz': 'Konsultatsiyalar', 'kr': '상담'}),
        bytes(image),
        json.dumps({'en': ["Legal matters", "Acquiring visa"], 'ru': ['Легальные вопросы', 'Получение визы'], 'uz': ['Legal savollar', 'Viza olish'], 'kr': ['법률사항', '비자']})
    ))
with open('static/vacancies.png', 'rb') as r:
    image = r.read()
    cur.execute('insert into "gb_product_category"("name", "pictureBlob", "examples") values (%s,%s,%s)', (
        json.dumps({'en': 'Vacancies', 'ru': 'Ваканции', 'uz': 'Vakansiyalar', 'kr': '결원'}),
        bytes(image),
        json.dumps({'en': ['Assistant chef', 'Software engineer', 'Help desk support'], 'ru': ['Помощник повара', 'Инженер программист', 'Служба поддержки'], 'uz': ['Oshpaz yordamchisi', 'Dasturiy muhandis', "Qo'llab-quvvatlash hizmati"], 'kr': ['주방장 보조', '소프트웨어 엔지니어', '헬프 데스크 지원']})
    ))
with open('static/food.png', 'rb') as r:
    image = r.read()
    cur.execute('insert into "gb_product_category"("name", "pictureBlob", "examples") values (%s,%s,%s)', (
        json.dumps({'en': 'Food', 'ru': 'Еда', 'uz': 'Oziq-ovqat', 'kr': '음식'}),
        bytes(image),
        json.dumps({'en': ['Restaurants', 'Cafe'], 'ru': ['Рестораны', 'Кафе'], 'uz': ['Restoranlar', 'Kafe'], 'kr': ['레스토랑', '커피점']})
    ))
cur.close()

db_conn.commit()
db_conn.close()
