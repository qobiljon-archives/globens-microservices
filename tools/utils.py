from google.auth.transport import requests as oauth_requests
from google.oauth2 import id_token as oauth_id_token
import requests
import hashlib
import time
import json


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

    print('google auth failure, wrong issuer')
    return None


def load_facebook_profile(access_token):
    req = requests.request(method='GET', url='https://graph.facebook.com/v2.12/me?fields=name,first_name,last_name,picture,email&access_token=' + access_token)
    print(req.status_code, access_token)
    if req.status_code == 200:
        user = json.loads(s=req.text)
        return {
            'name': user["name"],
            'email': user["email"],
            'picture': user["picture"]["data"]["url"],
        }

    print(f'facebook auth failure, status_code={req.status_code}')
    return None


def now_ms():
    return int(time.time() * 1000)


def now_us():
    return int(time.time() * 1000 * 1000)


def md5(value):
    return hashlib.md5(value.encode()).hexdigest()
