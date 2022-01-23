from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.apps.dashboard'

    def ready(self):
        from .models import Event
        from django.db.models.signals import pre_save
        pre_save.connect(Event.event_link_setter, sender=Event)
