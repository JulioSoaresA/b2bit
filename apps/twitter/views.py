from django.shortcuts import render
from .serializers import UserRegistrationSerializer, UserSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import viewsets

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken


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


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)

            return Response({
                'user': user_serializer.data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({'error': 'Invalid credentials'}, status=400)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def logout(self, request):
        response = Response({"message": "Logout successful."})
        response.delete_cookie('access_token')
        return response