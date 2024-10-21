from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Post, Like, Follow
from .serializers import UserRegistrationSerializer, UserSerializer, PostSerializer, LikeSerializer, FollowSerializer, PostListSerializer


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


class LoginView(TokenObtainPairView):
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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_view_name(self):
        return "Create Post"


class PostList(generics.ListAPIView):
    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created_at')
        return queryset
    
    serializer_class = PostListSerializer
