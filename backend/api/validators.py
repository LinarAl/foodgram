from django.core.exceptions import ValidationError
from rest_framework.serializers import \
    ValidationError as SerializersValidationError

from foodgram_backend.constants import FORBIDDEN_USERNAMES


def validator_forbidden_name(username):
    """Сверяет имя пользователя со списком запрещенных имен."""
    if username.lower() in FORBIDDEN_USERNAMES:
        raise ValidationError(
            f'Имя пользователя {username} запрещено')


def validate_unique_data(data: list, data_name='attr_name', key=None):
    """Валидация получаемых полей из POST и PATCH запросов.

    Если поле отсутствует или данные в поле не уникальны, то
    выводится ошибка serializers.ValidationError.

    data - список словарей, data_name - наименование валидируемого
    поля, key - ключ вложенного словаря."""
    if not data:
        raise SerializersValidationError(
            f'Поле {data_name} должно быть задано.')
    if key:
        data_id_lst = [element[key].id for element in data]
    else:
        data_id_lst = [element.id for element in data]
    unique_data_id_lst = set(data_id_lst)
    if len(data_id_lst) != len(unique_data_id_lst):
        raise SerializersValidationError(
            f'{data_name} должны быть уникальными.')
