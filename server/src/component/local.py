import json
import os
from config import local_dir, test_reports_dir
from src.util.executor import run_a_command_on_local, open_port_on_local

reports_dir = os.path.join(local_dir, test_reports_dir)

def get_all_local_cards() -> list:
    ''' get all local report cards in the local test reports directory'''
    test_results = []
    local_reports_dir = os.listdir(reports_dir)
    print(f"Total reports found on local: {len(local_reports_dir)}")

    for folder in local_reports_dir:
        folder_path = os.path.join(reports_dir, folder)
        report_card = {"json_report": {}, "html_report": "", "root_dir": folder} # initialize report card with 2 properties needed for the frontend

        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)

                if file.endswith(".json"):
                    with open(file_path, encoding="utf-8") as f:
                        report_card["json_report"] = json.load(f)
                if file.endswith(".html"):       
                    html_file_path = os.path.join(folder, file)
                    report_card["html_report"] = str(html_file_path)

                # time.sleep(0.1) # simulate slow connection
        test_results.append(report_card)
    sorted_test_results = sorted(test_results, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
    return sorted_test_results

def get_a_local_card_html_report(html) -> str:
    ''' get a local html report card based on the path requested'''
    html_file_path = os.path.join(reports_dir, html)
    with open(html_file_path, "r") as f:
        html_file_content = f.read()
        return html_file_content

async def view_a_report_on_local(root_dir) -> str | Exception:
    try:
        port = "9323" # default port for playwright show-report
        await open_port_on_local(port)
        command = f"cd {local_dir}&& npx playwright show-report {test_reports_dir}/{root_dir}"
        await run_a_command_on_local(command)
        message = f"http://localhost:{port}"
        print(f"View report message: {message}")
        return message
    except Exception as e:
        print(f"Error viewing report: {e}")
        raise e
