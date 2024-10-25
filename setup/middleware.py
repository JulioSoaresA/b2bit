# middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifica se o usuário está acessando /api/ e não está autenticado
        if request.path == '/api/' and not request.user.is_authenticated:
            return redirect(reverse('login'))  # 'login' deve ser o nome da sua rota de login

        response = self.get_response(request)
        return response
