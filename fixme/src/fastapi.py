from datetime import datetime
import json
import os
from fastapi import APIRouter, BackgroundTasks, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from src.utils.executor import create_command, run_a_command_on_local
from src.utils.logger import logger

router = APIRouter()

@router.get("/execute", response_class=PlainTextResponse, status_code=202)
async def execute_command(
    background_tasks: BackgroundTasks,
    options: str = Query(
        ...,
        title="Options",
        description="Command options to be executed",
        examples=['{"environment": "dev", "product": "clo", "proto": "perf", "suite": "smoke"}'],
    ),
) -> JSONResponse:
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
    


@router.get("/health", response_class=JSONResponse, status_code=200)
async def health_check() -> JSONResponse:
    from server import fastapi_app

    start_time = datetime.now()
    health_data = {
        "status": "healthy",
        "timestamp": start_time.isoformat(),
        "version": os.environ.get("VERSION", "unknown"),
        "services": {},
    }

    try:
        # Various instance health checks for services
        states = ["fixme"]
        for state in states:
            if hasattr(fastapi_app.state, state):
                try:
                    result = False
                    if state == "fixme":
                        logger.info("Performing health check for FixMe client...")
                        result = True  # Placeholder for actual health check logic

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