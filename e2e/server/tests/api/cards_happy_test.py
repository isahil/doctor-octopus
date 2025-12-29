import pytest
import requests

@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
def test_get_cards_with_all_filters(setup_teardown):
    """Test /cards endpoint with all filter combinations"""
    server_endpoint = setup_teardown
    CARDS_ENDPOINT = f"{server_endpoint}/cards"
    print("🧪 Testing /cards endpoint with comprehensive filters...")

    # Test different filter combinations
    test_cases = [
        {"source": "remote", "environment": "qa", "day": 1, "app": "loan", "protocol": "ui"},
        {"source": "remote", "environment": "sit", "day": 3, "app": "clo", "protocol": "api"},
        {"source": "remote", "environment": "all", "day": 7, "app": "all", "protocol": "all"},
        {"source": "remote", "environment": "qa", "day": 120, "app": "all", "protocol": "all"},
    ]

    results = []

    for i, params in enumerate(test_cases):
        print(f"🔍 Testing filter combination {i + 1}: {params}")

        try:
            # Make API request
            response = requests.get(CARDS_ENDPOINT, params=params, timeout=30)

            # Validate response
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            response_data = response.json()
            assert "cards" in response_data, "Response should contain 'cards' field"
            assert "message" in response_data, "Response should contain 'message' field"

            # Validate cards structure if present
            if response_data["cards"]:
                for card in response_data["cards"]:
                    assert "json_report" in card, "Each card should have 'json_report'"
                    assert "html_report" in card, "Each card should have 'html_report'"

            results.append(
                {
                    "test_case": i + 1,
                    "params": params,
                    "status": "PASSED",
                    "response_code": response.status_code,
                    "cards_count": len(response_data.get("cards", []))
                }
            )

            print(f"✅ Test case {i + 1} PASSED - Found {len(response_data.get('cards', []))} cards")

        except Exception as e:
            results.append(
                {"test_case": i + 1, "params": params, "status": "FAILED", "error": str(e)}
            )
            print(f"❌ Test case {i + 1} FAILED: {str(e)}")

    # Assert all tests passed
    failed_tests = [r for r in results if r["status"] == "FAILED"]
    assert len(failed_tests) == 0, f"Failed tests: {failed_tests}"
