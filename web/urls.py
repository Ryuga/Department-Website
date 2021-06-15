from django.urls import path
from .views import index_view, event_view


urlpatterns = [
    path('', index_view),
    path('event/', event_view)
]
