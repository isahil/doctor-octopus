import pytest

@pytest.fixture(scope="session")
def setup_teardown_fixture():
    print("Setting up the fixture")
    yield "Hello, World!"
    print("Tearing down the fixture")
