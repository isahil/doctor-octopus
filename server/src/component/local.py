import asyncio
import json
import os
from src.util.executor import run_a_command_on_local, is_port_open, kill_process_on_port

local_dir = os.environ.get('LOCAL_DIRECTORY', "../../") # path to test results directory can be changed in the .env file
reports_dir_name = os.environ.get("TEST_REPORTS_DIR", "test_reports") # test reports directory can be changed in the .env file
reports_dir = os.path.join(local_dir, reports_dir_name)

def get_all_local_cards():
    ''' get all local report cards in the local test reports directory'''
    test_results = []
    local_reports_dir = os.listdir(reports_dir)
    print(f"Total local reports found: {len(local_reports_dir)}")

    for folder in local_reports_dir:
        folder_path = os.path.join(reports_dir, folder)
        report_card = {"json_report": {}, "html_report": "", "root_dir": folder} # initialize report card with 2 properties needed for the frontend

        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)

                if file.endswith(".json"):
                    with open(file_path, "r") as f:
                        report_card["json_report"] = json.load(f)
                if file.endswith(".html"):       
                    html_file_path = os.path.join(folder, file)
                    report_card["html_report"] = str(html_file_path)

                # time.sleep(0.1) # simulate slow connection
        test_results.append(report_card)
    sorted_test_results = sorted(test_results, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
    return sorted_test_results

def get_a_local_card_html_report(html):
    ''' get a local html report card based on the path requested'''
    html_file_path = os.path.join(reports_dir, html)
    with open(html_file_path, "r") as f:
        html_file_content = f.read()
        return html_file_content

async def view_a_report_on_local(root_dir):
    try:
        port = "9323"
        pid = await is_port_open(port)
        if len(pid) > 0:
            await kill_process_on_port(pid)
        command = f"cd {local_dir}&& npx playwright show-report {reports_dir_name}/{root_dir}"
        task = asyncio.create_task(run_a_command_on_local(command))
        output = await task
        return output
    except Exception as e:
        raise e
