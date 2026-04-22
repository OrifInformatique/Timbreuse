#!/usr/bin/env python
from urllib.request import urlopen
from urllib.parse import quote_plus
import hmac
import json
import urllib.error
import os
from functools import reduce
import sys
from enum import Enum

class Method(Enum):
    GET = 'get'
    PUT = 'put'

class Controller(Enum):
    LOGS = 'LogsAPI'
    BADGES = 'BadgesAPI'
    USERS = 'UsersAPI'
    EVENT_LOGS = 'EventLogsAPI'

class APIClient:
    def __init__(self) -> None:
        self.base_url = os.getenv(
            'TIMBREUSE_API_BASE_URL',
            'https://timbreuse.sectioninformatique.ch'
        ).rstrip('/')

    @staticmethod
    def load_key() -> str:
        key_path = os.getenv('TIMBREUSE_API_KEY_FILE', '.key.json')
        with open(key_path, 'r', encoding='utf-8') as file:
            return json.load(file)['key']

    def create_token(self, date, badge_id, inside) -> str:
        text = f'{date}{badge_id}{inside}'.encode()
        key = self.load_key().encode()
        token_text = hmac.new(key, text, 'sha256').hexdigest()
        return token_text

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
            return html_file, html_file.status
        except urllib.error.HTTPError as e:
            return None, str(e)
        except urllib.error.URLError as e:
            return None, str(e)

    @staticmethod
    def _decode_response_body(html_file) -> str:
        body = html_file.read()
        if isinstance(body, bytes):
            return body.decode('utf-8', errors='replace')
        return str(body)

    def _parse_json_response(self, html_file, url: str):
        body = self._decode_response_body(html_file).strip()
        if body == '':
            return []
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            # Certains endpoints peuvent prefixer la reponse par du bruit
            # (warning PHP, HTML, saut de ligne, etc.). On tente d'extraire
            # le premier JSON valide.
            decoder = json.JSONDecoder()
            for idx, ch in enumerate(body):
                if ch not in ('{', '['):
                    continue
                try:
                    parsed, _ = decoder.raw_decode(body[idx:])
                    return parsed
                except json.JSONDecodeError:
                    continue
            preview = body[:240].replace('\n', '\\n')
            raise ValueError(f"Reponse API non-JSON sur {url}. Apercu: {preview}")

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
        if html_file is None:
            return []
        return self._parse_json_response(html_file, url)

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
        if html_file is None:
            return []
        return self._parse_json_response(html_file, url)

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
        if html_file is None:
            return []
        return self._parse_json_response(html_file, url)

    def receive_event_logs(self, start_date) -> list[dict]:
        """
        Recupere les events serveur (ex: hard delete) depuis start_date.
        """
        print('receive_event_logs', file=sys.stderr)
        token = self.create_token_args(start_date)
        arg = self.create_arg_args(start_date, token)
        url = self.create_url_n(Controller.EVENT_LOGS.value, Method.GET.value, arg)
        print(url, file=sys.stderr)
        html_file = self.send(url)[0]
        if html_file is None:
            return []
        return self._parse_json_response(html_file, url)

    @staticmethod
    def is_not_deleted(remote_row: dict) -> bool:
        """
        Interprete le champ date_delete renvoye par l'API distante.
        """
        date_delete = remote_row.get('date_delete')
        if date_delete is None:
            return True
        if isinstance(date_delete, str):
            return date_delete.strip().lower() in ('', 'none', 'null')
        return False

    def remote_user_exists_for_badge(self, badge_id: int) -> bool:
        """
        Verifie en interrogeant l'API distante si le badge est encore
        attribue a un utilisateur actif.
        """
        try:
            start_date = '1900-01-01 00:00:00'
            users = self.receive_users(start_date)
            badges = self.receive_badges(start_date)
        except Exception as e:
            # En cas d'indisponibilite reseau/API, on n'interrompt pas le
            # pointage local.
            print('remote_user_exists_for_badge fallback:', e, file=sys.stderr)
            return True

        active_user_ids = set()
        for user in users:
            if self.is_not_deleted(user):
                active_user_ids.add(user.get('id_user'))

        for badge in badges:
            if badge.get('id_badge') != badge_id:
                continue
            if not self.is_not_deleted(badge):
                continue
            id_user = badge.get('id_user')
            if id_user is not None and id_user in active_user_ids:
                return True
        return False


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
