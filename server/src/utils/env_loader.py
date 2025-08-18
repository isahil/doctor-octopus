import os
import platform
from dotenv import load_dotenv

load_dotenv(".env", verbose=False, override=True)


def get_local_dir():
    return os.environ.get("LOCAL_DIRECTORY", "../../")


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


def get_main_server_port():
    value = get_env_variable("MAIN_SERVER_PORT")
    if not value:
        raise ValueError("MAIN_SERVER_PORT environment variable is not set.")
    return int(value)


def get_redis_host():
    return get_env_variable("SDET_REDIS_HOST", "localhost")


def get_redis_port():
    return int(get_env_variable("SDET_REDIS_PORT", 6379))


def get_node_env():
    return get_env_variable("NODE_ENV", "dev")


def get_test_env():
    return get_env_variable("ENVIRONMENT", "qa")


def get_app_name():
    return get_env_variable("APP", "loan")


def get_fixme_mode():
    return get_env_variable("FIXME_MODE", "false").lower() == "true"


def get_fixme_server_port():
    return int(get_env_variable("FIXME_SERVER_PORT", 8001))


def get_fix_side():
    return get_env_variable("FIX_SIDE", "client")


def get_fix_mode():
    return get_env_variable("FIX_MODE", "solicited")


def get_fix_counter():
    return get_env_variable("COUNTER", "1")


def get_debug_mode():
    return get_env_variable("DEBUG", "false") == "true"

