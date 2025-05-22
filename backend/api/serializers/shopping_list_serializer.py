"""Сериализатор для списка покупок."""
from recipes.models import ShoppingList
from rest_framework import serializers

from .recipe_serializer import ShortRecipeSerializer


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingList."""

    class Meta:
        fields = ('user', 'recipe')
        model = ShoppingList

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data
