import os
from dotenv import load_dotenv
from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer

load_dotenv(".env", verbose=False, override=True)
local_dir: str = os.environ.get("LOCAL_DIRECTORY", "../../")  # path to the local project directory
environment: str = os.environ.get("ENVIRONMENT", "qa")
load_dotenv(f"{local_dir}.env", verbose=False)
load_dotenv(f"{local_dir}.dotenv/.{environment}", verbose=False)

server_mode: str = os.environ.get("SERVER_MODE", "local")  # [fixme, local]

test_reports_dir: str = os.environ.get(
    "TEST_REPORTS_DIR", "test_reports"
)  # test reports directory can be changed in the .env file
test_reports_date_format = "%m-%d-%Y_%I-%M-%S_%p"  # date format used for the remote test reports directory

the_lab_log_file_name: str = "the-lab.log"
the_lab_log_file_path: str = f"{local_dir}/logs/{the_lab_log_file_name}"

fastapi_app: FastAPI = None
socketio_app: ASGIApp = None
sio: AsyncServer = None

__all__ = [
    "sio",
    "fastapi_app",
    "socketio_app",
    "local_dir",
    "environment",
    "test_reports_dir",
    "the_lab_log_file_name",
    "the_lab_log_file_path",
]  # export the variables
