from datetime import datetime
from requests.auth import AuthBase
from os import environ as ENV
import jwt
import requests

BASE_URL = 'https://api.github.com'

def now_seconds():
    return int(datetime.now().timestamp())

def token_is_valid(expiration):
    if expiration:
        return now_seconds() < expiration
    return False

class InstallAuth(AuthBase):

    TOKEN = None
    EXPIRATION = None

    def __init__(self, installation_id):
        self.installation_id = installation_id

    def __call__(self, r):
        r.headers['Authorization'] = f'token {self.token}'
        return r

    @property
    def token(self):
        if token_is_valid(InstallAuth.EXPIRATION):
            return InstallAuth.TOKEN
        endpoint = f'{BASE_URL}/app/installations/{self.installation_id}/access_tokens'
        response = requests.request(
            method='POST',
            auth=JWTAuth(),
            url=endpoint
        )
        response.raise_for_status()
        data = response.json()
        InstallAuth.TOKEN = data.get('token')
        InstallAuth.EXPIRATION = int(datetime.strptime(data.get('expires_at'),'%Y-%m-%dT%H:%M:%SZ').timestamp()) - 10
        return InstallAuth.TOKEN
        
        

class JWTAuth(AuthBase):
    """
    Authenticating as a GitHub App
    """

    ALGORITHM = 'RS256'
    TOKEN = None
    EXPIRATION = None

    def __init__(self, application_id=None, pem_file=None, private_key=None):
        self.__application_id = application_id or ENV.get('GH_APPLICATION_ID') 
        self.__pem_file = pem_file or ENV.get('GH_PEM_FILE')
        try:
            with open(self.__pem_file, 'rb') as pem_file:
                self.__private_key = private_key or pem_file.read()
        except FileNotFoundError:
            print("Error! Check if path to pem file is correct.")

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r

    @property
    def token(self):
        if token_is_valid(JWTAuth.EXPIRATION):
            return JWTAuth.TOKEN
        now = now_seconds()
        payload = {
            'iat': now - 60,
            'exp': now + (10 * 60),
            'iss': self.__application_id
        }
        encoded_jwt = jwt.encode(payload, self.__private_key, algorithm=JWTAuth.ALGORITHM)
        JWTAuth.EXPIRATION = payload.get('exp')
        JWTAuth.TOKEN = encoded_jwt
        return JWTAuth.TOKEN
