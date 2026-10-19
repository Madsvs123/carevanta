from .handlers import NotificationsWorkflowView, NotificationsDashboardView, NotificationsHealthView, NotificationsBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet, NotificationPreferenceViewSet, NotificationsDashboardViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="notifications-notifications")
router.register("preferences", NotificationPreferenceViewSet, basename="notifications-preferences")
router.register("dashboard", NotificationsDashboardViewSet, basename="notifications-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", NotificationsWorkflowView.as_view()),
    path("workflows/bulk/", NotificationsBulkWorkflowView.as_view()),
    path("workflows/dashboard/", NotificationsDashboardView.as_view()),
    path("workflows/health/", NotificationsHealthView.as_view()),
]
