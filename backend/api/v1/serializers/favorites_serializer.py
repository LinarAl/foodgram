"""Сериализатор для избранного."""
from recipes.models import Favorites
from rest_framework import serializers

from .recipe_serializer import ShortRecipeSerializer


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorites."""

    class Meta:
        fields = ('user', 'recipe')
        model = Favorites

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data
