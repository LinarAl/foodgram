from django.db.models import Case, IntegerField, Q, Value, When
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    """Фильтрация рецепта по автору, тегам и ингредиентам."""

    author_id = rest_framework.NumberFilter(
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
    is_favorited = rest_framework.BooleanFilter(
        method='filter_is_favorited',
        label=_('В избранном'),
        help_text=_('Показыать рецепты которые находятся в вашем списке '
                    'избоанного'))
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label=_('В списке покупок'),
        help_text=_('Показыать рецепты которые находятся в вашем списке '
                    'покупок'))

    class Meta:
        model = Recipe
        fields = (
            'is_favorited', 'is_in_shopping_cart', 'author_id', 'tags',
            'ingredients')

    def filter_ingredients_icontains(self, queryset, name, value):
        return queryset.filter(ingredients__name__icontains=value)

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user.id)
        return queryset.none()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user.id)
        return queryset.none()


class IngredientFilter(rest_framework.FilterSet):
    """Фильрация ингредиентов по вхождению в начало названия и по вхождению в
    произвольном месте"""

    name = rest_framework.CharFilter(
        method='filter_name_istartswith_icontains')

    def filter_name_istartswith_icontains(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            match_priority=Case(
                When(name__istartswith=value, then=Value(1)),
                When(name__icontains=value, then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
        ).order_by('match_priority', 'name')

    class Meta:
        model = Ingredient
        fields = (
            'name',
        )
