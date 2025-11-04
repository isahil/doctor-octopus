import pytest
import requests

@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
def test_cards_endpoint_error_handling(setup_teardown):
    """Test /cards endpoint error handling"""
    server_endpoint = setup_teardown
    CARDS_ENDPOINT = f"{server_endpoint}/cards"
    print("🧪 Testing /cards endpoint error handling...")

    error_test_cases = [
        {"name": "missing_source_parameter", "params": {"environment": "qa", "day": 1}, "expected_status": 422},
        {
            "name": "invalid_day_parameter",
            "params": {"source": "remote", "environment": "qa", "day": "invalid"},
            "expected_status": 422,
        },
        {
            "name": "empty_cache_scenario",
            "params": {"source": "remote", "environment": "nonexistent", "day": 1},
            "expected_status": 200,  # Should return empty cards array
        },
    ]

    results = []

    for test_case in error_test_cases:
        print(f"🔍 Testing error case: {test_case['name']}")

        try:
            response = requests.get(CARDS_ENDPOINT, params=test_case["params"], timeout=30)

            assert response.status_code == test_case["expected_status"], (
                f"Expected {test_case['expected_status']}, got {response.status_code}"
            )

            if response.status_code == 200:
                response_data = response.json()
                # For empty cache, should still have proper structure
                assert "cards" in response_data
                assert isinstance(response_data["cards"], list)

            results.append({"test_case": test_case["name"], "status": "PASSED", "response_code": response.status_code})

            print(f"✅ Error test {test_case['name']} PASSED")

        except Exception as e:
            results.append({"test_case": test_case["name"], "status": "FAILED", "error": str(e)})
            print(f"❌ Error test {test_case['name']} FAILED: {str(e)}")

    # Assert all error handling tests passed
    failed_tests = [r for r in results if r["status"] == "FAILED"]
    assert len(failed_tests) == 0, f"Failed error handling tests: {failed_tests}"
