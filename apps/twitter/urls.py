from django.urls import path, include
from .views import LoginView, CustomRefreshTokenView, logout, RegisterView, LoginView, CreatePostViewSet, PostList, LikeViewSet, FollowViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'post/create_post', CreatePostViewSet)
router.register(r'post/like', LikeViewSet)

urlpatterns = [
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', logout, name='logout'),
    path('post/feed/', PostList.as_view(), name='post_feed'),
    path('', include(router.urls)),
]
