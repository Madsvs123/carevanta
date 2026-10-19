from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import CanAccessPHI
from .filters import DocumentFolderFilter, DocumentFilter
from .models import DocumentFolder, Document
from .serializers import DocumentFolderSerializer, DocumentSerializer
from .services import process_documents_workflow, get_documents_dashboard

class DocumentFolderViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentFolderSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = DocumentFolderFilter
    search_fields = ['name']
    ordering_fields = ("created_at, "updated_at", "id")


    def get_queryset(self):
        qs = DocumentFolder.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user).order_by("-created_at")
        return qs.filter(owner=user).order_by("-created_at")


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = DocumentFilter
    search_fields = ['title', 'filename']
    ordering_fields = ("created_at", "updated_at", "id")


    def get_queryset(self):
        qs = Document.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user).order_by("-created_at")
        return qs.filter(owner=user).order_by("-created_at")


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DocumentsDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_documents_dashboard(request.user))
