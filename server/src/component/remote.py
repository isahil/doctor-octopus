import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Union
import redis as _redis
from config import test_reports_dir, test_reports_redis_cache_name
from src.component.validation import validate
from src.util.s3 import S3
from src.util.logger import logger
import src.util.redis as redis_module
import instances

aws_bucket_name = os.environ.get("AWS_SDET_BUCKET_NAME")


def get_a_s3_card_html_report(html) -> bytes:
    card = S3.get_a_s3_object(html)
    return card


def total_s3_objects() -> int:
    total = S3.list_all_s3_objects()
    return len(total)


def format_s3_object_filter_data(obj):
    """Process only JSON report objects from S3 bucket"""
    object_name = obj["Key"]
    path_parts = object_name.split("/")

    if (len(path_parts) < 6) or not object_name.endswith("report.json"):
        return None

    return {
        "object_name": object_name,
        "day": path_parts[5],
        "protocol": path_parts[4],
        "environment": path_parts[3],
        "app": path_parts[2],
        "file_type": "json",
        "s3_root_dir": "/".join(path_parts[:6]),
    }


async def get_all_s3_cards(expected_filter_data: dict) -> list[dict]:
    """Get all report cards object from the S3 bucket"""

    s3_objects = S3.list_all_s3_objects()

    # Process objects in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        formatted_cards_filter_data = list(filter(None, executor.map(format_s3_object_filter_data, s3_objects)))

    # Group objects by report_dir_date. Do we need html_report key since json_report has the value?
    final_cards_pool = {}  # { "report_dir_date": { "json_report": {"object_name": "object_name_value"}, "html_report": "object_name_value", "root_dir": "" }}
    for received_card_filter_data in formatted_cards_filter_data:
        error = validate(received_card_filter_data, expected_filter_data)
        if error:
            continue

        report_dir_date = received_card_filter_data["day"]
        if report_dir_date not in final_cards_pool:
            final_cards_pool[report_dir_date] = {
                "filter_data": received_card_filter_data,
                "html_report": f"{report_dir_date}/index.html",
                "json_report": {},
                "root_dir": received_card_filter_data["s3_root_dir"],
            }

    _cards = await asyncio.gather(*[process_card(card_tuple) for card_tuple in final_cards_pool.items()])
    filtered_cards = [result for result in _cards if result is not None]
    # sorted_cards: list[dict]= sorted(filtered_cards, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
    return filtered_cards


async def process_card(card_tuple) -> Union[dict, None]:
    redis: redis_module.RedisClient = instances.redis
    redis_client: _redis.StrictRedis = instances.redis.redis_client

    card_date, card_value = card_tuple
    try:
        object_name = card_value["filter_data"].get("object_name")
        if not object_name:
            return None

        if not redis_client.hexists(test_reports_redis_cache_name, card_date):
            j_report = json.loads(S3.get_a_s3_object(object_name))
            del j_report["config"]  # remove config details from the report to reduce report size
            del j_report["suites"]  # remove suites from the report to reduce report size
            card_value["json_report"] = j_report
            await redis.create_reports_cache(test_reports_redis_cache_name, card_date, json.dumps(card_value))
            return card_value
        else:
            # logger.info(f"Card found in Redis cache: {card_date}")
            return None
    except (KeyError, json.JSONDecodeError):
        logger.info(f"Error processing card: {card_date}")
        return None


def download_s3_folder(s3_root_dir: str, bucket_name=aws_bucket_name) -> str:
    """
    Given a root_dir path for a folder in an S3 bucket, download all
    the objects inside root_dir to local, maintaining the same folder
    structure as in S3 bucket.
    """
    s3_objects = S3.list_all_s3_objects(bucket_name)
    test_report_dir = ""

    for obj in s3_objects:
        object_key = obj["Key"]

        if object_key.startswith(s3_root_dir):
            # Construct the local relative path from the object_key
            relative_path_parts = object_key[len(s3_root_dir) :].lstrip("/")
            test_report_dir = s3_root_dir.split("/")[-1]  # noqa: E201 Remove the test report root dir portion from the path parts. e.g. 'trading-apps/test_reports/api/12-31-2025_08-30-00_AM' -> '12-31-2025_08-30-00_AM'

            download_dir_root_path: str = "./"
            reports_dir_path = os.path.join(download_dir_root_path, test_reports_dir)  # "./test_reports"
            local_reports_dir_path = os.path.join(
                reports_dir_path, test_report_dir
            )  # "./test_reports/4-28-2025_10-01-41_AM"
            local_reports_dir_card_rel_path = os.path.join(local_reports_dir_path, relative_path_parts)

            local_dir_path = os.path.dirname(local_reports_dir_card_rel_path)
            if not os.path.exists(local_dir_path):
                os.makedirs(local_dir_path)

            S3.download_file(object_key, local_reports_dir_card_rel_path, bucket_name)

    logger.info(f"All objects from [{s3_root_dir}] in S3 bucket have been downloaded locally.")
    return test_report_dir
