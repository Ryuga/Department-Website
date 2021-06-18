from django.urls import path
from django.conf.urls import url
from .views import index_view, about_view, EventView, CourseView


urlpatterns = [
    url(r'^courses/(?P<slug>.*)', CourseView.as_view(), name="course_details"),
    url(r'^events/(?P<slug>.*)', EventView.as_view(), name="event_details"),
    url(r'^events/', EventView.as_view(), name="events"),
    url(r'^about/', about_view, name="about"),
    url('', index_view, name="home"),
]
