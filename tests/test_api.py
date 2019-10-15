import unittest
from base64 import b64encode
from peewee import SqliteDatabase
from app import app
from app.models import User

MODELS = [User]
test_db = SqliteDatabase(':memory:')


class ApiServiceTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = False
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)
        self.app = app.test_client()

    def tearDown(self):
        test_db.drop_tables(MODELS)
        test_db.close()

    @staticmethod
    def create_user(data=None, confirm=True):
        if not data:
            data = {
                'username': 'test',
                'password': 'test',
                'email': 'test@gg.com'
            }

        user = User()
        user.create_user(data)
        if confirm:
            user.confirmed = True
        user.save()
        return user

    def test_valid_add_user(self):
        """ Тест верного добавления пользователя. """

        resp = self.app.post('/api/users/', json={
            'username': 'test_add',
            'password': 'test_add',
            'email': 'test_add@gg.com',
            'birthday': '20.09.2000'
        })

        self.assertEqual(resp.status_code, 200, f'status_code == {resp.status_code}')
        self.assertTrue(User.get_or_none(User.username == 'test_add'), 'User not added.')
        self.assertTrue(User.get_or_none(User.email == 'test_add@gg.com'), 'User not added.')

    def test_invalid_add_user(self):
        """ Тест неверного добавления пользователя. """

        self.create_user(data={
            'username': 'unique',
            'password': 'test_add',
            'email': 'unique@gg.com'
        })

        params = [{
            'username': 'test_add',
            'password': 'test_add'
        }, {
            'username': 'test_add',
            'email': 'test_add@gg.com'
        }, {
            'email': 'test_add@gg.com',
            'password': 'test_add'
        }, {
            'username': 'test_add'
        }, {
            'username': 'unique',
            'password': 'test_add',
            'email': 'test_add@gg.com'
        }, {
            'username': 'test_add',
            'password': 'test_add',
            'email': 'unique@gg.com'
        }, {}]

        # Добавление с отсутсвием необходимых параметров или повторным использованием уникальных.
        for json in params:
            resp = self.app.post('/api/users/', json=json)

            if 'username' in json and json['username'] == 'unique':
                self.assertEqual(resp.status_code, 409, f'status_code == {resp.status_code}')
                self.assertEqual(resp.json['code'], 1008, f'code == {resp.json["code"]}')
            elif 'email' in json and json['email'] == 'unique@gg.com':
                self.assertEqual(resp.status_code, 409, f'status_code == {resp.status_code}')
                self.assertEqual(resp.json['code'], 1009, f'code == {resp.json["code"]}')
            else:
                self.assertEqual(resp.status_code, 400, f'status_code == {resp.status_code}')
                self.assertEqual(resp.json['code'], 1007, f'code == {resp.json["code"]}')

    def test_account_verification(self):
        """ Тест подтверждения email. """

        user = self.create_user(confirm=False)
        valid_url = f'/api/confirm/{user.generate_confirmation_token()}'

        test_u = User()
        test_u.email = 'invalid_email'
        invalid_urls = [
            valid_url + '0',
            '/api/confirm/' + test_u.generate_confirmation_token()
        ]

        # Передача неверного токена
        for invalid_url in invalid_urls:
            resp = self.app.get(invalid_url)

            self.assertEqual(resp.status_code, 400, f'status_code == {resp.status_code}')
            self.assertEqual(resp.json['code'], 1001, f'code == {resp.json["code"]}')

        # Передача верного токена впервые.
        resp = self.app.get(valid_url)

        self.assertEqual(resp.status_code, 200, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['message'], 'Email confirmed.', f'message == {resp.json["message"]}')

        # Передача верного токена повторно.
        resp = self.app.get(valid_url)

        self.assertEqual(resp.status_code, 400, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1000, f'code == {resp.json["code"]}')

    def test_not_confirmed_email(self):
        """ Проверка на выдачу токена только для подтвержденного пользователя. """

        user = self.create_user(data={
            'username': 'test_conf',
            'password': 'test_conf',
            'email': 'test_conf@gg.com'
        }, confirm=False)

        resp = self.app.post('/api/token', headers={
            'Authorization': b"Basic " + b64encode("test_conf:test_conf".encode())
        })
        self.assertEqual(resp.status_code, 400, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1003, f'code == {resp.json["code"]}')

        user.confirmed = True
        user.save()

        resp = self.app.post('/api/token', headers={
            'Authorization': b"Basic " + b64encode("test_conf:test_conf".encode())
        })
        self.assertEqual(resp.status_code, 200, f'status_code == {resp.status_code}')

    def test_authorization_request(self):
        """ Тест запроса на получение токена. """

        self.create_user(data={
            'username': 'test_auth',
            'password': 'test_auth',
            'email': 'test_auth@gg.com'
        })

        invalid_params = [{
            'username': 'test_auth',
            'password': 'invalid_test_auth'
        }, {
            'username': 'invalid_test_auth',
            'password': 'test_auth'
        }, {
            'username': 'test_auth',
            'password': ''
        }, {
            'username': '',
            'password': 'test_auth'
        }]

        # Передача неверного имени пользователя/пароля
        for param in invalid_params:
            resp = self.app.post('/api/token', headers={
                'Authorization': b"Basic " + b64encode(f"{param['username']}:{param['password']}".encode())
            })
            self.assertEqual(resp.status_code, 400, f'status_code == {resp.status_code}')
            self.assertEqual(resp.json['code'], 1004, f'code == {resp.json["code"]}')

        # Передача верного имени пользователя
        resp = self.app.post('/api/token', headers={
            'Authorization': b"Basic " + b64encode("test_auth:test_auth".encode())
        })
        self.assertEqual(resp.status_code, 200, f'status_code == {resp.status_code}')
        self.assertTrue(resp.json['token'])

    def test_delete_token(self):
        """ Удаляет токен. """

        user = self.create_user()
        token = user.get_token()

        resp = self.app.delete('/api/token', headers={
            'Authorization': f"Bearer {token}"
        })
        self.assertEqual(resp.status_code, 204, f'status_code == {resp.status_code}')

        resp = self.app.get('/api/users/', headers={
            'Authorization': f"Bearer {token}"
        })
        self.assertEqual(resp.status_code, 401, f'status_code == {resp.status_code}')

    def test_invalid_token(self):
        """ Пробует получить список пользователей без токена. """

        resp = self.app.get('/api/users/')

        self.assertEqual(resp.status_code, 401, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1002, f'code == {resp.json["code"]}')
        self.assertEqual(resp.json['message'], 'Invalid token.', f'message == {resp.json["message"]}')

    def test_get_users_id(self):
        """ Запрос на информацию о себе. """

        ids = []
        tokens = []

        for i in range(0, 2):
            user = self.create_user(data={
                'username': f'user{i}',
                'password': f'user{i}',
                'email': f'user{i}@gg.com'
            })
            tokens.append(user.get_token())
            ids.append(user.get_id())

        # invalid requests
        resp = self.app.get(f'/api/users/{ids[0]}', headers={
            'Authorization': "Bearer invalid_token"
        })
        self.assertEqual(resp.status_code, 401, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1002, f'code == {resp.json["code"]}')

        resp = self.app.get(f'/api/users/{ids[1]}', headers={
            'Authorization': f"Bearer {tokens[0]}"
        })
        self.assertEqual(resp.status_code, 403, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1005, f'code == {resp.json["code"]}')

        resp = self.app.get(f'/api/users/{ids[0] + ids[1]}', headers={
            'Authorization': f"Bearer {tokens[0]}"
        })
        self.assertEqual(resp.status_code, 404, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1006, f'code == {resp.json["code"]}')

        # valid request
        resp = self.app.get(f'/api/users/{ids[0]}', headers={
             'Authorization': f"Bearer {tokens[0]}"
        })
        self.assertEqual(resp.status_code, 200, f'status_code == {resp.status_code}')
        for param in ['email', 'id', 'username', 'birthday', 'confirmed']:
            self.assertIn(param, resp.json, f'{param} not included.')
        self.assertNotIn('password_hash', resp.json, 'password_hash include.')

    def test_get_users(self):
        """ Запрос на список пользователей. """

        user = self.create_user()
        token = user.get_token()

        # invalid request
        resp = self.app.get(f'/api/users/', headers={
            'Authorization': "Bearer invalid_token"
        })
        self.assertEqual(resp.status_code, 401, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1002, f'code == {resp.json["code"]}')

        # valid request
        resp = self.app.get('/api/users/', headers={
            'Authorization': f'Bearer {token}'
        })
        data_resp = resp.json['users'][0]

        self.assertEqual(resp.status_code, 200, f'status_code == {resp.status_code}')
        for param in ['id', 'username', 'email', 'confirmed']:  #todo 'birthday',
            self.assertIn(param, data_resp, f'{param} not included.')
        for param in ['password_hash']:
            self.assertNotIn(param, data_resp, f'{param} include.')

    def test_put_users_id(self):
        """ Запрос изменения пользователя. """

        ids = []
        tokens = []

        for i in range(0, 2):
            user = self.create_user(data={
                'username': f'user{i}',
                'password': f'user{i}',
                'email': f'user{i}@gg.com'
            })
            tokens.append(user.get_token())
            ids.append(user.get_id())

        # invalid request - неверный токен
        resp = self.app.put(f'/api/users/{ids[0]}', headers={
            'Authorization': "Bearer invalid_token"
        })
        self.assertEqual(resp.status_code, 401, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1002, f'code == {resp.json["code"]}')

        # invalid request - изменение чужого профиля
        resp = self.app.put(f'/api/users/{ids[1]}', headers={
            'Authorization': f"Bearer {tokens[0]}"
        })
        self.assertEqual(resp.status_code, 403, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1005, f'code == {resp.json["code"]}')

        # invalid request - измененние несуществуещего профиля
        resp = self.app.put(f'/api/users/{ids[0] + ids[1]}', headers={
            'Authorization': f"Bearer {tokens[0]}"
        })
        self.assertEqual(resp.status_code, 404, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1006, f'code == {resp.json["code"]}')

        # invalid request - изменение на уже использовавшийся username
        resp = self.app.put(f'/api/users/{ids[0]}', headers={
            'Authorization': f"Bearer {tokens[0]}"
        }, json={
            'username': 'user1'
        })
        self.assertEqual(resp.status_code, 409, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1008, f'code == {resp.json["code"]}')

        # invalid request - изменение на уже использовавшийся email
        resp = self.app.put(f'/api/users/{ids[0]}', headers={
            'Authorization': f"Bearer {tokens[0]}"
        }, json={
            'email': 'user1@gg.com'
        })
        self.assertEqual(resp.status_code, 409, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['code'], 1009, f'code == {resp.json["code"]}')

        # valid request
        resp = self.app.put(f'/api/users/{ids[0]}', headers={
            'Authorization': f"Bearer {tokens[0]}"
        }, json={
            'username': 'test_put',
            'email': 'test_put@gg.com',
            'birthday': '20.09.2000'
        })

        self.assertEqual(resp.status_code, 200, f'status_code == {resp.status_code}')
        self.assertEqual(resp.json['username'], 'test_put', resp.json['username'])
        self.assertEqual(resp.json['email'], 'test_put@gg.com', resp.json['email'])

        for param in ['email', 'id', 'username', 'birthday', 'confirmed']:
            self.assertIn(param, resp.json, f'{param} not included.')
        self.assertNotIn('password_hash', resp.json, 'password_hash include.')


if __name__ == '__main__':
    unittest.main()
