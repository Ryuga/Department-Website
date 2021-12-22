from django.contrib import admin

from .models import (
    Event, Faculty, Gallery, Course, Message, Batch, Alumni, Tag, PopUp, IpHash,
    Student, SubEvents, DashboardNotification, Registration
)

admin.site.register(Faculty)
admin.site.register(Event)
admin.site.register(Gallery)
admin.site.register(Course)
admin.site.register(Message)
admin.site.register(Batch)
admin.site.register(Alumni)
admin.site.register(Tag)
admin.site.register(IpHash)
admin.site.register(PopUp)
admin.site.register(Student)
admin.site.register(SubEvents)
admin.site.register(Registration)
admin.site.register(DashboardNotification)
