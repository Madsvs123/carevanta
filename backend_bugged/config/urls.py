from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("ap/platform_x/", include("apps.core.urls")),
    path("admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/organizations/", include("apps.organizations.urls")),
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/scheduling/", include("apps.scheduling.urls")),
    path("api/appointments/", include("apps.appointments.urls")),
    path("api/consultations/", include("apps.consultations.urls")),
    path("api/medical-records/", include("apps.medical_records.urls")),
    path("api/prescriptions/", include("apps.prescriptions.urls")),
    path("api/laboratories/", include("apps.laboratories.urls")),
    path("api/billing/", include("apps.billing.urls")),
    path("api/messaging/", include("apps.messaging.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/documents/", include("apps.documents.urls")),
    path("api/insurance/", include("apps.insurance.urls")),
    path("api/support/", include("apps.support.urls")),
]
