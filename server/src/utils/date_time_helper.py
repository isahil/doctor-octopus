
def get_est_date_time():
    """Get the current date and time in Eastern Standard Time (EST)
    Returns: MM-DD-YYYY_HH-MM-SS_AM/PM -> 12-30-2025_8-32-33_PM
    """
    
    from datetime import datetime
    date_time = datetime.now().strftime("%m-%d-%Y_%I-%M-%S_%p")
    return date_time