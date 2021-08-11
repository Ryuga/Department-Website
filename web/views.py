import hashlib

from django.shortcuts import render
from .models import Event, Course, Faculty, Message, Gallery, Batch, Tag, IpHash, PopUp
from django.views.generic import ListView, View
from ipware import get_client_ip


class IndexView(View):
    context = {}

    def get(self, request):
        self.context["upcoming_events"] = Event.objects.filter(status="upcoming")
        self.context["messages"] = Message.objects.all()[:3]
        ip, is_routable = get_client_ip(request)
        if is_routable:
            ip_hash = hashlib.md5(str.encode(ip))[:10]
            if not IpHash.objects.filter(hash=ip_hash).exists():
                IpHash.objects.create(
                    hash=ip_hash
                )
                self.context["popup"] = PopUp.objects.all()

        return render(request, "index.html", self.context)


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
    extra_context = {"tags": Tag.objects.all()}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['years'] = sorted(set([date[0].year for date in self.queryset.values_list('date')]), reverse=True)
        return context


class AlumniListView(ListView):
    template_name = "alumni.html"
    model = Batch
    paginate_by = 3
    queryset = Batch.objects.order_by('-year')

