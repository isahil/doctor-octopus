import pytest
import requests


@pytest.mark.api_smoke
@pytest.mark.api_sanity
@pytest.mark.api_regression
def test_notifications_stream_happy_path(setup_teardown):
    """Validate the SSE stream connects and returns the initial event payload"""
    server_endpoint = setup_teardown
    client_id = "test-client-sse"
    notifications_endpoint = f"{server_endpoint}/notifications/{client_id}"

    with requests.get(notifications_endpoint, stream=True, timeout=10) as response:
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type, f"Unexpected content-type: {content_type}"

        received_lines = []
        for line in response.iter_lines(decode_unicode=True):
            if line:
                received_lines.append(line)
            if len(received_lines) >= 3:
                break

        assert any("event: connected" in line for line in received_lines), "Missing initial connected event"
        assert any("data:" in line for line in received_lines), "Missing data payload in stream"


@pytest.mark.api_regression
def test_notifications_endpoint_negative_paths(setup_teardown):
    """Ensure invalid notification requests are handled gracefully"""
    server_endpoint = setup_teardown

    negative_scenarios = [
        {
            "name": "missing_client_id",
            "method": "get",
            "url": f"{server_endpoint}/notifications",
            "expected_status": 404,
        },
        {
            "name": "post_not_allowed",
            "method": "post",
            "url": f"{server_endpoint}/notifications/test-client",
            "expected_status": 405,
        },
    ]

    for scenario in negative_scenarios:
        print(f"🔍 Testing negative scenario: {scenario['name']}")

        if scenario["method"] == "post":
            response = requests.post(scenario["url"], timeout=10)
        else:
            response = requests.get(scenario["url"], timeout=10)

        assert response.status_code == scenario["expected_status"], (
            f"{scenario['name']} expected {scenario['expected_status']} but got {response.status_code}"
        )

