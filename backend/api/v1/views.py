from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .serializers import UserSerializer, AvatarSerializer, TagSerializer
from .pagination import BaseLimitOffsetPagination
from recipes.models import Tag

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
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
