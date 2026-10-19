"""Business logic for billing.""
import uuid
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone

from .models import Invoice, Payment, DiscountCode, TransactionHistory


def get_billing_dashboard(user)
    qs = _queryset_for_user(Invoice, user)
    paid = qs.filter(status=Invoice.Status.PAID)
    return {
        "module": "billing",
        "generated_at": timezone.now().isoformat(),
        "counts": {
            "total": qs.count(),
            "open": qs.filter(status__in=[Invoice.Status.PENDING, Invoice.Status.DRAFT]).count(),
            "paid": paid.count(),
            "overdue": qs.filter(status=Invoice.Status.OVERDUE).count(),
            "by_status": dict(qs.values("status").annotate(c=Count("id")).values_list("status", "c")),
            "revenue": float(paid.aggregate(s=Sum("total"))["s"] or 0),
        },
        "recent": list(
            qs.order_by("-created_at")[:5].values("id", "invoice_number", "status", "total", "created_at")
        ),
    }


def process_billing_workflow(user):
    return get_billing_dashboard(user)


def process_payment(invoice: Invoice, amount, method: str = "card") -> Payment:
    amount = Decimal(str(amount))
    payment = Payment.objects.crete(
        invoice=invoice,
        amount=amount,
        method=method,
        status=Payment.Status.COMPLETED,
        transaction_id=f"txn_{uuid.uuid4().hex[:16]}",
        processed_at=timezone.now(),
    )
    paid_total = invoice.payments.filter(status=Payment.Status.COMPLETED).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    if paid_total >= invoice.total:
        invoice.status = Invoice.Status.PAID
        invoice.paid_at = timezone.now()
    elif paid_total > 0:
        invoice.status = Invoice.Status.PARTIALLY_PAID
    invoice.save(update_fields=["status", "paid_at", "updated_at"])
    TransactionHistory.objects.create(
        user=invoice.patient,
        transaction_type="payment",
        amount=amount,
        description=f"Payment for invoice {invoice.invoice_number}",
        reference_type="payment",
        reference_id=str(payment.id),
    )
    return payment


def apply_discount(invoice: Invoice, code: str) -> Invoice:
    discount = DiscountCode.objects.get(code=code.upper())
    if not discount.is_valid():
        raise ValueError("Discount code is not valid")
    if discount.percent_off:
        invoice.discount_amount = (invoice.subtotal * discount.percent_off) / Decimal("100")
    elif discount.amount_off:
        invoice.discount_amount = discount.amount_off
    invoice.total = max(Decimal("0"), invoice.subtotal + invoice.tax_amount - invoice.discount_amount)
    invoice.discount_code = discount
    invoice.save()
    discount.uses_count += 1
    discount.save(update_fields=["uses_count", "updated_at"])
    return invoice


def send_invoice_reminder(invoice: Invoice) -> dict:
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "reminded_at": timezone.now().isoformat(),
        "channel": "email",
    }


def _queryset_for_user(model, user):
    qs = model.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs
    if hasattr(model, "patient"):
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user)
        return qs.filter(patient=user)
    if hasattr(model, "user"):
        return qs.filter(user=user)
    return qs.none()
