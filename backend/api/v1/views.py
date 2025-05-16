from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from .pagination import BaseLimitOffsetPagination
from .serializers import (AvatarSerializer, CreateRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer)

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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateRecipeSerializer
        if self.request.method == 'PATCH':
            return CreateRecipeSerializer
        return RecipeSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, *args, **kwargs):
        current_url = request.build_absolute_uri().split('/api')[0]
        link = self.get_object().link
        return Response(
            data={'get-link': f'{current_url}/{link}'},
            status=status.HTTP_200_OK
        )


def recipe_redirect_view(request, short_link):
    """Редирект на рецепт короткой ссылке."""
    print(short_link)
    recipe = get_object_or_404(Recipe, link=short_link)
    print(recipe.id)
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
