from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .pagination import BaseLimitOffsetPagination
from .serializers import (AvatarSerializer, CreateRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer, UserSerializer)

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)


# class RecipeViewSet(viewsets.ViewSet):
#     """ViewSet для модели Recipe"""

#     def list(self, request):
#         queryset = Recipe.objects.all()
#         serializer = RecipeSerializer(
#             queryset, many=True, context={'request': request})
#         return Response(serializer.data)

#     def create(self, request):
#         queryset = Recipe.objects.all()
#         print(queryset)
#         serializer = CreateRecipeSerializer(
#             queryset, many=False, context={'request': request})
#         return Response(serializer.data)

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
