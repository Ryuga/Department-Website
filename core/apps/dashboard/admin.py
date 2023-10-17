from django.contrib import admin
from .models import (
    Student, Program, Slideshow, Transaction,
    Event, EventDay, EventSchedule, Registration, ProgramStudentRelation
)

admin.site.register([
    Student, Program, Slideshow, Transaction,
    Event, EventDay, EventSchedule, Registration, ProgramStudentRelation
])
