from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


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
        current_url = request.build_absolute_uri().split('/api')[0]
        link = self.get_object().link
        return Response(
            data={'get-link': f'{current_url}/{link}'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart',
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        """Action для добавления и удаления рецепта в список покупок."""
        if self.request.method == 'POST':
            serializer = ShoppingListSerializer(
                data={'recipe': self.get_object().id, 'user': request.user.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            deleted, _ = ShoppingList.objects.filter(
                user=request.user,
                recipe=self.get_object()
            ).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

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
        if self.request.method == 'POST':
            serializer = FavoritesSerializer(
                data={'recipe': self.get_object().id, 'user': request.user.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            deleted, _ = Favorites.objects.filter(
                user=request.user,
                recipe=self.get_object()
            ).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def recipe_redirect_view(request, short_link):
    """Редирект на рецепт по короткой ссылке."""
    recipe = get_object_or_404(Recipe, link=short_link)
    return redirect(f'/api/recipes/{recipe.id}')


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class UsersViewSet(UserViewSet):
    """ViewSet для модели Users."""

    queryset = User.objects.all()
    pagination_class = BaseLimitOffsetPagination
    http_method_names = ('get', 'post', 'put', 'delete')
    permission_classes = (IsAdminOrReadOnly, IsAuthorOrReadOnly)

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
        elif request.method == 'DELETE' and user.avatar:
            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[IsAuthenticated])
    def subscribtions(self, request, *args, **kwargs):
        """Action для отображения подписок пользователя."""
        user = User.objects.filter(
            subscriber__user=request.user
        ).prefetch_related('recipes')
        print(user)
        page = self.paginate_queryset(user)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        """Action для подписки и отписки на пользователя."""
        user = self.get_object()
        print(user)
        if self.request.method == 'POST':
            serializer = SubscriptionCreateSerializer(
                data={'user': user.id, 'subscriber': request.user.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            deleted, _ = Subscription.objects.filter(
                user=user,
                subscriber=request.user
            ).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
