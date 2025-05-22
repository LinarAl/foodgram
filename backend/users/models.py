from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.validators import validator_forbidden_name
from foodgram_backend.constants import (FIRST_NAME_FIELD_LENGTH,
                                        LAST_NAME_FIELD_LENGTH,
                                        USERNAME_FIELD_LENGTH)


class User(AbstractUser):
    """Расширенная модель пользователя."""

    username = models.CharField(
        max_length=USERNAME_FIELD_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validator_forbidden_name
        ],
        verbose_name=_('Никнейм пользователя')
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_('Адрес электронной почты')
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_FIELD_LENGTH,
        verbose_name=_('Имя пользователя')
    )
    last_name = models.CharField(
        max_length=LAST_NAME_FIELD_LENGTH,
        verbose_name=_('Фамилия пользователя')
    )
    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default='',
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


class Subscription(models.Model):
    """Модель подписок."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Подписчик'),
        related_name='subscriber'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('Пользователь')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'user'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('user')),
                name='unique_subscriber'
            )
        ]
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user}'
