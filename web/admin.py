from django.contrib import admin

from .models import Event, Faculty, Alumni, Course, Message

admin.site.register(Faculty)
admin.site.register(Event)
admin.site.register(Alumni)
admin.site.register(Course)
admin.site.register(Message)
