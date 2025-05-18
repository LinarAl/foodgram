"""Модуль прав доступа для API."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """К запросам PUT, PATCH, DELETE допускается только автор и админ."""

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_staff))


class IsAuthorOrReadOnly(BasePermission):
    """К запросам PUT, PATCH, DELETE допускается только автор."""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
