import pytest
import requests


@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.regression
def test_cache_reload_happy_path(setup_teardown):
	"""Ensure /cache-reload accepts valid params and returns 200."""
	server_endpoint = setup_teardown
	endpoint = f"{server_endpoint}/cache-reload"

	params = {
		"source": "remote",
		"day": 1,
		"environment": "qa",
	}

	response = requests.get(endpoint, params=params, timeout=15)

	assert response.status_code == 200, f"Expected 200, got {response.status_code}"
	assert "application/json" in response.headers.get("content-type", ""), "Expected JSON response"


@pytest.mark.regression
def test_cache_reload_negative_paths(setup_teardown):
	"""Validate error responses when required params are missing or invalid."""
	server_endpoint = setup_teardown
	endpoint = f"{server_endpoint}/cache-reload"

	scenarios = [
		{
			"name": "missing_source",
			"params": {"day": 1, "environment": "qa"},
			"expected_status": 422,
		},
		{
			"name": "invalid_day_type",
			"params": {"source": "remote", "day": "abc", "environment": "qa"},
			"expected_status": 422,
		},
	]

	for scenario in scenarios:
		print(f"🔍 Testing scenario: {scenario['name']}")
		response = requests.get(endpoint, params=scenario["params"], timeout=10)

		assert response.status_code == scenario["expected_status"], (
			f"{scenario['name']} expected {scenario['expected_status']} but got {response.status_code}"
		)

