from django.contrib import admin
from django.urls import path, include, reverse_lazy

from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from rest_framework.permissions import AllowAny


schema_view = swagger_get_schema_view(
    openapi.Info(
        title='Twitter API',
        default_version='1.0.0',
        description='API documentation of Mini Twitter',
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('twitter.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),
]
