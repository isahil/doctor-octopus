import os
import platform
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from config import test_reports_dir

load_dotenv(".env", verbose=False, override=True)


def get_local_dir():
    return os.environ.get("LOCAL_DIRECTORY", "../../octopus-tests/")


local_dir = get_local_dir()  # path to the local project directory where tests need to be run from
load_dotenv(f"{local_dir}.env", verbose=False)
load_dotenv(f"{local_dir}.dotenv/.{os.environ.get('ENVIRONMENT')}", verbose=False)

from src.utils.logger import logger  # noqa


def get_env_variable(var_name, default_value=None):
    value = os.environ.get(var_name, default_value)
    # logger.trace(f"Retrieved environment variable '{var_name}': {value}")
    return value


def set_env_variable(var_name, value):
    os.environ[var_name] = value
    logger.info(f"Set environment variable '{var_name}': {value}")


def get_os_name():
    return platform.system()


def get_server_mode():
    return get_env_variable("SERVER_MODE")


def get_main_server_host():
    return get_env_variable("MAIN_SERVER_HOST", "localhost")


def get_main_server_port():
    value = get_env_variable("MAIN_SERVER_PORT")
    if not value:
        raise ValueError("MAIN_SERVER_PORT environment variable is not set.")
    return int(value)


def get_redis_host():
    return get_env_variable("SDET_REDIS_HOST", "localhost")


def get_redis_port():
    return int(get_env_variable("SDET_REDIS_PORT", 6379))


def get_test_reports_dir():
    """Get test reports directory, creating timestamped subdirectory if not already set"""
    dir_exists = get_env_variable("TEST_REPORTS_DIR")
    if dir_exists:
        return dir_exists

    # Format: MM-DD-YYYY_HH-MM-SS_AM/PM
    report_dir = datetime.now().strftime("%m-%d-%Y_%I-%M-%S_%p")
    full_test_reports_dir = f"./{test_reports_dir}/{report_dir}"

    # Ensure directory exists
    Path(full_test_reports_dir).mkdir(parents=True, exist_ok=True)
    set_env_variable("TEST_REPORTS_DIR", full_test_reports_dir)
    logger.info(f"Ensured reports directory at: {full_test_reports_dir}")

    return full_test_reports_dir


def get_node_env():
    return get_env_variable("NODE_ENV", "dev")


def get_test_env():
    return get_env_variable("ENVIRONMENT", "qa")


def get_app_name():
    return get_env_variable("APP", "loan")


def get_fixme_mode():
    return get_env_variable("FIXME_MODE", "false") == "true"


def get_fixme_server_port():
    return int(get_env_variable("FIXME_SERVER_PORT", "8001"))


def get_fix_side():
    return get_env_variable("FIX_SIDE", "client")


def get_fix_mode():
    return get_env_variable("FIX_MODE", "solicited")


def get_fix_counter():
    return get_env_variable("COUNTER", "1")


def get_debug_mode():
    """Get debug mode from environment variables. Returns True if any of the below conditions are met, otherwise False.
    - ACTIONS_STEP_DEBUG is set to "1" (GitHub Actions)
    - RUNNER_DEBUG is set to "1" (GitHub Actions)
    """
    return get_env_variable("ACTIONS_STEP_DEBUG") == "1" or get_env_variable("RUNNER_DEBUG") == "1"


def get_aws_sdet_bucket_name():
    return get_env_variable("AWS_SDET_BUCKET_NAME")


def get_aws_sdet_bucket_region():
    return get_env_variable("AWS_SDET_BUCKET_REGION")


def get_aws_sdet_bucket_access_key_id():
    return get_env_variable("AWS_SDET_BUCKET_ACCESS_KEY_ID")


def get_aws_sdet_bucket_secret_access_key():
    return get_env_variable("AWS_SDET_BUCKET_SECRET_ACCESS_KEY")


def get_aws_session_token():
    return get_env_variable("AWS_SESSION_TOKEN")
