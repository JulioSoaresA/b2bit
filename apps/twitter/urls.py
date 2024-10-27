from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CreatePostViewSet, 
    UpdatePostViewSet, DeletePostViewSet, PostList, LikeViewSet
    )
from users.views import FollowViewSet

# Configuração do router
router = DefaultRouter()
router.register(r'posts/create', CreatePostViewSet, basename='create_post')
router.register(r'posts/like', LikeViewSet, basename='like_post')
router.register(r'user/follow', FollowViewSet, basename='follow_user')

urlpatterns = [
    # Rotas de autenticação
    path('auth/', include('authentication.urls')),
    
    # Rotas de posts
    path('posts/feed/', PostList.as_view(), name='post_feed'),
    path('posts/update/<int:pk>/', UpdatePostViewSet.as_view({'put': 'update', 'get': 'retrieve'}), name='update_post'),
    path('posts/delete/<int:pk>', DeletePostViewSet.as_view({'delete': 'destroy'}), name='delete_post'),
    
    # Rotas de usuários e interações de follow
    path('user/', include('users.urls')),
    
    # Inclui rotas registradas no router
    path('', include(router.urls)),
]
