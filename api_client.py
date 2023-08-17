#!/usr/bin/env python
from urllib.request import urlopen
from urllib.parse import quote_plus
import hmac
import json
import urllib.error
from functools import reduce
import sys
import warnings
from enum import Enum

class Method(Enum):
    GET = 'get'
    PUT = 'put'

class Controller(Enum):
    LOGS = 'LogsAPI'
    BADGES = 'BadgesAPI'
    USERS = 'UsersAPI'

class APIClient:
    def __init__(self) -> None:
        local_test = False
        if local_test:
            self.base_url = 'http://localhost:8080'
        else:
            self.base_url = 'https://timbreuse.sectioninformatique.ch'

    @staticmethod
    def load_key() -> str:
        with open('.key.json', 'r') as file:
            return json.load(file)['key']

    def create_token(self, date, badge_id, inside) -> str:
        text = f'{date}{badge_id}{inside}'.encode()
        key = self.load_key().encode()
        token_text = hmac.new(key, text, 'sha256').hexdigest()
        return token_text

    @staticmethod
    def create_url(base_url, method, arg) -> str:
        warnings.warn("use create_url_n", DeprecationWarning)
        return f'{base_url}/{method}/{arg}'

    def create_url_n(self, controller:str, method:str, arg:str) -> str:
        '''
        >>> api_client = APIClient()
        >>> api_client.create_url_n('Logs', 'put', '2/3/4')
        'http://localhost:8080/Logs/put/2/3/4'

        # 'https://timbreuse.sectioninformatique.net/Logs/put/2/3/4'
        '''
        # return f'{base_url}/{method}/{arg}'
        return (f'{self.base_url}/{controller}/'
        f'{method}/{arg}')

    def send(self, url) -> tuple:
        '''
        wrap function of urllib.request.urlopen
        '''
        print('send', file=sys.stderr)
        try:
            html_file = urlopen(url)
            #html_file = urlopen(url, timeout=1)
        #    # print(html_file.read())
        #    # print()
        #    # print(html_file.url)
        #    # print(html_file.status)
        #    # print(html_file.headers)
        #    # return html_file
            return html_file, html_file.status
        except urllib.error.HTTPError as e:
            return None, str(e)
        
    
    def send_log(self, date, badge_id, inside) -> tuple:
        '''
        >>> client_API = APIClient()
        >>> file, code = client_API.send_log(*fake_info_stamping())
        >>> type(file)
        <class 'http.client.HTTPResponse'>
        >>> code
        201
        '''
        print('APIClient.send_log', file=sys.stderr)
        arg = self.create_arg_args(date, badge_id, inside, self.create_token(
            date, badge_id, inside)
        )
        url = self.create_url_n(Controller.LOGS.value, Method.PUT.value, arg)
        print(url, file=sys.stderr)
        return self.send(url)

    def _receive_logs(self, log_id) -> list[dict]:
        '''
        deprecated
        receive all logs from the server
        # >>> api_client = APIClient()
        # >>> logs = api_client.receive_logs(413)
        # >>> type(logs)
        # <class 'list'>

        # >>> type(logs[0])
        # <class 'dict'>
        '''
        warnings.warn("deprecated", DeprecationWarning)
        print('_receive_logs', file=sys.stderr)
        print(log_id, file=sys.stderr)
        url = self.create_url_n(Controller.LOGS.value, Method.GET.value, 
            log_id)
        print(url, file=sys.stderr)
        html_file = self.send(url)[0]
        
        return json.loads(html_file.readline())

    def receive_logs(self, start_date) -> list[dict]:
        '''
        receive all logs since the date in parameter from the server
        >>> api_client = APIClient()
        >>> logs = api_client.receive_logs("2022-12-12 00:00:00")
        '''
        print('receive_logs', file=sys.stderr)
        print(start_date, file=sys.stderr)
        token = self.create_token_args(start_date)
        arg = self.create_arg_args(start_date, token)
        url = self.create_url_n(Controller.LOGS.value, Method.GET.value, arg)
        print(url, file=sys.stderr)
        html_file = self.send(url)[0]
        
        return json.loads(html_file.readline())

    def send_badge_and_user(self, badge_id:int, name:str, surname:str):
        '''
        >>> api_client = APIClient()
        >>> file, code = api_client.send_badge_and_user(44, 'John', 'Malc')
        >>> type(file)
        <class 'http.client.HTTPResponse'>
        >>> code
        201
        '''
        print('APIClient.send_badge_and_user', file=sys.stderr)
        arg = self.create_arg_args(badge_id, name, surname,
            self.create_token_args(badge_id, name, surname))
        url = self.create_url_n(Controller.BADGES.value, Method.PUT.value, arg)
        print(url, file=sys.stderr)
        return self.send(url)

    def receive_users_and_badges(self, user_id) -> list[dict]:
        '''
        deprecated
        # receive all users and badges from the server
        #  >>> api_client = APIClient()
        #  >>> logs = api_client.receive_users_and_badges(97)
        #  >>> type(logs)
        #  <class 'list'>
        #  >>> type(logs[0])
        #  <class 'dict'>
        '''
        print('receive_users_and_badges', file=sys.stderr)
        warnings.warn("use create_arg_args", DeprecationWarning)
        print(user_id, file=sys.stderr)
        url = self.create_url_n(Controller.BADGES.value, Method.GET.value,
            user_id)
        print(url, file=sys.stderr)
        html_file = self.send(url)[0]
        return json.loads(html_file.readline())

    def receive_users(self, start_date) -> list[dict]:
        '''
        receive all users from the server
        >>> api_client = APIClient()
        >>> users = api_client.receive_users('2023-02-03 00:00:00')
        >>> isinstance(users, list)
        True
        '''
        print('receive_users', file=sys.stderr)
        token = self.create_token_args(start_date)
        arg = self.create_arg_args(start_date, token)
        url = self.create_url_n(Controller.USERS.value, Method.GET.value, arg)
        print(url, file=sys.stderr)
        html_file = self.send(url)[0]
        return json.loads(html_file.readline())

    def receive_badges(self, start_date):
        '''
        receive all badges from the server
        >>> api_client = APIClient()
        >>> badges = api_client.receive_badges('2023-02-03 00:00:00')
        >>> isinstance(badges, list)
        True
        '''
        print('receive_badges', file=sys.stderr)
        print('start_date', start_date, file=sys.stderr)
        token = self.create_token_args(start_date)
        arg = self.create_arg_args(start_date, token)
        url = self.create_url_n(Controller.BADGES.value, Method.GET.value, arg)
        print(url, file=sys.stderr)
        html_file = self.send(url)[0]
        return json.loads(html_file.readline())


    @staticmethod
    def create_arg_args(*args) -> str:
        '''
        >>> APIClient.create_arg_args('a', 'b', 'c')
        'a/b/c'
        '''
        print('create_arg_args', file=sys.stderr)
        text = reduce(lambda cumulator, word:f'{cumulator}/{word}', args)
        return quote_plus(text, '/')

    @classmethod
    def create_token_args(cls, *args) -> str:
        '''
        >>> badge_id, name, surname = 1, 'Sam', 'Smith'
        >>> api_client = APIClient()
        >>> api_client.create_token_args(badge_id, name, surname)
        '1d0e1bc7fb9d9588833c427aa27b3d5edd20725cdee071e8c3f60d6009761e57'
        '''
        text = reduce(lambda cumulator,
                      word: f'{cumulator}{word}', args)

        # is necessary args is one arg
        text = str(text)

        print(type(text), text, file=sys.stderr)
        text = text.encode()
        print(type(text), text, file=sys.stderr)
        key = cls.load_key().encode()
        token_text = hmac.new(key, text, 'sha256').hexdigest()
        return token_text
    

def fake_info_stamping() -> tuple:
    import datetime
    date = datetime.datetime.now()
    badge_id = 42
    inside = 1
    inside = 1 if bool(inside) else 0
    return date, badge_id, inside

def main():
    test = 0
    if test == 0:
        import doctest
        doctest.testmod()
    elif test == 1:
        pass

if __name__ == "__main__":
    main()
