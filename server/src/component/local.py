import json
import os
import asyncio
import shutil
from typing import Union
from config import local_dir, test_reports_dir
from src.util.executor import is_port_open, open_port_on_local, run_a_command_on_local
from src.util.date import less_or_eqaul_to_date_time
from src.util.logger import logger

server_host = os.environ.get("MAIN_SERVER_HOST", "")
reporter_port = os.environ.get("REPORTER_SERVER_PORT", 9323)  # default port for playwright show-report
test_reports_path = os.path.join("./", test_reports_dir)  # "./test-reports"


def local_report_directories():
    """get all local report directories"""
    local_report_directories = os.listdir(test_reports_path)
    logger.info(f"Total reports found on local: {len(local_report_directories)}")
    logger.info(f"Local report directories: {local_report_directories}")
    return local_report_directories


def format_local_dir_filter_data(local_dir):
    """Process only JSON report objects from S3 bucket"""
    # object_name = obj["Key"]
    # path_parts = local_dir.split("/")

    # if (len(path_parts) < 6) or not local_dir.endswith("report.json"):
    #     return None

    return {
        "object_name": local_dir,
        "day": local_dir,
        # "protocol": path_parts[4],
        # "environment": path_parts[3],
        # "app": path_parts[2],
        # "file_type": "json",
        "local_root_dir": local_dir,
    }


def get_all_local_cards(expected_filter_data: dict) -> dict:
    """get all local report cards in the local test reports directory"""
    local_report_dirs = local_report_directories()

    formatted_cards_filter_data = list(filter(None, map(format_local_dir_filter_data, local_report_dirs)))

    final_cards_pool = {}
    for received_card_filter_data in formatted_cards_filter_data:
        day = int(expected_filter_data.get("day", ""))
        if not less_or_eqaul_to_date_time(received_card_filter_data["day"], day):
            continue

        report_dir_date = received_card_filter_data["day"]
        if report_dir_date not in final_cards_pool:
            final_cards_pool[report_dir_date] = {
                "filter_data": received_card_filter_data,
                "html_report": f"{report_dir_date}/index.html",
                "json_report": {},
                "root_dir": received_card_filter_data["local_root_dir"],
            }

    # results = await asyncio.gather(*[process_card(card_tuple) for card_tuple in final_cards_pool.items()])
    # filtered_results = [result for result in results if result is not None]
    # sorted_test_results = sorted(results, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
    # logger.info(f"Total reports found on local: {len(filtered_results)}")
    return final_cards_pool


async def process_card(card_tuple) -> Union[dict, None]:
    card_date, card_value = card_tuple
    try:
        object_name = card_value["filter_data"].get("object_name")
        if not object_name:
            return None

        local_report_dir_path = os.path.join(test_reports_path, card_value["root_dir"])
        logger.info(f"Local report dir path: {local_report_dir_path}")
        if os.path.isdir(local_report_dir_path):
            logger.info(f"ISDIR Local report dir path | {os.listdir(local_report_dir_path)}")
            for file in os.listdir(local_report_dir_path):
                file_path = os.path.join(local_report_dir_path, file)

                if file.endswith(".json"):
                    with open(file_path, encoding="utf-8") as j_report:
                        card_value["json_report"] = json.load(j_report)
                        del card_value["json_report"]["suites"]  # remove suites from the report to reduce report size
                        # await redis.create_reports_cache(test_reports_redis_cache_name, card_date, json.dumps(card_value))
                    return card_value
    except (KeyError, json.JSONDecodeError):
        logger.info(f"Error processing card: {card_date}")
        return None


def get_a_local_card_html_report(html) -> str:
    """get a local html report card based on the path requested"""
    html_file_path = os.path.join(test_reports_path, html)
    with open(html_file_path, "r") as f:
        html_file_content = f.read()
        return html_file_content


async def wait_for_local_report_to_be_ready(root_dir):
    try:
        report_dir = os.path.join(test_reports_path, root_dir)
        pid = await is_port_open(9323)
        while not os.path.exists(report_dir) and pid:
            await asyncio.sleep(1)
            pid = await is_port_open(9323)
        await asyncio.sleep(1)  # wait for the report to be ready
        return report_dir
    except Exception as e:
        logger.info(f"Error waiting for report to be ready: {e}")
        raise e


async def view_a_report_on_local(root_dir):
    try:
        command = f"cd {local_dir}&& npx playwright show-report {test_reports_dir}/{root_dir} --host 0.0.0.0 --port {reporter_port}"

        await open_port_on_local(int(reporter_port))

        wait_for_port_readiness_task = asyncio.create_task(wait_for_local_report_to_be_ready(root_dir))
        asyncio.create_task(run_a_command_on_local(command))

        await wait_for_port_readiness_task

        message = f"http://{server_host}:{reporter_port}"
        logger.info(f"Report is ready to be viewed at: {message}")
        return message
    except Exception as e:
        logger.info(f"Error viewing report: {e}")
        raise e


def cleanup_old_test_report_directories(max_dirs=10):
    """
    Remove older test report directories, keeping only the most recent ones.
    Args:
        max_dirs (int): Maximum number of directories to keep
    """
    try:
        if not os.path.exists(test_reports_path):
            logger.warning(f"Test reports directory {test_reports_path} not found")
            return False

        dirs = []
        for item in os.listdir(test_reports_path):
            item_path = os.path.join(test_reports_path, item)
            if os.path.isdir(item_path):
                # Get directory creation time or modification time
                timestamp = os.path.getctime(item_path)
                dirs.append((item_path, timestamp))

        if len(dirs) > max_dirs:
            dirs.sort(key=lambda x: x[1], reverse=True)  # Sort by timestamp (newest first)
            dirs_to_remove = dirs[max_dirs:]  # Keep track of removed directories
            removed_count = 0

            for dir_path, _ in dirs_to_remove:
                try:
                    shutil.rmtree(dir_path)
                    removed_count += 1
                    logger.info(f"Removed old test report directory: {os.path.basename(dir_path)}")
                except Exception as e:
                    logger.error(f"Failed to remove directory {dir_path}: {str(e)}")

            logger.info(f"Cleanup complete. Removed {removed_count} old test report directories.")
        else:
            logger.info(f"No cleanup needed. Only {len(dirs)} directories exist (max: {max_dirs}).")
    except Exception as e:
        logger.error(f"Error during cleanup of test report directories: {str(e)}")
        return False
    return True
