"""Вьюсеты пользователя."""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from ..pagination import BaseLimitOffsetPagination
from ..permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from ..serializers.subscription_serializer import (
    SubscriptionCreateSerializer, SubscriptionSerializer)
from ..serializers.user_serializer import AvatarSerializer

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
            subscriptions__subscriber=request.user
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
