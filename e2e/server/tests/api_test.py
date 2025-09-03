
def test_api_endpoint(setup_teardown_fixture):
    print("REST API test started")
    assert setup_teardown_fixture == "Hello, World!"
    print("REST API test completed")
