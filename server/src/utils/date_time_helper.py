
def get_est_date_time():
    """Get the current date and time in Eastern Standard Time (EST)
    Returns: MM-DD-YYYY_HH-MM-SS_AM/PM -> 12-30-2025_8-32-33_PM
    """
    
    from datetime import datetime
    date_time = datetime.now().strftime("%m-%d-%Y_%I-%M-%S_%p")
    return date_time

def get_unix_time():
    """Get the current Unix timestamp
    Returns: float Unix timestamp
    """
    from datetime import datetime
    unix_timestamp = datetime.now().timestamp()
    return unix_timestamp

def convert_unix_to_iso8601_time(unix_timestamp: float) -> str:
    """Convert a Unix timestamp to ISO 8601 format with milliseconds
    Example: 1704067200.0 -> '2024-01-01T00:00:00.000'
    """
    from datetime import datetime

    iso_format = datetime.fromtimestamp(unix_timestamp).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    return iso_format

def convert_iso8601_to_unix_time(iso_timestamp: str) -> float:
    """Convert an ISO 8601 formatted timestamp to Unix timestamp. Z suffix indicates UTC.
    Example: '2024-01-01T00:00:00.000Z' -> 1704067200.0
    """
    from datetime import datetime

    dt = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    unix_timestamp = dt.timestamp()
    return unix_timestamp

