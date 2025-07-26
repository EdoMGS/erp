import logging
import uuid
from decimal import Decimal

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def generate_unique_code(prefix=""):
    """Generate a unique code with optional prefix"""
    unique_id = str(uuid.uuid4()).split("-")[0]
    return f"{prefix}{unique_id}" if prefix else unique_id


def generate_unique_reference(prefix="", length=8):
    """Generate unique reference number"""
    unique_id = str(uuid.uuid4().hex[:length])
    return f"{prefix}{unique_id}" if prefix else unique_id


def calculate_work_hours(start_time, end_time):
    """Calculate work hours between two timestamps"""
    if not start_time or not end_time:
        return Decimal("0.00")
    diff = end_time - start_time
    hours = Decimal(str(diff.total_seconds() / 3600))
    return round(hours, 2)


def is_business_day(date):
    """Check if given date is a business day"""
    return date.weekday() < 5  # Monday = 0, Sunday = 6


def validate_file_size(file, max_size_mb):
    """Validate file size"""
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(_(f"File size cannot exceed {max_size_mb}MB"))


def send_notification(title, message, object_type=None, object_id=None, recipients=None):
    """Generic notification sender"""
    from django.contrib.auth import get_user_model

    get_user_model()

    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            notification_data = {
                "type": "notification.message",
                "title": title,
                "message": message,
                "object_type": object_type,
                "object_id": object_id,
            }

            if recipients:
                for recipient in recipients:
                    async_to_sync(channel_layer.group_send)(f"user_{recipient.id}_notifications", notification_data)
            else:
                async_to_sync(channel_layer.group_send)("global_notifications", notification_data)
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


def calculate_financial_metrics(obj):
    """Generic financial calculation helper"""
    from decimal import Decimal

    try:
        total = Decimal("0.00")
        if hasattr(obj, "amount"):
            total += obj.amount
        if hasattr(obj, "additional_costs"):
            total += obj.additional_costs
        return total
    except Exception as e:
        logger.error(f"Error calculating financial metrics: {e}")
        return Decimal("0.00")


def calculate_price_with_tax(price, tax_rate):
    """Calculate price with tax"""
    if not isinstance(price, (int, float, Decimal)):
        raise ValidationError(_("Price must be a number"))
    if not isinstance(tax_rate, (int, float, Decimal)):
        raise ValidationError(_("Tax rate must be a number"))

    return Decimal(price) * (1 + Decimal(tax_rate) / 100)
