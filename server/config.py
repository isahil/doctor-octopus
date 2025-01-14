import os
from dotenv import load_dotenv
load_dotenv('.env', verbose=False, override=True)
local_dir: str = os.environ.get("LOCAL_DIRECTORY", "../../") # path to the local project directory
environment: str = os.environ.get("ENVIRONMENT", "qa")
load_dotenv(f'{local_dir}.env', verbose=False)
load_dotenv(f'{local_dir}.dotenv/.{environment}', verbose=False)

from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer

server_mode: str = os.environ.get("SERVER_MODE", "local") # [fixme, local]

test_reports_dir: str = os.environ.get("TEST_REPORTS_DIR", "test_reports") # test reports directory can be changed in the .env file
test_reports_age = 7 # days. control how old the test reports can be to be displayed on the frontend

the_lab_log_file_name: str = "the-lab.log"
the_lab_log_file_path: str = f"{local_dir}/logs/{the_lab_log_file_name}"

fastapi_app: FastAPI = None
sio: AsyncServer = None
socketio_app: ASGIApp = None

cors_allowed_origins: list = [
    "http://localhost:3000",
    "http://localhost:8000",
]

__all__ = ["sio","fastapi_app", "socketio_app", "cors_allowed_origins", "local_dir", "environment", "test_reports_dir", "the_lab_log_file_name", "the_lab_log_file_path"] # export the variables
