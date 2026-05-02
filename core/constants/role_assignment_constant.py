# core/constants/role_assignment_constant.py
from datetime import timedelta
from django.utils import timezone

UNDO_WINDOW = timedelta(seconds=10)


def is_within_undo_window(log_created_at) -> bool:
    return (timezone.now() - log_created_at) < UNDO_WINDOW


def seconds_left_to_undo(log_created_at) -> int:
    elapsed = timezone.now() - log_created_at
    remaining = UNDO_WINDOW - elapsed
    return max(0, int(remaining.total_seconds()))
