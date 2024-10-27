import time
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from twitter.models import Post, Like, Follow
from twitter.serializers import LikeSerializer, FollowSerializer, FollowedListSerializer, FollowerListSerializer
from .serializers import UserSerializer
from apps.twitter.tasks import send_follower_notification, update_likes_for_user, cache_followers_count





class FollowViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    throttle_classes = [UserRateThrottle]
    
    def create(self, request, *args, **kwargs):
        followed_user_id = request.data.get('followed')

        if not followed_user_id:
            return Response({"detail": "User to follow not provided."}, status=status.HTTP_400_BAD_REQUEST)

        if followed_user_id == str(request.user.id):  # `request.user.id` é um inteiro, então converta para string
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            followed_user = User.objects.get(pk=followed_user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        existing_follow = Follow.objects.filter(follower=request.user, followed=followed_user).first()

        if existing_follow:
            existing_follow.delete()
            cache_followers_count.delay(followed_user.id)
            return Response({"detail": "Unfollowed successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            Follow.objects.create(follower=request.user, followed=followed_user)
            cache_followers_count.delay(followed_user.id)
            # Envie o email de notificação
            send_follower_notification.delay(followed_user.id, request.user.id)
            
            return Response({"detail": "Followed successfully."}, status=status.HTTP_201_CREATED)
    
    def get_view_name(self):
        return "Follow/Unfollow User"


class FollowedListView(generics.ListAPIView):
    serializer_class = FollowedListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['followed_username']
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user).order_by('-created_at')


class FollowerListView(generics.ListAPIView):
    serializer_class = FollowerListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['follower__username']
    throttle_classes = [UserRateThrottle]
    
    def get_queryset(self):
        return Follow.objects.filter(followed=self.request.user).order_by('-created_at')


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'email']
    
    def get_queryset(self):
        queryset = User.objects.all().exclude(pk=self.request.user.id)
        
        return queryset


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    throttle_classes = [UserRateThrottle]

    def get_object(self):
        return self.request.user