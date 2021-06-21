from django.shortcuts import render
from django.views import View
from .models import Event, Course, Faculty, Message, Gallery, Alumni
from django.views.generic import ListView


def index_view(request):
    upcoming_events = Event.objects.filter(status="upcoming")
    messages = Message.objects.order_by('creation_date')[:3]
    return render(request, "index.html", {"messages": messages, "upcoming_events": upcoming_events})


def about_view(request):
    return render(request, "about.html")


def lazy_load_faculty(request):
    faculties = Faculty.objects.all()
    return render(request, "faculty-lazyload.html", {"faculties": faculties})


class EventView(View):
    model = Event
    template_name = "event-details.html"

    def get(self, request, slug=None):
        if slug:
            try:
                event = self.model.objects.get(link=slug)
                return render(request, self.template_name, {"event": event})
            except self.model.DoesNotExist:
                return render(request, "404.html")
        else:
            events = Event.objects.all()
            return render(request, "events.html", {"events": events})


class CourseView(View):
    model = Course
    template_name = "course-details.html"

    def get(self, request, slug):
        try:
            course = self.model.objects.get(link=slug)
            return render(request, self.template_name, {"course": course})
        except self.model.DoesNotExist:
            return render(request, "404.html")


class GalleryListView(ListView):
    template_name = "gallery.html"
    model = Gallery
    paginate_by = 12
    queryset = model.objects.order_by('-date')


class AlumniListView(ListView):
    template_name = "alumni.html"
    model = Alumni
    paginate_by = 12
    queryset = Alumni.objects.order_by('-batch__year')

