from django.db import models
from django.contrib.auth.models import User

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
        return self.like_set.count()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} likes {self.post.content[:50]}'


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.PROTECT, related_name='follower')
    followed = models.ForeignKey(User, on_delete=models.PROTECT, related_name='followed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.follower.username} follows {self.followed.username}'
