"""HTTP handler adapters exposing enriched `scheduling` workflows."""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import workflows


class SchedulingWorkflowView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(workflows.describe())

    def post(self, request):
        operation = request.data.get("operation")
        payload = request.data.get("payload") or {}
        if not operation:
            return Response({"detail": "operation required"}, status=status.HTTP_400_BAD_REQUEST)
        result = workflows.run(str(operation), actor=request.user, payload=dict(payload))
        code = status.HTTP_200_OK if result.get("ok") else status.HTTP_400_BAD_REQUEST
        return Response(result, status=code)


class SchedulingDashboardView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(workflows.dashboard(request.user))


class SchedulingHealthView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(workflows.healthcheck())


class SchedulingBulkWorkflowView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        ops = request.data.get("operations") or []
        return Response({"results": workflows.bulk_run(ops, actor=request.user)})
