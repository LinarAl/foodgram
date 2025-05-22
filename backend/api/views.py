"""Вьюсеты."""
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .pagination import BaseLimitOffsetPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, FavoritesSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          SubscriptionCreateSerializer, SubscriptionSerializer,
                          TagSerializer)

User = get_user_model()


class UsersViewSet(UserViewSet):
    """ViewSet для модели Users."""

    queryset = User.objects.all()
    pagination_class = BaseLimitOffsetPagination
    http_method_names = ('get', 'post', 'put', 'delete')
    permission_classes = (IsAdminOrReadOnly, IsAuthorOrReadOnly)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'delete'],
            permission_classes=[IsAuthenticated], url_path='me/avatar')
    def avatar(self, request):
        """Action для добавления и удаления аватара пользователя."""
        user = get_object_or_404(User, username=request.user.username)

        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[IsAuthenticated])
    def subscribtions(self, request, *args, **kwargs):
        """Action для отображения подписок пользователя."""
        user = User.objects.filter(
            subscriptions__subscriber=request.user
        ).prefetch_related('recipes')
        page = self.paginate_queryset(user)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        """Action для подписки и отписки на пользователя."""
        user = self.get_object()
        if self.request.method == 'POST':
            serializer = SubscriptionCreateSerializer(
                data={'user': user.id, 'subscriber': request.user.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted, _ = Subscription.objects.filter(
            user=user,
            subscriber=request.user
        ).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Recipe"""
    queryset = (
        Recipe.objects
        .select_related('author')
        .prefetch_related('ingredients', 'tags')
    )
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = BaseLimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, *args, **kwargs):
        """Action для получения короткой ссылки."""
        host = request.get_host()
        link = self.get_object().link
        return Response(
            data={'short-link': f'http://{host}/s/{link}'},
            status=status.HTTP_200_OK
        )

    @staticmethod
    def create_delete_shopping_cart_favorites(
            request_method, current_serializer, current_model, recipe, user):
        """Метод добавления и удаления рецепта в списка покупок и избранное."""
        if request_method == 'POST':
            serializer = current_serializer(
                data={'recipe': recipe.id, 'user': user.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        current_model.objects.filter(
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart',
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        """Action для добавления и удаления рецепта в список покупок."""
        return self.create_delete_shopping_cart_favorites(
            request_method=self.request.method,
            current_serializer=ShoppingListSerializer,
            current_model=ShoppingList,
            recipe=self.get_object(),
            user=request.user
        )

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        """Action для скачивания списка покупок."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_list__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        content = "Список покупок:\n\n"
        count = 0
        for item in ingredients:
            count += 1
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['total_amount']
            content += f'{count}) {name} ({unit}): {amount}\n'

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_cart.txt"')
        return response

    @action(detail=True, methods=['post', 'delete'], url_path='favorite',
            permission_classes=[IsAuthenticated])
    def favorites(self, request, *args, **kwargs):
        """Action для добавления и удаления рецепта в избранное."""
        return self.create_delete_shopping_cart_favorites(
            request_method=self.request.method,
            current_serializer=FavoritesSerializer,
            current_model=Favorites,
            recipe=self.get_object(),
            user=request.user
        )


def recipe_redirect_view(request, short_link):
    """Редирект на рецепт по короткой ссылке."""
    recipe = get_object_or_404(Recipe, link=short_link)
    return redirect(f'/recipes/{recipe.id}')
