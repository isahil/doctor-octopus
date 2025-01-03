import os

local_dir = os.environ.get("LOCAL_DIRECTORY", "../../") # path to the local test results directory
the_lab_log_file_name = "the-lab.log"
the_lab_log_file_path = f"{local_dir}/logs/{the_lab_log_file_name}"

__all__ = ["local_dir", "the_lab_log_file_name", "the_lab_log_file_path"]