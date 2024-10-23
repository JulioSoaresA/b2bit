from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken



class AuthenticationUserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='admin')
    
    def test_user_authentication_success(self):
        """Test user authentication with valid credentials."""
        user = authenticate(username='admin', password='admin')
        self.assertTrue((user is not None) and user.is_authenticated)
    
    def test_user_authentication_failure(self):
        """Test user authentication with invalid credentials."""
        user = authenticate(username='admin', password='wrongpassword')
        self.assertFalse((user is not None) and user.is_authenticated)


class JWTAuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.token_url = '/api/auth/login/'

    def test_login_success(self):
        """Test successful login with valid credentials."""
        data = {
            'username': 'testuser',
            'password': 'password'
        }

        response = self.client.post(self.token_url, data, format='json')
        
        # Verifica se o login foi bem-sucedido
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verifica se os dados do usuário estão presentes
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        
        # Verifica se o token JWT foi gerado e está no cookie
        self.assertIn('access_token', response.cookies)
        self.assertTrue(response.cookies['access_token'].value)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.token_url, data, format='json')
        
        # Verifica se a resposta de erro é retornada corretamente
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)

    def test_login_cookie_settings(self):
        """Test the settings of the access_token cookie."""
        data = {
            'username': 'testuser',
            'password': 'password'
        }

        response = self.client.post(self.token_url, data, format='json')
        
        # Verifica se o cookie foi configurado corretamente
        cookie = response.cookies.get('access_token')
        self.assertIsNotNone(cookie)
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'None')
        self.assertTrue(cookie['secure'])
        self.assertEqual(cookie['path'], '/')


class JWTProtectedRouteTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', email='testuser@example.com')
        self.login_url = '/api/auth/login/'  
        
        # URL de uma rota protegida por JWT
        self.protected_url = '/api/post/feed/'

    def authenticate(self):
        """Authenticate the user and set the JWT access token cookie."""
        data = {
            'username': 'testuser',
            'password': 'password'
        }
        
        # Realiza a requisição de login
        response = self.client.post(self.login_url, data, format='json')
        
        # Verifica se o login foi bem-sucedido e o cookie JWT foi gerado
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        
        # Configura o cookie para ser utilizado nas próximas requisições
        self.client.cookies['access_token'] = response.cookies['access_token']

    def test_access_protected_route_without_authentication(self):
        """Test access to a protected route without authentication."""
        response = self.client.get(self.protected_url)
        
        # Verifica se o acesso é negado
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'As credenciais de autenticação não foram fornecidas.')

    def test_access_protected_route_with_authentication(self):
        """Test access to a protected route with authentication."""
        # Primeiro, autentica o usuário
        self.authenticate()
        
        # Agora tenta acessar a rota protegida
        response = self.client.get(self.protected_url)
        
        # Verifica se o acesso é permitido (status 200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

