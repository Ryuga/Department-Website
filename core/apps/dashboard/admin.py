from django.contrib import admin

from .models import Student, Program, Slideshow, Registration, Transaction, Event, EventDay, EventSchedule


admin.site.register(Event)
admin.site.register(Student)
admin.site.register(Slideshow)
admin.site.register(Registration)
admin.site.register(Program)
admin.site.register(Transaction)
admin.site.register(EventDay)
admin.site.register(EventSchedule)
