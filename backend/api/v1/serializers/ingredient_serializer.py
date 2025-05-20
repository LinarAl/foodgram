"""Сериализатор ингридиента."""
from recipes.models import Ingredient
from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient
