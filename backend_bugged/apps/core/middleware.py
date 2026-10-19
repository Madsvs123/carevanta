from django.utils.deprecation import MiddlewareMixin

from apps.core.audit import log_audit_event


class RequestAuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._audit_ip = request.META.get("REMOTE_ADDR")
        request._audit_user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:512]
        return None

    def process_response(self, request, response):
        user = getattr(request, "user", None)
        if (
            request.path.startswith("/api/")
            and user is not None
            and getattr(user, "is_authenticated", False)
            and request.method in ("POST", "PUT", "PATCH", "DELETE")
        ):
            log_audit_event(
                actor=user,
                action=request.method.lower(),
                resource_type="api_request",
                resource_id=request.path,
                ip_address=getattr(request, "_audit_ip", None),
                user_agent=getattr(request, "_audit_user_agent", ""),
            )
        return response
