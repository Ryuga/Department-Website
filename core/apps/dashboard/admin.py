from django.contrib import admin
from .models import (
    Student, Program, Slideshow, Transaction,
    Event, EventDay, EventSchedule, Registration,
)

admin.site.register([
    Student, Program, Slideshow, Transaction,
    Event, EventDay, EventSchedule, Registration,
])
