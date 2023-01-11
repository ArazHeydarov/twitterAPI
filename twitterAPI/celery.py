import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twitterAPI.settings')
app = Celery("twitterAPI")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
