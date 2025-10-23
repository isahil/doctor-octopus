import os

test_reports_dir: str = os.environ.get("TEST_REPORTS_DIR", "test_reports")
test_reports_date_format = "%m-%d-%Y_%I-%M-%S_%p"  # date format used for the remote test reports directory

test_reports_redis_key = "doctor-octopus:trading-apps-reports"
do_current_clients_count_key = "doctor-octopus:stats:current_clients_count"
do_lifetime_clients_count_key = "doctor-octopus:stats:lifetime_clients_count"
do_max_concurrent_clients_key = "doctor-octopus:stats:max_concurrent_clients_count"
redis_instance_key: str = "doctor-octopus:stats:redis_instance_count"
aioredis_instance_key: str = "doctor-octopus:stats:aioredis_instance_count"
redis_cache_ttl: int = 60  # Redis cache Time To Live (TTL) in days

test_environments: list = ["qa", "dev", "uat", "sit"]  # list of test environments.

the_lab_log_file_name: str = "lab.log"  # default log file name for the lab component
the_doc_log_file_name: str = "doc.log"  # default log file name for the executor component

max_local_dirs = 500  # max number of downloaded test report directories to keep
notification_frequency_time: int = 10  # frequency of S3 notifications update in seconds
pubsub_frequency_time: int = 1  # frequency of redis pubsub update in seconds

rate_limit_wait_time: float = 0.25  # seconds to wait between S3 downloads to avoid rate limiting
rate_limit_folder_batch_size: int = 5  # number of S3 folders to download in a batch before waiting
rate_limit_file_batch_size: int = 20  # number of S3 objects to download in a batch before waiting

__all__ = [
    "do_lifetime_clients_count_key",
    "do_current_clients_count_key",
    "do_max_concurrent_clients_key",
    "max_local_dirs",
    "test_environments",
    "test_reports_dir",
    "test_reports_redis_key",
    "the_lab_log_file_name",
    "the_doc_log_file_name",
    "pubsub_frequency_time",
    "redis_cache_ttl",
]  # export the variables
