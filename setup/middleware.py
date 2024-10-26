import jwt
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from jwt import InvalidTokenError

class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifica se o usuário está acessando /api/ e não está autenticado
        if request.path == '/api/' and not self._is_authenticated(request):
            return redirect(reverse('login'))  # 'login' deve ser o nome da sua rota de login

        response = self.get_response(request)
        return response

    def _is_authenticated(self, request):
        # Extrai o token JWT do cookie 'access_token'
        token = request.COOKIES.get('access_token')
        if token:
            try:
                # Decodifica o token com a chave secreta do Django
                jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                return True
            except InvalidTokenError:
                return False
        return request.user.is_authenticated 