"""Пагинация API."""
from rest_framework.pagination import PageNumberPagination

from foodgram_backend.constants import (DEFAULT_PAGE_SIZE, PAGE_SIZE_MAX_LIMIT,
                                        PAGE_SIZE_PARAM, PAGE_SIZE_QUERY_PARAM)


class BaseLimitOffsetPagination(PageNumberPagination):
    """Базовый класс пагинации."""

    page_size = DEFAULT_PAGE_SIZE
    page_query_param = PAGE_SIZE_PARAM
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
    max_page_size = PAGE_SIZE_MAX_LIMIT
