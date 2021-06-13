from firebase_admin.auth import InvalidIdTokenError, ExpiredIdTokenError, RevokedIdTokenError, CertificateFetchError
from google.auth.transport import requests as oauth_requests
from google.oauth2 import id_token as oauth_id_token
from firebase_admin import auth
from tools import settings
import requests
import hashlib
import time


def get_timestamp_ms():
    return int(round(time.time() * 1000))


def load_google_profile(id_token):
    google_id_details = oauth_id_token.verify_oauth2_token(id_token=id_token, request=oauth_requests.Request())
    if google_id_details['iss'] in ['accounts.google.com', 'https://accounts.google.com']:
        return {
            'name': google_id_details['name'],
            'email': google_id_details['email'],
            'picture': google_id_details['picture'],
        }
    else:
        print('google auth failure, wrong issuer')
    return None


def load_apple_profile(token):
    try:
        name = '[fullName]'
        if ',' in token:
            token, name = token.split(',')
        apple_profile = auth.verify_id_token(id_token=token)
        return {
            'name': name,
            'email': apple_profile['email'],
            'picture': 'http://54.180.83.68/static/appleProfileImage.png',
        }
    except (ValueError, InvalidIdTokenError, ExpiredIdTokenError, RevokedIdTokenError, CertificateFetchError):
        print('apple auth failure')
    return None


def load_picture_bytes(picture):
    res = requests.get(picture)
    if res.status_code == 200:
        return res.content
    return None


def now_ms():
    return int(time.time() * 1000)


def now_us():
    return int(time.time() * 1000 * 1000)


def md5(value):
    return hashlib.md5(value.encode()).hexdigest()


def get_currency_str(currency):
    return settings.currency_enum2str_map[currency]


def get_currency_enum(currency_str):
    return settings.currency_str2enum_map[currency_str]


def get_product_type_str(product_type):
    return settings.product_type_enum2str_map[product_type]


def get_product_type_enum(product_type_str):
    return settings.product_type_str2enum_map[product_type_str]
