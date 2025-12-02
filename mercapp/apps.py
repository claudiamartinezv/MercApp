from django.apps import AppConfig

class MercappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mercapp'

    def ready(self):
        import mercapp.signals  # noqa
