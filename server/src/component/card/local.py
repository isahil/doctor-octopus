import json
import os
import asyncio
from config import local_dir, test_reports_dir
from src.component.card.validation import validate
from src.util.executor import is_port_open, open_port_on_local, run_a_command_on_local
from src.util.date import less_or_eqaul_to_date_time

server_host = os.environ.get("VITE_SERVER_HOST", "localhost")
reporter_port = os.environ.get("VITE_REPORTER_PORT", "9323")  # default port for playwright show-report
reports_dir = os.path.join(local_dir, test_reports_dir) # ""../../test-reports"


async def get_all_local_cards(sio, sid, filter: int) -> list:
    """get all local report cards in the local test reports directory"""
    results = []
    local_report_directories = os.listdir(reports_dir)
    print(f"Total reports found on local: {len(local_report_directories)}")

    for local_report_directory in local_report_directories:
        local_report_dir_path = os.path.join(reports_dir, local_report_directory)
        card = {
            "json_report": {},
            "html_report": "",
            "root_dir": local_report_directory,
        }  # initialize report card with 2 properties needed for the frontend

        if os.path.isdir(local_report_dir_path):
            if not less_or_eqaul_to_date_time(local_report_directory, filter):
                continue
            for file in os.listdir(local_report_dir_path):
                file_path = os.path.join(local_report_dir_path, file)

                if file.endswith(".json"):
                    with open(file_path, encoding="utf-8") as f:
                        card["json_report"] = json.load(f)
                if file.endswith(".html"):
                    html_file_path = os.path.join(local_report_directory, file)
                    card["html_report"] = str(html_file_path)

                # time.sleep(0.1) # simulate slow connection
        results.append(card)
    sorted_test_results = sorted(results, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
    for card in sorted_test_results:
        await sio.emit("cards", card, room=sid)
    if len(sorted_test_results) == 0:
        await sio.emit("cards", False, room=sid)
    return sorted_test_results


def get_a_local_card_html_report(html) -> str:
    """get a local html report card based on the path requested"""
    html_file_path = os.path.join(reports_dir, html)
    with open(html_file_path, "r") as f:
        html_file_content = f.read()
        return html_file_content


async def wait_for_local_report_to_be_ready(root_dir):
    try:
        report_dir = os.path.join(reports_dir, root_dir)
        pid = await is_port_open("9323")
        while not os.path.exists(report_dir) and pid:
            await asyncio.sleep(1)
            pid = await is_port_open("9323")
        await asyncio.sleep(1) # wait for the report to be ready
        return report_dir
    except Exception as e:
        print(f"Error waiting for report to be ready: {e}")
        raise e

async def view_a_report_on_local(root_dir):
    try:
        command = f"cd {local_dir}&& npx playwright show-report {test_reports_dir}/{root_dir} --host 0.0.0.0 --port {reporter_port}"

        await open_port_on_local(reporter_port)

        wait_for_port_readiness_task = asyncio.create_task(wait_for_local_report_to_be_ready(root_dir))
        asyncio.create_task(run_a_command_on_local(command))
        
        await wait_for_port_readiness_task

        message = f"http://{server_host}:{reporter_port}"
        print(f"Report is ready to be viewed at: {message}")
        return message
    except Exception as e:
        print(f"Error viewing report: {e}")
        raise e
