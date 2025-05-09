from api.v1.validators import validator_forbidden_name
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Расширенная модель пользователя."""

    username = models.CharField(
        max_length=settings.USERNAME_FIELD_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validator_forbidden_name
        ],
        verbose_name=_('Никнейм пользователя')
    )
    email = models.EmailField(
        unique=True,
        # error_messages={
        #     'unique': 'Данный адрес уже используется'
        # },
        verbose_name=_('Адрес электронной почты')
    )

    first_name = models.CharField(
        max_length=settings.FIRST_NAME_FIELD_LENGTH,
        verbose_name=_('Имя пользователя')
    )

    last_name = models.CharField(
        max_length=settings.LAST_NAME_FIELD_LENGTH,
        verbose_name=_('Фамилия пользователя')
    )

    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default=None,
        verbose_name=_('Аватар пользователя')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ('username',)

    def __str__(self):
        return self.username
