import asyncio
import json
import os
import platform
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, JSONResponse
from src.component.local  import get_all_local_cards, view_a_report_on_local
from src.component.remote import get_all_s3_cards, download_s3_folder
from src.util.logger import stream_log_file
from src.util.executor import run_a_command_on_local

aws_bucket_name = os.environ.get('AWS_BUCKET_NAME')
local_dir = os.environ.get("LOCAL_DIRECTORY", "../../") # path to the local test results directory
log_file_name = "the-lab.log"
log_file_path = f"{local_dir}/logs/{log_file_name}"

router = APIRouter()

@router.get("/reports/")
async def get_all_reports(source: str = Query(..., title="Source Name", description="Retrieve all the HTML & JSON reports from the source", example="local/remote")
    ) -> list:
    ''' Get available report cards based on the source requested '''
    print(f"Report Source: {source}")
    if source == "remote":
        s3_cards = get_all_s3_cards()
        return s3_cards
    else: return get_all_local_cards()

@router.get("/report/", response_class=HTMLResponse)
async def get_a_report(
    source: str = Query(..., title="Source Name", description="Source of the html report file to be retrieved", example="local/remote"),
    root_dir_path: str = Query(None, title="Root Directory", description="Root directory of the report to be retrieved", example="2021-09-01T14:00:00")
    ) -> HTMLResponse:
    ''' Start the playwright report view server to see the report content when 'View Report' button is clicked '''
    if source == "remote": test_report_dir = download_s3_folder(root_dir_path)
    else: test_report_dir = root_dir_path

    output = await view_a_report_on_local(test_report_dir)
    return HTMLResponse(status_code=200, content=output, media_type="text/html")


@router.get("/the-lab/")
async def run_command(
    command: str = Query(..., title="Execute Command", description="Command to be executed on the server", example="ls")
    ) -> str:
    ''' Run a playwright test command to execute on the server using The Lab '''
    print(f"FASTAPI received command: {json.loads(command)}")
    lab_options = json.loads(command)
    env = lab_options.get("environment")
    app = lab_options.get("app")
    proto = lab_options.get("proto")
    suite = lab_options.get("suite")

    os = platform.system().lower()
    if os == "darwin" or os == "linux":
        command = f"cd {local_dir} && ENVIRONMENT={env} APP={app} npm run {proto}:{suite}"
    elif os == "windows": command = f"cd {local_dir} && set ENVIRONMENT={env}& set APP={app}& npm run {proto}:{suite}"
    else : raise OSError("Unsupported OS to run command")
    command_task = asyncio.create_task(run_a_command_on_local(f"{command} >> logs/{log_file_name}")) # start background task to run the command
    asyncio.create_task(stream_log_file(log_file_path)) # start background task to stream the log file
    await command_task

    return JSONResponse(status_code=200, content={"message": "Command executed successfully"}, media_type="text/plain")
