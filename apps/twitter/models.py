from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(verbose_name="Image", upload_to='core/static/img/posts/')
    deleted_post = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_likes_count(self):
        return self.likes.count() 


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} likes {self.post.content[:50]}'


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.PROTECT, related_name='follower')
    followed = models.ForeignKey(User, on_delete=models.PROTECT, related_name='followed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.follower.username} follows {self.followed.username}'

    @classmethod
    def get_followers_count(cls, user):
        """Retorna o número de seguidores de um usuário, utilizando cache."""
        cache_key = f'user_{user.id}_followers_count'
        followers_count = cache.get(cache_key)

        if followers_count is None:
            followers_count = cls.objects.filter(followed=user).count()
            cache.set(cache_key, followers_count, timeout=60 * 15)  # Cache por 15 minutos
        return followers_count

    @classmethod
    def get_followed_count(cls, user):
        """Retorna o número de usuários que um usuário está seguindo, utilizando cache."""
        cache_key = f'user_{user.id}_followed_count'
        followed_count = cache.get(cache_key)

        if followed_count is None:
            followed_count = cls.objects.filter(follower=user).count()
            cache.set(cache_key, followed_count, timeout=60 * 15)  # Cache por 15 minutos
        return followed_count