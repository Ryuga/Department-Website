from core.apps.dashboard.views import (
    DashView, UserProfileView, LoginView, RegisterView, GoogleAuthLoginCallback, payment_handler, media_access,
    EventProgramsView, EventScheduleView, EventRegistrationView, logout_request, MyRegistrationDetailView,
    AdminRegistrationDetailView, AdminRegistrationDataView
)
from django.urls import re_path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

app_name="dashboard"
urlpatterns = [
    path('', DashView.as_view(), name="dashboard"),
    path('', DashView.as_view(), name="home"),
    path('login/oauth2/google/', GoogleAuthLoginCallback.as_view(), name="oauth_login"),
    path('accounts/login/', LoginView.as_view(), name="login_redirect"),
    path('payments/handlers/', payment_handler, name="payment_handler"),
    re_path(r'^logout/', logout_request, name="logout"),
    re_path(r'^login/', LoginView.as_view(), name="login"),
    re_path(r'^media/(?P<path>.*)', media_access, name='media'),
    re_path(r'^(?P<event_link>.*)/registration/me/',
            MyRegistrationDetailView.as_view(), name="my_registration_details"),
    re_path(r'^register/', RegisterView.as_view(), name="register"),
    re_path(r'^profile/', UserProfileView.as_view(), name="profile"),
    re_path(r'^event/registration/details/(?P<reg_id>.*)/',
            AdminRegistrationDetailView.as_view(), name="registration_details_admin_by_id"),
    re_path(r'^event/registration/details/',
            AdminRegistrationDetailView.as_view(), name="registration_details_admin"),
    re_path(r'^(?P<event_link>.*)/registration/data/',
            AdminRegistrationDataView.as_view(), name="registration_data"),
    re_path(r'^(?P<event_link>.*)/registration/', EventRegistrationView.as_view(), name="registration"),
    re_path(r'^(?P<event_link>.*)/schedule/', EventScheduleView.as_view(), name="schedule"),
    re_path(r'^(?P<event_link>.*)/programs/', EventProgramsView.as_view(), name="programs"),

]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
