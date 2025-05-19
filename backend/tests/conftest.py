import pytest


@pytest.fixture
def user_data():
    """Данные для создания пользователя."""
    return {
        'email': 'testuser@yamdb.fake',
        'username': 'TestUser',
        'first_name': 'User Firstname',
        'last_name': 'User Lastname',
        'password': 'jefF2hd23D2!'
    }


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(
        email='user@yamdb.fake',
        username='User',
        first_name='User Firstname',
        last_name='User Lastname',
        password='jefF2hd23D2!'
    )
