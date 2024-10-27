import time
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, mixins, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Post, Like, Follow
from .serializers import UserRegistrationSerializer, UserSerializer, PostSerializer, LikeSerializer, FollowSerializer, PostListSerializer, FollowedListSerializer, FollowerListSerializer
from .tasks import send_follower_notification, update_likes_for_user, cache_followers_count

class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            request.data['refresh'] = refresh_token
            
            response = super().post(request, *args, **kwargs)
            
            tokens = response.data
            access_token = tokens['access']
            
            res = Response()
            
            res.data = {
                'refreshed': True,
            }
            
            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                samesite='None',
                path='/'
            )
            
            return res
            
        except:
            return Response({'refreshed': False})


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    throttle_classes = [AnonRateThrottle]


class LoginView(TokenObtainPairView):
    throttle_classes = [AnonRateThrottle]
    def post(self, request, *args, **kwargs):
        try:
            # Cria uma instância do serializer e valida os dados
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Obtém o usuário autenticado através do serializer
            user = serializer.user

            # Gera os tokens
            tokens = serializer.validated_data

            # Serializa os dados do usuário
            user_serializer = UserSerializer(user)

            # Cria a resposta customizada com tokens e dados do usuário
            res = Response()
            res.data = {
                'success': True,
                'user': user_serializer.data  # Inclui os dados do usuário
            }

            # Configura o cookie do access_token
            res.set_cookie(
                key='access_token',
                value=tokens['access'],
                httponly=True,
                samesite='None',
                secure=True,
                path='/'
            )

            return res

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        
        response = Response({
            'success': 'Logged out successfully'
        })
        
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=400)


class CreatePostViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    throttle_classes = [UserRateThrottle]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_view_name(self):
        return "Create Post"


class UpdatePostViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        """Limita a busca aos posts do usuário autenticado que não foram deletados."""
        return Post.objects.filter(user=self.request.user, deleted_post=False)

    def perform_update(self, serializer):
        """Verifica se o usuário é o dono do post antes de salvar as alterações."""
        post = self.get_object()
        
        if post.user != self.request.user:
            raise PermissionDenied({"detail": "Você não tem permissão para editar este post."})

        # Salva as alterações se a permissão for concedida
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        """Obtém o post e retorna os dados preenchidos, se não estiver deletado."""
        instance = self.get_object()
        
        if instance.deleted_post:
            raise NotFound({"detail": "Post não encontrado ou foi deletado."})
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)  # Retorna os dados do post


class DeletePostViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        # Limita a busca aos posts do usuário autenticado
        return Post.objects.filter(user=self.request.user, deleted_post=False)

    def perform_destroy(self, instance):
        # Verifica se o usuário é o dono do post
        if instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para deletar este post.")
        # Marca o post como deletado (exclusão lógica)
        instance.deleted_post = True
        instance.save()
        return Response({"detail": "Post deletado com sucesso."}, status=status.HTTP_204_NO_CONTENT)


class PostList(generics.ListAPIView):
    serializer_class = PostListSerializer
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'content', 'user__username']

    def get_queryset(self):
        # Obtém os usuários que o usuário atual está seguindo
        followed_users = Follow.objects.filter(follower=self.request.user).values_list('followed', flat=True)

        # Filtra os posts dos usuários seguidos e ordena por data de criação
        posts = Post.objects.filter(user__in=followed_users, deleted_post=False).order_by('-created_at')

        # Atualiza a contagem de likes de cada post utilizando o cache
        for post in posts:
            cache_key = f'post_{post.id}_likes'
            likes_count = cache.get(cache_key)
            if likes_count is None:
                # Se não está no cache, conta os likes e atualiza o cache
                likes_count = post.likes.count()  # ou use post.get_likes_count()
                cache.set(cache_key, likes_count, timeout=60 * 15)
            post.likes_count = likes_count  # Atribui a contagem de likes ao atributo do post
        return posts



class LikeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    throttle_classes = [UserRateThrottle]

    def create(self, request, *args, **kwargs):
        post_id = request.data.get('post')
        post = Post.objects.get(pk=post_id)

        existing_like = Like.objects.filter(user=request.user, post=post).first()

        if existing_like:
            existing_like.delete()
            # Atualiza o cache após adicionar o like
            update_likes_for_user(request.user.id)
            return Response(
                {"detail": "Like removed successfully."},
                status=status.HTTP_200_OK
            )
        else:
            like = Like.objects.create(user=request.user, post=post)
            serializer = self.get_serializer(like)
            # Atualiza o cache após adicionar o like
            update_likes_for_user(request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_view_name(self):
        return "Like Post"

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