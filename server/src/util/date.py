from datetime import datetime, timedelta


def less_or_qaul_to_date_time(report_dir_date, date_format, filter) -> bool:
  """
  Compare the date of the report directory with the current date.
  If the report is older than the filter, return False.
  """
  try:
    date_obj = datetime.strptime(report_dir_date, date_format)  # e.g. "12-31-2024_08-30-00_AM"
    if datetime.now() - date_obj > timedelta(days=filter):
      return False
  except ValueError:
    try:
      # Will discontinue support for this format in the future
      date_obj = datetime.strptime(
        report_dir_date, "%Y-%m-%d-%H-%M-%S"
      )  # e.g. "2024-12-31-1-40-53" [used in legacy reports]
      if datetime.now() - date_obj > timedelta(days=filter):
        return False
    except ValueError:
      print(f"Error while parsing date: {report_dir_date} | {ValueError}")
      return False
  return True
