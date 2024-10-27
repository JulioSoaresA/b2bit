from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import PermissionDenied
from .models import Post, Like, Follow
from .tasks import update_likes_for_user
from .serializers import PostSerializer, LikeSerializer, PostListSerializer


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