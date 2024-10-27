from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, CustomRefreshTokenView, logout, RegisterView, CreatePostViewSet, 
    UpdatePostViewSet, DeletePostViewSet, PostList, LikeViewSet, FollowViewSet, 
    FollowedListView, FollowerListView, UserListView, UserProfileView
)

# Configuração do router
router = DefaultRouter()
router.register(r'posts/create', CreatePostViewSet, basename='create_post')
router.register(r'posts/like', LikeViewSet, basename='like_post')
router.register(r'user/follow', FollowViewSet, basename='follow_user')

urlpatterns = [
    # Rotas de autenticação
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    
    # Rotas de posts
    path('posts/feed/', PostList.as_view(), name='post_feed'),
    path('posts/update/<int:pk>/', UpdatePostViewSet.as_view({'put': 'update', 'get': 'retrieve'}), name='update_post'),
    path('posts/delete/<int:pk>', DeletePostViewSet.as_view({'delete': 'destroy'}), name='delete_post'),
    
    # Rotas de usuários e interações de follow
    path('user/following/', FollowedListView.as_view(), name='user_followed'),
    path('user/followers/', FollowerListView.as_view(), name='user_followers'),
    path('user/list/', UserListView.as_view(), name='user_list'),
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),

    # Inclui rotas registradas no router
    path('', include(router.urls)),
]
