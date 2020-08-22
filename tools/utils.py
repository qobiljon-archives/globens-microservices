from google.auth.transport import requests as oauth_requests
from google.oauth2 import id_token as oauth_id_token
import time


def get_timestamp_ms():
    return int(round(time.time() * 1000))


def load_google_profile(id_token):
    google_id_details = oauth_id_token.verify_oauth2_token(id_token=id_token, request=oauth_requests.Request())
    if google_id_details['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        print('google auth failure, wrong issuer')
        return None
    print(google_id_details)
    return {
        'id_token': id_token,
        'name': google_id_details['name'],
        'email': google_id_details['email']
    }
