from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "detail": response.data.get("detail", response.data),
            "errors": response.data if isinstance(response.data, dict) else {},
            "status_code": response.status_code,
        }
    return response
