"""Вьюсет ингридиента."""
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient
from rest_framework import viewsets

from ..filters import IngredientFilter
from ..serializers.ingredient_serializer import IngredientSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
