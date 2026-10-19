from rest_framework.exceptions import APIException
from rest_framework import status


class CareVantaError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A CareVanta business rule was violated."
    default_code = "carevanta_error"


class BookingConflictError(CareVantaError):
    default_detail = "The requested time slot is no longer available."
    default_code = "booking_conflict"


class IdentityNotVerifiedError(CareVantaError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Identity verification is required."
    default_code = "identity_not_verified"


class PrescriptionWarningError(CareVantaError):
    default_detail = "Prescription has unresolved safety warnings."
    default_code = "prescription_warning"
