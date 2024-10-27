from django.urls import path
from .views import (
    FollowedListView, FollowerListView, 
    UserListView, UserProfileView
)


urlpatterns = [
    # Rotas de usuários e interações de follow
    path('following/', FollowedListView.as_view(), name='user_followed'),
    path('followers/', FollowerListView.as_view(), name='user_followers'),
    path('user_list/', UserListView.as_view(), name='user_list'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]
