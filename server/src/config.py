import os

local_dir = os.environ.get("LOCAL_DIRECTORY", "../../") # path to the local test results directory
reports_dir_name = os.environ.get("TEST_REPORTS_DIR", "test_reports") # test reports directory can be changed in the .env file

the_lab_log_file_name = "the-lab.log"
the_lab_log_file_path = f"{local_dir}/logs/{the_lab_log_file_name}"

cors_allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

__all__ = ["cors_allowed_origins", "local_dir", "reports_dir_name", "the_lab_log_file_name", "the_lab_log_file_path"] # export the variables
