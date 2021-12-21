from django.urls import re_path
from .views import (
    IndexView, about_view, lazy_load_faculty, GalleryListView,
    EventView, CourseView, AlumniListView
)
from .dash_views import (
    DashView, UserProfileView, LoginView, RegisterView, GoogleAuthLoginCallback,
    ZephyrusEventsView, ZephyrusScheduleView, ZephyrusRegistrationView, logout_request
)
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('login/oauth2/google/', GoogleAuthLoginCallback.as_view(), name="oauth_login"),
    path('accounts/login/', LoginView.as_view(), name="login_redirect"),
    re_path(r'^logout/', logout_request, name="logout"),
    re_path(r'^courses/(?P<slug>.*)', CourseView.as_view(), name="course_details"),
    re_path(r'^events/(?P<slug>.*)', EventView.as_view(), name="event_details"),
    re_path(r'^events/', EventView.as_view(), name="events"),
    re_path(r'^about/', about_view, name="about"),
    re_path(r'^login/', LoginView.as_view(), name="login"),
    re_path(r'^register/', RegisterView.as_view(), name="register"),
    re_path(r'^gallery/', GalleryListView.as_view(), name="gallery"),
    re_path(r'^alumni/', AlumniListView.as_view(), name="alumni"),
    re_path(r'^lazy/faculty/', lazy_load_faculty, name="lazy_load_faculty"),
    re_path(r'^dashboard/', DashView.as_view(), name="dashboard"),
    re_path(r'^profile/', UserProfileView.as_view(), name="profile"),
    re_path(r'^zephyrus/registration/', ZephyrusRegistrationView.as_view(), name="registration"),
    re_path(r'^zephyrus/schedule/', ZephyrusScheduleView.as_view(), name="schedule"),
    re_path(r'^zephyrus/events/', ZephyrusEventsView.as_view(), name="events"),
    path('', IndexView.as_view(), name="home"),
]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
