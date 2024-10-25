from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Follow
from .tasks import cache_followers_count, cache_followed_count

# Atualiza cache de seguidores quando um novo Follow é criado
@receiver(post_save, sender=Follow)
def update_followers_cache_on_create(sender, instance, **kwargs):
    cache_followers_count.delay(instance.followed.id)

# Atualiza cache de seguidores quando um Follow é deletado
@receiver(post_delete, sender=Follow)
def update_followers_cache_on_delete(sender, instance, **kwargs):
    cache_followers_count.delay(instance.followed.id)

# Atualiza cache de seguidos quando um novo Follow é criado
@receiver(post_save, sender=Follow)
def update_followed_cache_on_create(sender, instance, **kwargs):
    cache_followed_count.delay(instance.follower.id)

# Atualiza cache de seguidos quando um Follow é deletado
@receiver(post_delete, sender=Follow)
def update_followed_cache_on_delete(sender, instance, **kwargs):
    cache_followed_count.delay(instance.follower.id)
