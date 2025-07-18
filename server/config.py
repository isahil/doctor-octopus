import os
from dotenv import load_dotenv

load_dotenv(".env", verbose=False, override=True)
local_dir: str = os.environ.get(
    "LOCAL_DIRECTORY", "../../"
)  # path to the local project directory where tests need to be run from
environment: str = os.environ.get("ENVIRONMENT", "")
load_dotenv(f"{local_dir}.env", verbose=False)
load_dotenv(f"{local_dir}.dotenv/.{environment}", verbose=False)

node_env: str = os.environ.get("NODE_ENV", "")  # [dev, prod]
fixme_mode: str = os.environ.get("FIXME_MODE", "")  # [true, false]

test_reports_dir: str = os.environ.get("TEST_REPORTS_DIR", "test_reports")
test_reports_date_format = "%m-%d-%Y_%I-%M-%S_%p"  # date format used for the remote test reports directory
test_reports_redis_cache_name = "trading-apps-reports"
current_doctor_clients_count_key = "DO_current_clients_count"
lifetime_doctor_clients_count_key = "DO_lifetime_clients_count"
max_concurrent_clients_key = "DO_max_concurrent_clients_count"
redis_instance_key: str = "DO_redis_instance"
aioredis_instance_key: str = "DO_aioredis_instance"

the_lab_log_file_name: str = "lab.log"
the_doc_log_file_name: str = "doc.log"
the_lab_log_file_path: str = f"{local_dir}logs/{the_lab_log_file_name}"
the_doc_log_file_path: str = f"{local_dir}logs/{the_doc_log_file_name}"

max_local_dirs = 250  # max number of downloaded test report directories to keep
notification_frequency_time: int = 10  # frequency of S3 notifications update in seconds
pubsub_frequency_time: int = 1  # frequency of redis pubsub update in seconds

__all__ = [
    "environment",
    "lifetime_doctor_clients_count_key",
    "local_dir",
    "current_doctor_clients_count_key",
    "max_concurrent_clients_key",
    "max_local_dirs",
    "node_env",
    "test_reports_dir",
    "test_reports_redis_cache_name",
    "the_lab_log_file_name",
    "the_lab_log_file_path",
    "the_doc_log_file_name",
    "the_doc_log_file_path",
    "pubsub_frequency_time"
]  # export the variables
