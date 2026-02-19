from datetime import datetime, timedelta
from config import test_reports_date_format


def _parse_report_date(received_date: str) -> datetime:
    """Parse a report directory date string, supporting multiple formats.

    Tries formats in order:
    1. Current format with milliseconds: "%m-%d-%Y_%I-%M-%S-%f_%p"
    2. Previous format without milliseconds: "%m-%d-%Y_%I-%M-%S_%p"
    3. Legacy format: "%Y-%m-%d-%H-%M-%S"

    Raises ValueError if no format matches.
    """
    formats = [
        test_reports_date_format,  # Current: "02-18-2026_03-45-30-123456_PM"
        "%m-%d-%Y_%I-%M-%S_%p",  # Previous: "02-18-2026_03-45-30_PM"
        "%Y-%m-%d-%H-%M-%S",  # Legacy: "2024-12-31-1-40-53"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(received_date, fmt)
        except ValueError:
            continue

    # If all formats fail, raise ValueError with all attempted formats
    raise ValueError(f"Unable to parse date '{received_date}' using any known format: {formats}")


def less_or_eqaul_to_date_time(received_date, expected_date_range) -> bool:
    """
    Compare the date of the report directory with the current date.
    If the report is older than the filter, return False.

    Supports multiple date formats for backward compatibility:
    - Current (with milliseconds): "02-18-2026_03-45-30-123456_PM"
    - Previous (no milliseconds): "02-18-2026_03-45-30_PM"
    - Legacy: "2024-12-31-1-40-53"
    """
    try:
        date_time = _parse_report_date(received_date)
        date_diff = datetime.now() - date_time
        if date_diff > timedelta(days=int(expected_date_range)):
            return False
    except ValueError:
        return False
    return True
