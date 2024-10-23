from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

@shared_task
def send_follower_notification(followed_user_id, user_id):
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