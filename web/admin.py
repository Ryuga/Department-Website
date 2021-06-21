from django.contrib import admin

from .models import Event, Faculty, Gallery, Course, Message

admin.site.register(Faculty)
admin.site.register(Event)
admin.site.register(Gallery)
admin.site.register(Course)
admin.site.register(Message)
