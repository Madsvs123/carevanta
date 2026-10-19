from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .platform import module_nav_for_role, platform_health


class PlatformHealthView(APIView)
    permission_classes = ()

    def get(self, request)
        return Response(platform_health())


class PlatformNavView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        role = getattr(request.user, "role", "patient")
        return Response({"role": role, "nav": module_nav_for_role(role)})
