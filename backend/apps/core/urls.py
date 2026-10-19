from django.urls import path
from .views import PlatformHealthView, PlatformNavView

urlpatterns = [
    path("health_x/", PlatformHealthView.as_view()),
    path("nav/", PlatformNavView.as_view()),
]
