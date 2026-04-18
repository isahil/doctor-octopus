import os

node_env: str = os.environ.get("NODE_ENV", "")

workers_limit: int = 1  # number of workers for the main server process

the_lab_log_file_name: str = "lab.log"  # default log file name for the lab component
the_doc_log_file_name: str = "doc.log"  # default log file name for the executor component

__all__ = [
    "workers_limit",
    "the_lab_log_file_name",
    "the_doc_log_file_name",
]  # export the variables
