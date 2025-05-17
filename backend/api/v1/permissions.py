"""Модуль прав доступа для API."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthenticatedOrIsAuthorOrReadOnly(BasePermission):
    """Чтение для всех, Post метод для авторизованных пользователей, Patch и
    Delete методы только для авторов объектов."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
