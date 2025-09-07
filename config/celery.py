import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery app instance
app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
# This looks for a tasks.py file in each app directory.
app.autodiscover_tasks()

# Schedule periodic tasks
app.conf.beat_schedule = {
    # Check budgets every 5 minutes
    'check-budgets-every-5-minutes': {
        'task': 'budget.tasks.check_budgets_and_schedules_task',
        'schedule': crontab(minute='*/5'),
    },
    # Reset daily spend at midnight every day
    'reset-daily-spend-midnight': {
        'task': 'budget.tasks.reset_daily_spend_task',
        'schedule': crontab(minute=0, hour=0),
    },
    # Reset monthly spend at midnight on the first day of the month
    'reset-monthly-spend-first-day': {
        'task': 'budget.tasks.reset_monthly_spend_task',
        'schedule': crontab(day_of_month='1', minute=0, hour=0),
    },
}