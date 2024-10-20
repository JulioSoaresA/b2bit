from django.urls import path, include
from .views import LoginView, CustomRefreshTokenView, logout, RegisterView, LoginView, AuthViewSet


urlpatterns = [
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout, name='logout'),
]
