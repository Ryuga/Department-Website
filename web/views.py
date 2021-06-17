from django.shortcuts import render
from django.views import View

# Create your views here.


def index_view(request):
    return render(request, "index.html")


class EventView(View):
    def get(self, request, event_id=None):
        pass
