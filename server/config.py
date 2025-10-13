import os
# from dotenv import load_dotenv

# load_dotenv(".env", verbose=False, override=True)
# local_dir: str = os.environ.get(
#     "LOCAL_DIRECTORY", "../../"
# )  # path to the local project directory where tests need to be run from
# load_dotenv(f"{local_dir}.env", verbose=False)
# load_dotenv(f"{local_dir}.dotenv/.{environment}", verbose=False)

test_reports_dir: str = os.environ.get("TEST_REPORTS_DIR", "test_reports")
test_reports_date_format = "%m-%d-%Y_%I-%M-%S_%p"  # date format used for the remote test reports directory
test_reports_redis_cache_name = "trading-apps-reports"

do_current_clients_count_key = "DO:current_clients_count"
do_lifetime_clients_count_key = "DO:lifetime_clients_count"
do_max_concurrent_clients_key = "DO:max_concurrent_clients_count"
redis_instance_key: str = "DO:redis_instance_count"
aioredis_instance_key: str = "DO:aioredis_instance_count"
redis_cache_expiry_days: int = 30  # number of days to keep the Redis cache

test_environments: list = ["qa", "dev", "uat", "sit"]  # list of test environments.

the_lab_log_file_name: str = "lab.log"  # default log file name for the lab component
the_doc_log_file_name: str = "doc.log"  # default log file name for the executor component

max_local_dirs = 500  # max number of downloaded test report directories to keep
notification_frequency_time: int = 10  # frequency of S3 notifications update in seconds
pubsub_frequency_time: int = 1  # frequency of redis pubsub update in seconds

rate_limit_wait_time: float = 3  # seconds to wait between S3 downloads to avoid rate limiting
rate_limit_folder_batch_size: int = 5  # number of S3 folders to download in a batch before waiting
rate_limit_file_batch_size: int = 20  # number of S3 objects to download in a batch before waiting

__all__ = [
    "do_lifetime_clients_count_key",
    "do_current_clients_count_key",
    "do_max_concurrent_clients_key",
    "max_local_dirs",
    "test_environments",
    "test_reports_dir",
    "test_reports_redis_cache_name",
    "the_lab_log_file_name",
    "the_doc_log_file_name",
    "pubsub_frequency_time",
    "redis_cache_expiry_days",
]  # export the variables
