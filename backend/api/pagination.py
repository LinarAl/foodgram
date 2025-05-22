"""Пагинация API."""
from rest_framework.pagination import LimitOffsetPagination

from foodgram_backend.constants import DEFAULT_PAGE_SIZE


class BaseLimitOffsetPagination(LimitOffsetPagination):
    """Базовый класс пагинации."""

    default_limit = DEFAULT_PAGE_SIZE
