from .handlers import MessagingWorkflowView, MessagingDashboardView, MessagingHealthView, MessagingBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConversationViewSet, MessageViewSet, MessageAttachmentViewSet, MessagingDashboardViewSet

router = DefaultRouter()
router.register("conversations", ConversationViewSet, basename="messaging-conversations")
router.register("messages", MessageViewSet, basename="messaging-messages")
router.register("attachments", MessageAttachmentViewSet, basename="messaging-attachments")
router.register("dashboard", MessagingDashboardViewSet, basename="messaging-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", MessagingWorkflowView.as_view()),
    path("workflows/bulk/", MessagingBulkWorkflowView.as_view()),
    path("workflows/dashboard/", MessagingDashboardView.as_view()),
    path("workflows/health/", MessagingHealthView.as_view()),
]
