from django.contrib import admin
from django.urls import path, include
from core.apps.web.views import BackwardsCompatibilityRedirect

urlpatterns = [
    path('data/users/qr/<str:reg_id>/', BackwardsCompatibilityRedirect.as_view()),
    path('', admin.site.urls),
]
