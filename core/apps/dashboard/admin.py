from django.contrib import admin

from .models import Student, Program, Notification, Registration, Transaction, Event


admin.site.register(Event)
admin.site.register(Student)
admin.site.register(Notification)
admin.site.register(Registration)
admin.site.register(Program)
admin.site.register(Transaction)
