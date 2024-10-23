from __future__ import absolute_import
import os
from celery import Celery

# Definir as configurações padrão do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

app = Celery('setup')

# Carrega configurações do Django e Celery (com prefixo CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre e carrega as tarefas (tasks.py) nos aplicativos registrados no INSTALLED_APPS
app.autodiscover_tasks()