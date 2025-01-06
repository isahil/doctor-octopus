import os
from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer

fastapi_app: FastAPI = None
sio: AsyncServer = None
socketio_app: ASGIApp = None

local_dir: str = os.environ.get("LOCAL_DIRECTORY", "../../") # path to the local test results directory
test_reports_dir: str = os.environ.get("TEST_REPORTS_DIR", "test_reports") # test reports directory can be changed in the .env file
the_lab_log_file_name: str = "the-lab.log"
the_lab_log_file_path: str = f"{local_dir}/logs/{the_lab_log_file_name}"

cors_allowed_origins: list = [
    "http://localhost:3000",
    "http://localhost:8000",
]

__all__ = ["sio","fastapi_app", "socketio_app", "cors_allowed_origins", "local_dir", "test_reports_dir", "the_lab_log_file_name", "the_lab_log_file_path"] # export the variables
