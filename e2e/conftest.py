import pytest

@pytest.fixture(scope="session")
def setup_teardown():
    print("Setting up the fixture")
    server_endpoint = "http://localhost:8000"
    yield server_endpoint
    print("Tearing down the fixture")
