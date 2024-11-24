import time
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from twitter.models import Post, Like, Follow
from twitter.serializers import LikeSerializer, FollowSerializer, FollowedListSerializer, FollowerListSerializer
from .serializers import UserSerializer
from apps.twitter.tasks import update_likes_for_user, cache_followers_count


def send_follower_notification(followed_user_id, user_id):
    """Send an email notification to the followed user when a new follower is added."""
    try:
        followed_user = User.objects.get(id=followed_user_id)
        follower_user = User.objects.get(id=user_id)
        
        subject = f"{follower_user.username} começou a seguir você!"
        message = f"Olá {followed_user.username},\n\n{follower_user.username} começou a seguir você!!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [followed_user.email]
        
        send_mail(subject, message, from_email, recipient_list)

    except ObjectDoesNotExist as e:
        # Lide com o caso em que um dos usuários não é encontrado
        print(f"Erro ao encontrar usuário: {e}")
    except Exception as e:
        # Lide com qualquer outra exceção
        print(f"Erro inesperado: {e}")


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
            # Remove o relacionamento de "seguir"
            existing_follow.delete()
            return Response({"detail": "Unfollowed successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            # Cria o relacionamento de "seguir"
            Follow.objects.create(follower=request.user, followed=followed_user)
            # Envie o email de notificação (opcional)
            send_follower_notification(followed_user.id, request.user.id)
            
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
