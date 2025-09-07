from django.apps import AppConfig

class BudgetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budget'

    def ready(self):
        # Remove or comment out this line - it's causing the error
        # import budget.tasks
        pass