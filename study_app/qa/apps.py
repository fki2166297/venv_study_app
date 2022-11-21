from django.apps import AppConfig
# from .ap_scheduler import start


class QaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qa'

    def ready(self):
        from .ap_scheduler import start
        start()
