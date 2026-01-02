import os
import sys
import uvicorn
import socket
import requests
import multiprocessing
from celery import shared_task, Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# Process registry to track running servers
running_processes = {}


class UvicornServerTask(Task):
    """Base task class for running Uvicorn servers with proper process tracking"""

    _process = None
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f"Task failed: {exc}")
        # Cleanup any processes that might still be running
        if self._process and self._process.is_alive():
            logger.info(f"Terminating process after failure: {self._process.pid}")
            self._process.terminate()
            self._process.join(timeout=5)
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Cleanup after task returns"""
        if status == "REVOKED" and self._process and self._process.is_alive():
            logger.info(f"Terminating process after revocation: {self._process.pid}")
            self._process.terminate()
            self._process.join(timeout=5)
        super().after_return(status, retval, task_id, args, kwargs, einfo)


def run_uvicorn_server(app_path, host, port, workers, reload=False):
    """Function to run in a separate process for each server"""
    sys.argv = []  # Reset sys.argv to prevent conflicts
    logger.info(f"Starting Uvicorn server: {app_path} on port {port}")

    try:
        uvicorn.run(app_path, host=host, port=port, lifespan="on", workers=workers, reload=reload, log_level="info")
    except Exception as e:
        logger.error(f"Error running Uvicorn server: {str(e)}")
        raise


def is_port_in_use(host, port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


@shared_task(bind=True, base=UvicornServerTask, name="src.celery.tasks.run_main_server")
def run_main_server(self, host="0.0.0.0", port=8000):
    """Task to run the main server using uvicorn directly"""
    # Set environment variable for server mode
    os.environ["SERVER_MODE"] = "main"

    # Check if the port is already in use
    if is_port_in_use(host, port):
        logger.warning(f"Port {port} is already in use. Main server might already be running.")
        return {"status": "warning", "message": f"Port {port} already in use"}

    # Determine number of workers and reload flag based on environment
    node_env = os.environ.get("NODE_ENV", "dev")
    workers = 1 if node_env == "dev" else 2
    reload = node_env != "production"

    # Start the server in a separate process
    process = multiprocessing.Process(
        target=run_uvicorn_server, args=("server:fastapi_app", host, port, workers, reload, "on"), daemon=True
    )

    process.start()
    self._process = process
    logger.info(f"Main server started with PID: {process.pid}")

    # Store the process for cleanup
    running_processes[f"main_server_{port}"] = process

    return {"status": "running", "pid": process.pid, "port": port, "service": "main"}


@shared_task(bind=True, base=UvicornServerTask, name="src.celery.tasks.run_notification_server")
def run_notification_server(self, host="0.0.0.0", port=8001):
    """Task to run the utility server using uvicorn directly"""
    os.environ["SERVER_MODE"] = "util"

    # Check if the port is already in use
    if is_port_in_use(host, port):
        logger.warning(f"Port {port} is already in use. Util server might already be running.")
        return {"status": "warning", "message": f"Port {port} already in use"}

    # Determine number of workers and reload flag based on environment
    node_env = os.environ.get("NODE_ENV", "dev")
    workers = 1 if node_env == "dev" else 2
    reload = node_env != "production"

    # Start the server in a separate process
    process = multiprocessing.Process(
        target=run_uvicorn_server, args=("server-util:fastapi_app", host, port, workers, reload, "on"), daemon=True
    )

    process.start()
    self._process = process
    logger.info(f"Util server started with PID: {process.pid}")

    # Store the process for cleanup
    running_processes[f"notification_server_{port}"] = process

    return {"status": "running", "pid": process.pid, "port": port, "service": "notification"}


@shared_task(name="src.celery.tasks.initialize_environment")
def initialize_environment():
    """Task to initialize the application environment"""
    logger.info("Initializing application environment")
    try:
        # Import here to avoid circular imports
        import asyncio
        from initialize import main as setup_environment

        # Run the async function in an event loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(setup_environment())
        
        logger.info(f"Environment initialization completed: {result}")
        return {"status": "success", "message": "Environment initialized successfully"}
    except Exception as e:
        logger.error(f"Environment initialization failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@shared_task(name="src.celery.tasks.health_check")
def health_check():
    """Task to check the health of all running services"""
    logger.info("Performing health check")
    services = {
        "main": "http://localhost:8000/health",
        "notification": "http://localhost:8001/health",
    }

    results = {}

    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            results[name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "code": response.status_code,
            }
        except requests.RequestException as e:
            results[name] = {"status": "unreachable", "error": str(e)}

    return results


def stop_a_process(key: str):
        process = running_processes[key]
        service = key.split("_")[0]
        port = key.split("_")[-1]

        if process.is_alive():
            pid = process.pid
            logger.info(f"Stopping {key} (PID: {pid})")
            process.terminate()
            process.join(timeout=5)

            # Force kill if still alive
            if process.is_alive():
                logger.warning(f"Process did not terminate gracefully, force killing: {pid}")
                process.kill()
                process.join(timeout=1)

            del running_processes[key]
            return {"status": "stopped", "service": service, "port": port, "pid": pid}
        else:
            logger.warning(f"Process for {key} is not running")
            del running_processes[key]
            return {"status": "not_running", "service": service, "port": port}


@shared_task(name="src.celery.tasks.stop_service")
def stop_service(service_name, port):
    """Task to stop a specific service by name and port"""
    key = f"{service_name}_{port}"

    if key in running_processes:
        stop_a_process(key)
    else:
        logger.warning(f"No process found for {service_name} on port {port}")
        return {"status": "not_found", "service": service_name, "port": port}


@shared_task(name="src.celery.tasks.stop_all_services")
def stop_all_services():
    """Task to stop all running services"""
    results = []

    for key in list(running_processes.keys()):
        result = stop_a_process(key)
        results.append(result)

    running_processes.clear()
    return results
