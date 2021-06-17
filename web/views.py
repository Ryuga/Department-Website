from django.shortcuts import render
from django.views import View
from .models import Event


def index_view(request):
    return render(request, "index.html")


class EventView(View):
    model = Event

    def get(self, request, slug=None):
        if slug:
            try:
                event = self.model.objects.get(link=slug)
                return render(request, "event-details.html", {"event": event})
            except Event.DoesNotExist:
                return render(request, "404.html")
        else:
            events = Event.objects.all()
            return render(request, "events.html", {"events": events})

