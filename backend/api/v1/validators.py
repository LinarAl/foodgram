from django.conf import settings
from django.core.exceptions import ValidationError


def validator_forbidden_name(username):
    """Сверяет имя пользователя со списком запрещенных имен."""
    if username.lower() in settings.FORBIDDEN_USERNAMES:
        raise ValidationError(
            f'Имя пользователя {username} запрещено')
