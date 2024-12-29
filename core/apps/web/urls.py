from django.urls import re_path
from .views import (
    IndexView, AboutView, lazy_load_faculty, GalleryListView,
    EventView, CourseView, AlumniListView, dashboard_redirect,
    PrivacyView, TermsView
)
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

app_name = "web"
urlpatterns = [
    path('', IndexView.as_view(), name="home"),
    path('zephyrus/', dashboard_redirect, name="zephyrus"),
    re_path(r'^courses/(?P<slug>.*)', CourseView.as_view(), name="course_details"),
    re_path(r'^events/(?P<slug>.*)', EventView.as_view(), name="event_details"),
    re_path(r'^events/', EventView.as_view(), name="events"),
    re_path(r'^about/', AboutView.as_view(), name="about"),
    re_path(r'^gallery/', GalleryListView.as_view(), name="gallery"),
    re_path(r'^alumni/', AlumniListView.as_view(), name="alumni"),
    re_path(r'^privacy/', PrivacyView.as_view(), name="privacy"),
    re_path(r'^terms/', TermsView.as_view(), name="terms"),
    re_path(r'^lazy/faculty/', lazy_load_faculty, name="lazy_load_faculty"),
]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
