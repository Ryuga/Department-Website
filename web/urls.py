from django.urls import path
from django.conf.urls import url
from .views import index_view, about_view, lazy_load_faculty, AlumniListView, EventView, CourseView


urlpatterns = [
    url(r'^courses/(?P<slug>.*)', CourseView.as_view(), name="course_details"),
    url(r'^events/(?P<slug>.*)', EventView.as_view(), name="event_details"),
    url(r'^events/', EventView.as_view(), name="events"),
    url(r'^about/', about_view, name="about"),
    url(r'^alumni/', AlumniListView.as_view(), name="alumni"),
    url(r'^lazy/faculty/', lazy_load_faculty, name="lazy_load_faculty"),
    url('', index_view, name="home"),
]
