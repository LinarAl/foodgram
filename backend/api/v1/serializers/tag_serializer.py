"""Сериализатор тега."""
from recipes.models import Tag
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag
