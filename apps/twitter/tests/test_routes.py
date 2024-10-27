from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from twitter.models import Post, Like, Follow
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io



class CreatePostViewSetTest(APITestCase):
    def setUp(self):
        # Cria um usuário de teste
        self.user = User.objects.create_user(username='testuser', password='password')

        # Define a URL de login e a URL de criação de post
        self.login_url = reverse('login')  # Nome da rota para LoginView
        self.create_post_url = '/api/posts/create/'

    def get_jwt_cookie(self):
        """Faz o login e captura o cookie JWT."""
        login_data = {
            'username': 'testuser',
            'password': 'password'
        }

        # Faz a requisição para a LoginView para obter o cookie
        response = self.client.post(self.login_url, login_data, format='json')
        
        # Verifica se o login foi bem-sucedido
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Retorna o cookie 'access_token'
        return response.cookies.get('access_token')

    def test_create_post_with_image(self):
        """Test creating a post with an image."""
        # Obtém o cookie JWT via login
        cookie = self.get_jwt_cookie()

        # Cria uma imagem em memória usando PIL
        image = Image.new('RGB', (100, 100), color='red')  # Uma imagem 100x100 vermelha
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')  # Salva como JPEG
        image_file.seek(0)  # Volta ao início do arquivo

        # Cria um arquivo de upload
        image_upload = SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")

        data = {
            'title': 'Test Post',
            'content': 'This is a test post.',
            'image': image_upload  # Inclui a imagem no corpo da requisição
        }

        # Faz a requisição de criação de post, incluindo o cookie JWT
        response = self.client.post(
            self.create_post_url, 
            data, 
            format='multipart',  # Necessário para envio de arquivos
            HTTP_COOKIE=f'access_token={cookie.value}'  # Inclui o cookie na requisição
        )

        # Verifica o status e a criação do post
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LikeViewSetTest(APITestCase):
    def setUp(self):
        # Cria um usuário de teste
        self.user = User.objects.create_user(username='testuser', password='password')

        # Define a URL de login e a URL de criação de post
        self.login_url = reverse('login')  # Nome da rota para LoginView

        self.post = Post.objects.create(title='Post Test', content='Test content', user=self.user)
        self.like_url = '/api/posts/like/'
    
    def get_jwt_cookie(self):
        """Faz o login e captura o cookie JWT."""
        login_data = {
            'username': 'testuser',
            'password': 'password'
        }

        # Faz a requisição para a LoginView para obter o cookie
        response = self.client.post(self.login_url, login_data, format='json')
        
        # Verifica se o login foi bem-sucedido
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Retorna o cookie 'access_token'
        return response.cookies.get('access_token')

    def test_like_post(self):
        """Test liking a post with JWT"""
        # Obtém o cookie JWT via login
        cookie = self.get_jwt_cookie()
        
        data = {
            'post': self.post.id
        }
        
        response = self.client.post(
            self.like_url, 
            data, 
            format='json',  # Necessário para envio de arquivos
            HTTP_COOKIE=f'access_token={cookie.value}'  # Inclui o cookie na requisição
        )
                
        # Verifica se o like foi adicionado
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_unlike_post(self):
        """Test unliking a post with JWT"""
        # Primeiro, dar o like para garantir que haja um registro para unlike
        self.test_like_post()
        
        # Obtém o cookie JWT via login
        cookie = self.get_jwt_cookie()
        
        data = {
            'post': self.post.id
        }
        
        response = self.client.post(
            self.like_url, 
            data, 
            format='json',  # Necessário para envio de arquivos
            HTTP_COOKIE=f'access_token={cookie.value}'  # Inclui o cookie na requisição
        )
        
        # Verifica se o like foi removido
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 0)


class FollowViewSetTest(APITestCase):
    def setUp(self):
        # Cria dois usuários, um para seguir e outro para ser seguido
        self.follower = User.objects.create_user(username='follower', password='password')
        self.followed = User.objects.create_user(username='followed', password='password')

        # Define a URL de login e a URL de criação de post
        self.login_url = reverse('login')  # Nome da rota para LoginView
        self.follow_url = '/api/user/follow/'
    
    def get_jwt_cookie(self):
        """Faz o login e captura o cookie JWT."""
        login_data = {
            'username': 'follower',
            'password': 'password'
        }

        # Faz a requisição para a LoginView para obter o cookie
        response = self.client.post(self.login_url, login_data, format='json')
        
        # Verifica se o login foi bem-sucedido
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Retorna o cookie 'access_token'
        return response.cookies.get('access_token')

    def test_follow_user(self):
        """Test following a user with JWT"""
        # Obtém o cookie JWT via login
        cookie = self.get_jwt_cookie()
        
        data = {
            'follower': self.follower.id,
            'followed': self.followed.id
        }
        
        response = self.client.post(
            self.follow_url, 
            data, 
            format='json',  # Necessário para envio de arquivos
            HTTP_COOKIE=f'access_token={cookie.value}'  # Inclui o cookie na requisição
        )
        
        # Verifica se o follow foi realizado
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_unfollow_user(self):
        """Test unfollowing a user with JWT"""
        # Primeiro, faz o follow para garantir que haja um registro para unfollow
        self.test_follow_user()
        
        # Obtém o cookie JWT via login
        cookie = self.get_jwt_cookie()
        
        # Define os dados para deixar de seguir
        data = {
            'follower': self.follower.id,
            'followed': self.followed.id
        }
        
        # Faz a requisição para deixar de seguir
        response = self.client.post(
            self.follow_url, 
            data, 
            format='json',  # Necessário para enviar dados JSON
            HTTP_COOKIE=f'access_token={cookie.value}'  # Inclui o cookie na requisição
        )
        
        # Verifica se o follow foi removido
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Follow.objects.count(), 0)
