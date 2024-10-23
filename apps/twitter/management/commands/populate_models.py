import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from twitter.models import Post, Like, Follow

fake = Faker()

# Número de usuários a serem criados
NUM_USERS = 1550

# Limites para o número de posts e likes por usuário
MIN_POSTS_PER_USER = 1
MAX_POSTS_PER_USER = 3

# Número máximo de seguidores por usuário
MAX_FOLLOWERS_PER_USER = 1549

def generate_data(command):
    users = []
    posts = []
    likes = []
    follows = []
    
    # Conjunto para rastrear usernames gerados
    existing_usernames = set()

    # Criar usuários
    for i in range(NUM_USERS):
        username = fake.user_name()

        # Garantir que o username seja único
        while username in existing_usernames:
            username = fake.user_name()  # Gerar um novo username se já existir

        existing_usernames.add(username)

        user = User.objects.create_user(
            username=username,
            email=fake.email(),
            password='password'
        )
        users.append(user)

        # Exibir progresso da criação de usuários
        command.stdout.write(command.style.SUCCESS(f'Usuário {i + 1}/{NUM_USERS} criado: {user.username}'))

    # Criar posts para cada usuário
    for i, user in enumerate(users):
        num_posts = random.randint(MIN_POSTS_PER_USER, MAX_POSTS_PER_USER)
        for j in range(num_posts):
            post = Post.objects.create(
                user=user,
                title=fake.sentence(),
                content=fake.paragraph(),
                image=fake.file_name(extension='jpg'),
            )
            posts.append(post)

            # Exibir progresso da criação de posts
            command.stdout.write(command.style.SUCCESS(f'Post {j + 1} criado para {user.username}'))

    # Criar likes aleatórios em posts
    for i, user in enumerate(users):
        num_likes = random.randint(1, min(len(posts), 1549))  # Cada usuário pode curtir até 1549 posts
        liked_posts = random.sample(posts, num_likes)
        for j, post in enumerate(liked_posts):
            like = Like.objects.create(user=user, post=post)
            likes.append(like)

            # Exibir progresso da criação de likes
            command.stdout.write(command.style.SUCCESS(f'Like {j + 1}/{num_likes} dado por {user.username}'))

    # Criar follows aleatórios
    for i, user in enumerate(users):
        num_follows = random.randint(1, MAX_FOLLOWERS_PER_USER)
        followers = random.sample([u for u in users if u != user], num_follows)
        for j, follower in enumerate(followers):
            follow = Follow.objects.create(follower=follower, followed=user)
            follows.append(follow)

            # Exibir progresso da criação de follows
            command.stdout.write(command.style.SUCCESS(f'{follower.username} seguiu {user.username}'))

    return users, posts, likes, follows

class Command(BaseCommand):
    help = 'Popula o banco de dados com usuários, posts, likes e follows'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando a geração de dados...'))
        users, posts, likes, follows = generate_data(self)
        self.stdout.write(self.style.SUCCESS(f'Concluído: {len(users)} usuários, {len(posts)} posts, {len(likes)} likes, e {len(follows)} follows criados.'))
