import os
import platform
import subprocess
import time
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from src.component.local  import get_all_local_cards, get_a_local_card_html_report, view_a_report_on_local
from src.component.remote import get_all_s3_cards, download_s3_folder
import json

aws_bucket_name = os.environ.get('AWS_BUCKET_NAME')
local_dir = os.environ.get("LOCAL_DIRECTORY", "../../") # path to the local test results directory

router = APIRouter()

@router.get("/reports/")
async def get_all_reports(source: str = Query(..., title="Source Name", description="Retrieve all the HTML & JSON reports from the source", example="local/remote")
    ) -> list:
    ''' get report cards based on the source requested '''
    print(f"Report Source: {source}")
    if source == "remote":
        s3_cards = get_all_s3_cards()
        return s3_cards
    else: return get_all_local_cards()

@router.get("/report/", response_class=HTMLResponse)
async def get_a_report(
    source: str = Query(..., title="Source Name", description="Source of the html report file to be retrieved", example="local/remote"),
    root_dir: str = Query(None, title="Root Directory", description="Root directory of the report to be retrieved", example="2021-09-01T14:00:00")
    ) -> HTMLResponse:
    '''get the specific html report content when 'View Report' button is clicked'''
    if source == "remote":
        print(f"Viewing a remote report: {root_dir}")
        test_report_dir = download_s3_folder(root_dir)
    else : test_report_dir = root_dir

    output = await view_a_report_on_local(test_report_dir)
    return HTMLResponse(status_code=200, content=output, media_type="text/html")


@router.get("/run-test-suite/")
def run_command(
    command: str = Query(..., title="Execute Command", description="Command to be executed on the server", example="ls")
    ) -> str:
    ''' Run a playwright test command on the server'''
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
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(f"Return Code: {result.returncode} | Command executed: {result.args}")

    if result.stdout: print(f"Output STDOUT: {result.stdout}")
    elif result.stderr: print(f"Output STDERR: {result.stderr}")
    output = result.stdout if result.stdout else result.stderr
    return output
