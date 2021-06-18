from django.contrib import admin

from .models import Event, Faculty, Alumni, Course

admin.site.register(Faculty)
admin.site.register(Event)
admin.site.register(Alumni)
admin.site.register(Course)
