from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from djoser.views import UserViewSet
from recipes.models import (Ingredient, Recipe, RecipeIngredient, ShoppingList,
                            Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .pagination import BaseLimitOffsetPagination
from .permissions import IsAuthenticatedOrIsAuthorOrReadOnly
from .serializers import (AvatarSerializer, CreateRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingListSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Recipe"""
    queryset = Recipe.objects.all()
    pagination_class = BaseLimitOffsetPagination
    permission_classes = (IsAuthenticatedOrIsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return CreateRecipeSerializer
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
            if not deleted:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

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


def recipe_redirect_view(request, short_link):
    """Редирект на рецепт по короткой ссылке."""
    recipe = get_object_or_404(Recipe, link=short_link)
    return redirect(f'/api/recipes/{recipe.id}')


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ('get',)


class UsersViewSet(UserViewSet):
    """ViewSet для модели Users."""

    queryset = User.objects.all()
    # serializer_class = UserSerializer
    # lookup_field = 'username'
    pagination_class = BaseLimitOffsetPagination
    # permission_classes = (IsAdminOnly,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)
    http_method_names = ('get', 'post', 'put', 'delete')

    @action(detail=False, methods=['put', 'delete'],
            permission_classes=[IsAuthenticated], url_path='me/avatar')
    def avatar(self, request):
        user = get_object_or_404(User, username=request.user.username)

        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.method == 'PUT':
            serializer.save()
        else:
            serializer.save(avatar=None)
        return Response(serializer.data, status=status.HTTP_200_OK)
