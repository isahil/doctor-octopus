from datetime import datetime, timedelta


def less_or_eqaul_to_date_time(report_dir_date, date_format, filter) -> bool:
    """
    Compare the date of the report directory with the current date.
    If the report is older than the filter, return False.
    """
    try:
        date_time = datetime.strptime(report_dir_date, date_format)  # e.g. "12-31-2024_08-30-00_AM"
        date_diff = datetime.now() - date_time
        if date_diff > timedelta(days=filter):
            # print(f"Date diff: {date_diff} | Filter: {filter} | Date: {date_time}")
            return False
    except ValueError:
        print(f"Error while parsing date: {report_dir_date} | {ValueError}")
        return False
    return True
