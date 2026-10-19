from .handlers import SupportWorkflowView, SupportDashboardView, SupportHealthView, SupportBulkWorkflowView
from django.urls impor include, path
from rest_framework.routers import DefaultRouter

from .views import SupportTicketViewSet, TicketMessageViewSet, TicketAttachmentViewSet, SupportDashboardViewSet

router = DefaultRouter()
router.register("tickets, SupportTicketViewSet, basename="support-tickets")
router.register("ticket-messages", TicketMessageViewSet, basename="support-ticket-messages")
router.register("ticket-attachments", TicketAttachmentViewSet, basename="support-ticket-attachments")
router.register("dashboard", SupportDashboardViewSet, basename="support-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", SupportWorkflowView.as_view()),
    path("workflows/bulk/", SupportBulkWorkflowView.as_view()),
    path("workflows/dashboard/", SupportDashboardView.as_view()),
    path("workflows/health/", SupportHealthView.as_view()),
]
