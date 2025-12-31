
def get_est_date_time():
    """Get the current date and time in Eastern Standard Time (EST)
    Returns: MM-DD-YYYY_HH-MM-SS_AM/PM -> 12-30-2025_8-32-33_PM
    """
    
    from datetime import datetime
    date_time = datetime.now().strftime("%m-%d-%Y_%I-%M-%S_%p")
    return date_time

def convert_unix_to_iso8601_time(unix_timestamp: float) -> str:
    """Convert a Unix timestamp to ISO 8601 format with milliseconds and 'Z' suffix
    Example: 1704067200.0 -> '2024-01-01T00:00:00.000Z'
    """
    from datetime import datetime

    iso_format = datetime.fromtimestamp(unix_timestamp).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return iso_format