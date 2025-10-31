import json
import os
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
import config
import instances
from src.utils.executor import create_command, run_a_command_on_local
from src.component.local import local_report_directories
from src.utils.logger import logger
import src.component.remote as remote
import src.component.notification as notification

router = APIRouter()


@router.get("/cards/", response_class=JSONResponse, status_code=200)
async def get_all_cards(
    source: str = Query(
        ...,
        title="Source",
        description="Retrieve all the HTML & JSON reports from the source",
        example="remote",
    ),
    environment: str = Query(
        "qa",
        title="Environment",
        description="Test environment to filter the reports by",
        example="qa",
    ),
    day: int = Query(
        ...,
        title="Day",
        description="Filter the reports age based on the given day number",
        example=3,
    ),
    app: str = Query(
        "all",
        title="App",
        description="Application to filter the reports by",
        example="clo,loan",
    ),
    protocol: str = Query(
        "all",
        title="Protocol",
        description="Protocol to filter the reports by",
        example="ui,api",
    ),
):
    """Get available report cards based on the source requested"""
    cache_environments = config.test_environments if environment == "all" else [environment]
    cards_instance = instances.fastapi_app.state.cards
    if cards_instance:
        all_cards = []
        for cache_environment in cache_environments:
            expected_filter_data = {"source": source, "environment": cache_environment, "day": day, "app": app, "protocol": protocol}
            logger.info(f"Getting all cards with filter data: {expected_filter_data}")
            fetched_cards = cards_instance.get_cards_from_cache(expected_filter_data)
            if fetched_cards:
                all_cards.extend(fetched_cards)
        
        if len(all_cards) == 0:
            logger.error("No cards found in redis cache.")
            return JSONResponse(
                content={
                    "error": "No cards found in redis cache.",
                    "cards": [],
                },
                status_code=200,
            )

        return JSONResponse(
            content={
                "message": "Cards retrieved successfully",
                "cards": all_cards,
            },
            status_code=200,
        )
    else:
        logger.info("Cards class not found in app state.")
        return JSONResponse(
            content={
                "message": "Cards class instance not found in app state.",
                "cards": [],
            },
            status_code=500,
        )


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
        title="S3 Root Directory",
        description="S3 Root directory of the report to be retrieved. Can be used by client to hit the static server directly",
        example="2021-09-01T14:00:00",
    ),
):
    test_report_dir = os.path.basename(root_dir)
    local_r_directories = local_report_directories()

    if source == "remote" and test_report_dir not in local_r_directories:
        logger.info(f"Card not in local. Downloading from S3: {test_report_dir}")
        test_report_dir = remote.download_s3_folder(root_dir)
    else:
        logger.info(f"Card available in local: {test_report_dir}")
    mount_path = f"/test_reports/{test_report_dir}"
    return f"{mount_path}/index.html"


@router.get("/reload-cache/", response_class=JSONResponse, status_code=200)
async def reload_cards_cache(
    source: str = Query(
        ...,
        title="Source",
        description="Retrieve all the HTML & JSON reports from the source",
        example="remote",
    ),
    day: int = Query(
        ...,
        title="Filter",
        description="Filter the reports age based on the given string",
        example=7,
    ),
    environment: str = Query(
        "qa",
        title="Environment",
        description="Environment to filter the reports",
        example="qa",
    ),
):
    """Get available report cards based on the source requested"""
    expected_filter_data = {"environment": environment, "day": day, "source": source}
    cards = instances.fastapi_app.state.cards
    await cards.actions(expected_filter_data)


@router.get("/execute", response_class=PlainTextResponse, status_code=202)
async def execute_command(
    background_tasks: BackgroundTasks,
    options: str = Query(
        ...,
        title="Options",
        description="Command options to be executed",
        example='{"environment": "dev", "app": "clo", "proto": "perf", "suite": "smoke"}',
    ),
):
    """Execute a command on the running server"""
    command = "n/a"
    try:
        _options: dict = json.loads(options)
        _command: str = create_command(_options)
        if command := _command:
            logger.info(f"Command to be executed: {command}")
    except json.JSONDecodeError as e:
        logger.info(f"Invalid JSON input: {e}")
        return JSONResponse(content={"command": command, "error": str(e)}, status_code=500)

    try:
        background_tasks.add_task(run_a_command_on_local, command)
        return JSONResponse(
            content={
                "message": "The command has been successfully submitted and is running in the background.",
                "details": "Please check the server logs or Artillery Cloud for progress updates.",
            },
            status_code=202,
        )
    except Exception as e:
        return JSONResponse(content={"command": command, "error": str(e)}, status_code=500)


@router.get("/notifications/{client_id}", response_class=StreamingResponse)
async def notifications_sse(client_id: str, request: Request):
    """Server-Sent Events (SSE) endpoint to stream push notifications"""
    logger.info(f"Client [{client_id}] connected to /notifications S.S.E endpoint")
    return StreamingResponse(
        notification.notification_stream(request, client_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.get("/health", response_class=JSONResponse, status_code=200)
async def health_check():
    start_time = datetime.now()
    health_data = {
        "status": "healthy",
        "timestamp": start_time.isoformat(),
        "version": os.environ.get("VERSION", "unknown"),
        "services": {},
    }

    try:
        # Various instance health checks for services
        states = ["redis", "aioredis", "cards"]
        for state in states:
            if hasattr(instances.fastapi_app.state, state):
                try:
                    result = False
                    if state == "redis":
                        result = instances.redis.ping()
                    elif state == "aioredis":
                        result = await instances.aioredis.ping()
                    elif state == "cards":
                        result = getattr(instances.fastapi_app.state, state).ping()
                    health_data["services"][state] = "healthy" if result else "unhealthy"
                except Exception as e:
                    logger.warning(f"{state} health check failed: {str(e)}")
                    health_data["services"][state] = "unhealthy"
            else:
                health_data["services"][state] = "n/a"

        response_time = (datetime.now() - start_time).total_seconds() * 1000
        health_data["response_time_ms"] = round(response_time, 2)

        logger.info(f"Health check completed successfully in {response_time:.2f}ms")
        return JSONResponse(content=health_data, status_code=200)
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["error"] = str(e)
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(content=health_data, status_code=500)
