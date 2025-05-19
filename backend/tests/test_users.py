from http import HTTPStatus

import pytest


@pytest.mark.django_db(transaction=True)
class TestUserAPI:
    USERS_URL = '/api/users/'
    USERS_ME_URL = '/api/users/me/'
    USER_PUT_DEL_AVATAR = '/api/users/me/avatar/'
    USUER_SET_PASSWORD = '/api/users/set_password/'
    TOKEN_LOGIN = '/api/auth/token/login/'
    TOKEN_DELETE = '/api/auth/token/logout/'

    def test_create_user(self, client, user_data):
        """Создание пользователя и получение токена."""
        response = client.post(self.USERS_URL, data=user_data)
        assert response.status_code == HTTPStatus.CREATED
        assert response.data['email'] == user_data['email']

        response = client.post(
            self.TOKEN_LOGIN,
            data={
                'email': user_data['email'],
                'password': user_data['password']
            }
        )
        assert response.status_code == HTTPStatus.OK

    def test_create_user_invalid_data(self, client):
        """Создание пользователя с неверными данными."""
        response = client.post(self.USERS_URL, data={})
        assert response.status_code == HTTPStatus.BAD_REQUEST
