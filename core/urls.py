from django.contrib import admin
from django.urls import path, include
from core.apps.web.views import AdminUserDataView, AdminRegistrationCountView

urlpatterns = [
    path('data/users/qr/<str:reg_id>/', AdminUserDataView.as_view()),
    path('data/users/', AdminUserDataView.as_view()),
    path('data/registration/count/', AdminRegistrationCountView.as_view()),
    path('', admin.site.urls),
]
