import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')

app = Celery('AramGoV2')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'send-due-reminders': {
        'task': 'todo.tasks.send_due_reminders',
        'schedule': crontab(minute='*/15'),  # Run every 15 minutes
    },
    'create-recurring-tasks': {
        'task': 'todo.tasks.create_recurring_tasks',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')