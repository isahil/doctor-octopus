import os
from dotenv import load_dotenv
from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer

load_dotenv(".env", verbose=False, override=True)
local_dir: str = os.environ.get("LOCAL_DIRECTORY", "../../")  # path to the local project directory
environment: str = os.environ.get("ENVIRONMENT")
load_dotenv(f"{local_dir}.env", verbose=False)
load_dotenv(f"{local_dir}.dotenv/.{environment}", verbose=False)

node_env: str = os.environ.get("NODE_ENV")  # [dev, prod]
fixme_mode: str = os.environ.get("FIXME_MODE")  # [true, false]

test_reports_dir: str = os.environ.get(
    "TEST_REPORTS_DIR", "test_reports"
)  # test reports directory can be changed in the .env file
test_reports_date_format = "%m-%d-%Y_%I-%M-%S_%p"  # date format used for the remote test reports directory
lifetime_doctor_clients_count_key = "DO_lifetime_clients_count"
max_concurrent_clients_key = "DO_max_concurrent_clients_count"

the_lab_log_file_name: str = "the-lab.log"
the_doc_log_file_name: str = "the-doc.log"
the_lab_log_file_path: str = f"{local_dir}/logs/{the_lab_log_file_name}"
the_doc_log_file_path: str = f"{local_dir}/logs/{the_doc_log_file_name}"

fastapi_app: FastAPI = None
socketio_app: ASGIApp = None
sio: AsyncServer = None

__all__ = [
    "environment",
    "fastapi_app",
    "lifetime_doctor_clients_count_key",
    "local_dir",
    "max_concurrent_clients_key",
    "node_env",
    "sio",
    "socketio_app",
    "test_reports_dir",
    "the_lab_log_file_name",
    "the_lab_log_file_path",
    "the_doc_log_file_name",
    "the_doc_log_file_path",
]  # export the variables
