from celery import shared_task
from django.db.models import Count
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from twitter.models import Post, Follow


@shared_task
def send_follower_notification(followed_user_id, user_id):
    """Send an email notification to the followed user when a new follower is added."""
    try:
        followed_user = User.objects.get(id=followed_user_id)
        follower_user = User.objects.get(id=user_id)
        
        subject = f"{follower_user.username} começou a seguir você!"
        message = f"Olá {followed_user.username},\n\n{follower_user.username} começou a seguir você!!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [followed_user.email]
        
        send_mail(subject, message, from_email, recipient_list)

    except ObjectDoesNotExist as e:
        # Lide com o caso em que um dos usuários não é encontrado
        print(f"Erro ao encontrar usuário: {e}")
    except Exception as e:
        # Lide com qualquer outra exceção
        print(f"Erro inesperado: {e}")


@shared_task
def update_post_likes_cache():
    """Update the cache with the number of likes for each post of all followed users for all users."""
    # Obtém todos os usuários
    users = User.objects.all()

    # Para armazenar os likes dos posts
    posts_likes = []

    # Obtém todos os usuários que seguem outros usuários
    followed_users_map = {user.id: Follow.objects.filter(follower=user).values_list('followed', flat=True) for user in users}

    # Filtra todos os posts dos usuários seguidos
    for user, followed_users in followed_users_map.items():
        if followed_users:
            followed_posts = Post.objects.filter(user__in=followed_users, deleted_post=False).annotate(
                like_count=Count('likes')  # Alterado de 'like_set' para 'likes'
            ).values('id', 'like_count')
            posts_likes.extend(followed_posts)
        print(f"Posts seguidos por {user}: {len(followed_posts)}", flush=True)  # Log de depuração

    # Atualiza o cache com os likes dos posts seguidos
    for post in posts_likes:
        cache_key = f'post_{post["id"]}_likes'
        cache.set(cache_key, post['like_count'], timeout=60 * 15)  # Cache expira em 15 minutos
        print(f"Atualizando cache para post {post['id']}: {post['like_count']} likes", flush=True)  # Log de depuração


@shared_task
def update_likes_for_user(user_id):
    # Recupera os usuários seguidos pelo usuário específico
    followed_users = Follow.objects.filter(follower_id=user_id).values_list('followed', flat=True)

    # Recupera os posts dos usuários seguidos e anota a contagem de likes
    posts = Post.objects.filter(user__in=followed_users, deleted_post=False).annotate(
        likes_count=Count('likes')  # 'likes' deve ser o related_name definido no modelo Like
    )

    for post in posts:
        cache_key = f'post_likes_{post.id}'
        likes_count = post.likes_count  # Acessa diretamente a contagem de likes

        # Armazena ou atualiza a contagem de likes no cache
        cache.set(cache_key, likes_count, timeout=60 * 15)  # Cache para 15 minutos
        print(f'Salvando likes no cache para o post {post.id}: {likes_count}', flush=True)
    print(f'Likes cache atualizado para o usuário {user_id}', flush=True)


@shared_task
def cache_followers_count(user_id):
    """Tarefa para atualizar o cache de seguidores."""
    user = User.objects.get(id=user_id)
    followers_count = Follow.objects.filter(followed=user).count()
    cache.set(f'user_{user_id}_followers_count', followers_count, timeout=60 * 15)  # Cache por 15 minutos
    print(f'Cache atualizado para o usuário {user_id}: {followers_count} seguidores', flush=True)

@shared_task
def cache_followed_count(user_id):
    """Tarefa para atualizar o cache de seguidos."""
    user = User.objects.get(id=user_id)
    followed_count = Follow.objects.filter(follower=user).count()
    cache.set(f'user_{user_id}_followed_count', followed_count, timeout=60 * 15)  # Cache por 15 minutos
    print(f'Cache atualizado para o usuário {user_id}: {followed_count} seguidos', flush=True)