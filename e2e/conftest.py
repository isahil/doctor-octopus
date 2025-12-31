import pytest
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env", verbose=False, override=True)

# Add server src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "server"))
from src.utils.env_loader import (  # type: ignore  # noqa: E402
    get_main_server_host,
    get_main_server_port,
    get_test_reports_dir,
)

TEST_REPORTS_DIR = get_test_reports_dir()


def pytest_configure(config):
    """Set configuration before test collection"""
    html_report_path = f"{TEST_REPORTS_DIR}/index.html"
    json_report_path = f"{TEST_REPORTS_DIR}/report.json"

    # Set the options directly on the config object
    config.option.htmlpath = html_report_path
    config.option.json_report_file = json_report_path


@pytest.fixture(scope="session")
def setup_teardown():
    print("Setting up the setup_teardown fixture")
    main_server_host = get_main_server_host()
    main_server_port = get_main_server_port()
    server_endpoint = f"http://{main_server_host}:{main_server_port}"
    yield server_endpoint
    print("Tearing down the setup_teardown fixture")
