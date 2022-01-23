from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.apps.web'

    def ready(self):
        from .models import Faculty, Course
        from django.db.models.signals import pre_save
        pre_save.connect(Faculty.faculty_link_setter, Faculty)
        pre_save.connect(Course.course_link_setter, Course)
