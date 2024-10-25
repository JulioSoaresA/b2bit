from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from twitter.models import Follow
from twitter.tasks import send_follower_notification
from unittest.mock import patch


User = get_user_model()

class FollowCacheTest(TestCase):
    def setUp(self):
        # Criação de usuários para teste
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.user3 = User.objects.create_user(username='user3', password='password')
        
        # Limpa o cache antes de cada teste
        cache.clear()

    def test_get_followers_count_cache(self):
        # Cria um novo seguidor e verifica o cache
        Follow.objects.create(follower=self.user2, followed=self.user1)
        followers_count = Follow.get_followers_count(self.user1, update_cache=True)
        self.assertEqual(followers_count, 1)

    def test_get_followed_count_cache(self):
        """Test the cache for the followed count."""
        
        # Sem seguidos inicialmente
        self.assertEqual(Follow.get_followed_count(self.user2), 0)
        
        # Criação de uma relação de seguidor e seguidos
        Follow.objects.create(follower=self.user2, followed=self.user1)
        
        # Atualiza o cache explicitamente
        Follow.get_followed_count(self.user2, update_cache=True)
        
        # Confere se o cache contém o valor correto
        cache_key = f'user_{self.user2.id}_followed_count'
        self.assertEqual(cache.get(cache_key), 1)

class FollowSignalCacheTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        
        # Limpa o cache antes de cada teste
        cache.clear()

    def test_followers_cache_update_on_new_follow(self):
        """Test the cache update when a new follower is added."""
        
        # Cria a relação de seguidor e seguido
        Follow.objects.create(follower=self.user2, followed=self.user1)
        
        # Atualiza o cache explicitamente
        Follow.get_followers_count(self.user1, update_cache=True)
        
        # Confere se o cache contém o valor correto de seguidores
        cache_key = f'user_{self.user1.id}_followers_count'
        self.assertEqual(cache.get(cache_key), 1)
        
    def test_followers_cache_update_on_unfollow(self):
        """Test the cache update when a follower is removed."""
        
        Follow.objects.create(follower=self.user2, followed=self.user1)
        Follow.get_followers_count(self.user1, update_cache=True)

        # Realiza o unfollow
        Follow.objects.filter(follower=self.user2, followed=self.user1).delete()

        # Verifique se o cache é atualizado para o novo valor
        Follow.get_followers_count(self.user1, update_cache=True)
        cache_key = f'user_{self.user1.id}_followers_count'
        self.assertEqual(cache.get(cache_key), 0)

class FollowCacheExpirationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        
        # Limpa o cache antes de cada teste
        cache.clear()

    def test_followers_cache_expiration(self):
        """Test the cache expiration for followers count."""
        
        # Cria um novo seguidor e verifica se o cache expira corretamente
        Follow.objects.create(follower=self.user2, followed=self.user1)
        cache_key = f'user_{self.user1.id}_followers_count'
        
        # Atualiza o cache manualmente para simular expiração
        Follow.get_followers_count(self.user1, update_cache=True)
        self.assertEqual(cache.get(cache_key), 1)

        # Força a expiração do cache e verifica o recalculo
        cache.delete(cache_key)
        self.assertEqual(Follow.get_followers_count(self.user1, update_cache=True), 1)


class SendFollowerNotificationTest(TestCase):

    def setUp(self):
        # Criação dos usuários de teste
        self.followed_user = User.objects.create_user(
            username='followed_user', email='followed_user@example.com', password='test123'
        )
        self.follower_user = User.objects.create_user(
            username='follower_user', email='follower_user@example.com', password='test123'
        )

    @patch('twitter.tasks.send_mail')
    def test_send_follower_notification(self, mock_send_mail):
        """Test the email notification sent to the followed user when a new follower is added."""
        
        # Chama a task que usa send_mail internamente
        send_follower_notification(self.followed_user.id, self.follower_user.id)
        
        # Verifica se send_mail foi chamada com os argumentos corretos em ordem
        mock_send_mail.assert_called_once_with(
            f"{self.follower_user.username} começou a seguir você!",
            f"Olá {self.followed_user.username},\n\n{self.follower_user.username} começou a seguir você!!",
            "testsbackend@gmail.com",
            ["followed_user@example.com"]
        )
