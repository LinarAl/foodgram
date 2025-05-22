"""Вьюсет тега."""
from django.contrib.auth import get_user_model
from recipes.models import Tag
from rest_framework import viewsets

from ..serializers.tag_serializer import TagSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
