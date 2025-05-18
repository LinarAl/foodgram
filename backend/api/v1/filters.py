from django.db.models import Q
from django_filters import rest_framework
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    """Фильтрация рецепта по автору, тегам и ингредиентам."""

    author = rest_framework.CharFilter(
        field_name='author_id',
        lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    ingredients = rest_framework.CharFilter(
        method='filter_ingredients_icontains')
    # is_favorited = 
    # is_in_shopping_cart

    def filter_ingredients_icontains(self, queryset, name, value):
        return queryset.filter(ingredients__name__icontains=value)

    class Meta:
        model = Recipe
        fields = (
            'author', 'tags', 'ingredients'
        )


class IngredientFilter(rest_framework.FilterSet):
    """Фильрация ингредиентов по вхождению в начало названия и по вхождению в
    произвольном месте"""

    name = rest_framework.CharFilter(
        method='filter_name_istartswith_icontains')

    def filter_name_istartswith_icontains(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        )

    class Meta:
        model = Ingredient
        fields = (
            'name',
        )
