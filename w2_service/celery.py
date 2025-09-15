import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'w2_service.settings')

app = Celery('w2_service')

# Load task settings from the Django settings file.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all registered Django apps.
app.autodiscover_tasks()

# This is a dummy task for testing Celery
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')