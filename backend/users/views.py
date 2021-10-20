from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.permissions import IsAuthorOrAdmin
from recipes.views import DefaultResultsSetPagination
from users.models import Subscription, User
from users.serializers.subscription import SubscribeSerializer


class CustomUserViewSet(UserViewSet):
    pagination_class = DefaultResultsSetPagination
    action_permissions = {
        IsAuthorOrAdmin: ['partial_update', 'destroy', 'create'],
        AllowAny: ['retrieve', 'list']
    }

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def get_subscriptions(self, request):
        paginator = DefaultResultsSetPagination()
        users = User.objects.filter(subscribed__user=self.request.user)
        result_page = paginator.paginate_queryset(users, request)
        page = self.paginate_queryset(users)
        serializer = SubscribeSerializer(
            # page,
            result_page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


    @action(
        detail=True,
        methods=['get', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        current_user = request.user
        user = get_object_or_404(
            User,
            id=id
        )
        serializer = SubscribeSerializer(
            many=False,
            instance=user,
            context={'request': request}
        )
        if request.method == 'GET':
            if Subscription.objects.filter(
                    subscribed=current_user, user=user
            ).exists():
                return Response(status=status.HTTP_204_NO_CONTENT)
            Subscription.objects.create(user_id=id, subscribed=current_user)
            return Response(serializer.data, status=status.HTTP_200_OK)


        Subscription.objects.filter(
            subscribed_id=current_user.id,
            user_id=user.id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
