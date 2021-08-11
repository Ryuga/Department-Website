from django.conf.urls import url
from .views import IndexView, about_view, lazy_load_faculty, GalleryListView, EventView, CourseView, AlumniListView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    url(r'^courses/(?P<slug>.*)', CourseView.as_view(), name="course_details"),
    url(r'^events/(?P<slug>.*)', EventView.as_view(), name="event_details"),
    url(r'^events/', EventView.as_view(), name="events"),
    url(r'^about/', about_view, name="about"),
    url(r'^gallery/', GalleryListView.as_view(), name="gallery"),
    url(r'^alumni/', AlumniListView.as_view(), name="alumni"),
    url(r'^lazy/faculty/', lazy_load_faculty, name="lazy_load_faculty"),
    path('', IndexView.as_view(), name="home"),
]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
