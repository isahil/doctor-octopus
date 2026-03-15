import os
from dotenv import load_dotenv

load_dotenv(".env", verbose=False, override=True)


def get_local_dir():
    return os.environ.get("LOCAL_DIRECTORY", "../../octopus-tests/")


local_dir = (
    get_local_dir()
)  # path to the local project directory where tests need to be run from
load_dotenv(f"{local_dir}.env", verbose=False)
load_dotenv(f"{local_dir}.dotenv/.{os.environ.get('ENVIRONMENT')}", verbose=False)


def get_env_variable(var_name, default_value=None):
    value = os.environ.get(var_name, default_value)
    return value


def get_server_mode():
    return get_env_variable("SERVER_MODE")


def get_node_env():
    return get_env_variable("NODE_ENV", "dev")


def get_test_env():
    return get_env_variable("ENVIRONMENT", "qa")


def get_redis_host():
    return get_env_variable("SDET_REDIS_HOST", "localhost")


def get_redis_url():
    sdet_redis_host = get_redis_host()
    redis_url = f"redis://{sdet_redis_host}:6379/0"
    return redis_url


def get_fixme_server_port():
    port = get_env_variable("FIXME_SERVER_PORT", 8001)
    if not port:
        raise ValueError("FIXME_SERVER_PORT environment variable is not set.")
    return int(port)


def get_debug_mode():
    """Get debug mode from environment variables. Returns True if any of the below conditions are met, otherwise False.
    - ACTIONS_STEP_DEBUG is set to "1" (GitHub Actions)
    - RUNNER_DEBUG is set to "1" (GitHub Actions)
    """
    return (
        get_env_variable("ACTIONS_STEP_DEBUG") == "1"
        or get_env_variable("RUNNER_DEBUG") == "1"
    )
