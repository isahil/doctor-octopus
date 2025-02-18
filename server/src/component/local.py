import json
import os
from config import local_dir, test_reports_dir, test_reports_date_format
from src.util.executor import run_a_command_on_local, open_port_on_local
from src.util.date import less_or_qaul_to_date_time

reports_dir = os.path.join(local_dir, test_reports_dir)


async def get_all_local_cards(sio, sid, filter: int) -> list:
    """get all local report cards in the local test reports directory"""
    results = []
    local_reports_dir = os.listdir(reports_dir)
    print(f"Total reports found on local: {len(local_reports_dir)}")

    for report_dir in local_reports_dir:
        report_dir_path = os.path.join(reports_dir, report_dir)
        card = {
            "json_report": {},
            "html_report": "",
            "root_dir": report_dir,
        }  # initialize report card with 2 properties needed for the frontend

        if os.path.isdir(report_dir_path):
            if not less_or_qaul_to_date_time(report_dir, test_reports_date_format, filter):
                continue
            for file in os.listdir(report_dir_path):
                file_path = os.path.join(report_dir_path, file)

                if file.endswith(".json"):
                    with open(file_path, encoding="utf-8") as f:
                        card["json_report"] = json.load(f)
                if file.endswith(".html"):
                    html_file_path = os.path.join(report_dir, file)
                    card["html_report"] = str(html_file_path)

                # time.sleep(0.1) # simulate slow connection
        results.append(card)
    sorted_test_results = sorted(results, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
    for card in sorted_test_results:
        await sio.emit("cards", card, room=sid)
    return sorted_test_results


def get_a_local_card_html_report(html) -> str:
    """get a local html report card based on the path requested"""
    html_file_path = os.path.join(reports_dir, html)
    with open(html_file_path, "r") as f:
        html_file_content = f.read()
        return html_file_content


async def view_a_report_on_local(root_dir):
    try:
        port = "9323"  # default port for playwright show-report
        await open_port_on_local(port)
        command = f"cd {local_dir}&& npx playwright show-report {test_reports_dir}/{root_dir}"
        await run_a_command_on_local(command)
        message = f"http://localhost:{port}"
        print(f"View report message: {message}")
        return message
    except Exception as e:
        print(f"Error viewing report: {e}")
        raise e
