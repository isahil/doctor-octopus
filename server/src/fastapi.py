import asyncio
import json
import os
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from src.util.executor import create_command, run_a_command_on_local
from src.component.card.local import get_all_local_cards, local_report_directories
from src.component.card.remote import get_all_s3_cards, download_s3_folder

router = APIRouter()

@router.get("/cards/", response_class=JSONResponse, status_code=200, deprecated=True)
async def get_all_cards(
    source: str = Query(
        ...,
        title="Source",
        description="Retrieve all the HTML & JSON reports from the source",
        example="local/remote",
    ),
    filter: int = Query(
        ...,
        title="Filter",
        description="Filter the reports age based on the given string",
        example=7,
    ),
):
    """Get available report cards based on the source requested"""
    print(f"Report Source: {source}")
    if source == "remote":
        s3_cards = get_all_s3_cards({"day": filter})
        return s3_cards
    else:
        return get_all_local_cards(filter)


@router.get("/card", response_class=PlainTextResponse, status_code=200)
async def get_a_card(
    source: str = Query(
        ...,
        title="Source",
        description="Source of the html report file to be retrieved",
        example="local/remote",
    ),
    root_dir: str = Query(
        None,
        title="Root Directory",
        description="Root directory of the report to be retrieved",
        example="2021-09-01T14:00:00",
    ),
):
    test_report_dir = os.path.basename(root_dir)
    local_r_directories = local_report_directories()

    if source == "remote" and test_report_dir not in local_r_directories:
        print(f"Not in local. Downloading report from S3: {test_report_dir}")
        test_report_dir = download_s3_folder(root_dir)
    else:
        print(f"Already in local. No need to download: {test_report_dir}")
    mount_path = f"/test_reports/{test_report_dir}"
    
    return f"{mount_path}/index.html"


@router.get("/execute", response_class=PlainTextResponse, status_code=200)
async def execute_command(
    options: object = Query(
        ...,
        title="Options",
        description="Command options to be executed",
        example='{"environment": "dev", "app": "clo", "proto": "api", "suite": "smoke"}',
    )
):
    """Execute a command on the running server"""
    options = json.loads(options)
    command = create_command(options)
    try:
        return await asyncio.create_task(run_a_command_on_local(command))
    except Exception as e:
        print(f"Error executing command: {e}")
        return JSONResponse(content={f"command: {command} \nerror: {str(e)}"}, status_code=500)
