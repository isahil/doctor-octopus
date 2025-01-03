import asyncio
import json
import os
import platform
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from src.component.local  import get_all_local_cards, view_a_report_on_local
from src.component.remote import get_all_s3_cards, download_s3_folder
from src.util.logger import stream_log_file
from src.util.executor import run_a_command_on_local
from config import the_lab_log_file_path, the_lab_log_file_name, local_dir

aws_bucket_name = os.environ.get('AWS_BUCKET_NAME')

router = APIRouter()

@router.get("/cards/", response_class=JSONResponse)
async def get_all_cards(source: str = Query(..., title="Source Name", description="Retrieve all the HTML & JSON reports from the source", example="local/remote")
    ):
    ''' Get available report cards based on the source requested '''
    print(f"Report Source: {source}")
    if source == "remote":
        s3_cards = get_all_s3_cards()
        return s3_cards
    else: return get_all_local_cards()

@router.get("/card/", response_class=PlainTextResponse, status_code=307)
async def get_a_card(
    source: str = Query(..., title="Source Name", description="Source of the html report file to be retrieved", example="local/remote"),
    root_dir: str = Query(None, title="Root Directory", description="Root directory of the report to be retrieved", example="2021-09-01T14:00:00")
    ):
    ''' Start the playwright report view server to see the report content when 'View Report' button is clicked '''
    if source == "remote": test_report_dir = download_s3_folder(root_dir)
    else: test_report_dir = root_dir

    output = await view_a_report_on_local(test_report_dir)
    return output


@router.get("/the-lab/", response_class=JSONResponse, status_code=200)
async def run_command(
    command: str = Query(..., title="Execute Command", description="Command to be executed on the server", example="ls")
    ):
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
    command_task = asyncio.create_task(run_a_command_on_local(f"{command} >> logs/{the_lab_log_file_name}")) # start background task to run the command
    asyncio.create_task(stream_log_file(the_lab_log_file_path)) # start background task to stream the log file
    await command_task

    return {"message": "The Lab command executed successfully"}
