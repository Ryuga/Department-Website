from django.urls import path
from django.conf.urls import url
from .views import index_view, EventView


urlpatterns = [
    url(r'^events/(?P<slug>.*)', EventView.as_view(), name="event_details"),
    url(r'^events/', EventView.as_view(), name="events"),
    url('', index_view, name="home"),
    url(r'^about/', index_view, name="about"),
]
