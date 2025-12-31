import asyncio
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Union
import redis as _redis
from config import (
    test_reports_dir,
    test_reports_redis_key,
    rate_limit_file_batch_size,
)
from src.component.validation import validate
from src.utils.s3 import S3
from src.utils.logger import logger
from src.utils.env_loader import get_aws_sdet_bucket_name
import src.utils.redis as redis_module

aws_bucket_name = get_aws_sdet_bucket_name()

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
        "object_name": object_name, # 'trading-apps/test_reports/loan/qa/api/12-31-2025_08-30-00_AM/report.json'
        "app": path_parts[2],
        "product": path_parts[2],
        "environment": path_parts[3],
        "protocol": path_parts[4],
        "day": path_parts[5],
        "file_type": "json",
        "s3_root_dir": "/".join(path_parts[:6]),
    }


async def get_all_s3_cards(expected_filter_data: dict, rate_limit_wait=0) -> list[dict]:
    """Get all report cards object from the S3 bucket"""

    s3_objects = S3.list_all_s3_objects()

    # Process objects in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        received_cards = list(filter(None, executor.map(format_s3_object_filter_data, s3_objects)))

    # Group objects by report_dir_date. Do we need html_report key since json_report has the value?
    cards_pool = {}  # { "report_dir_date": { "json_report": {"object_name": "object_name_value"}, "html_report": "object_name_value", "root_dir": "" }}
    for received_card in received_cards:
        error = validate(received_card, expected_filter_data)
        if error:
            continue

        report_dir_date = received_card["day"]
        if report_dir_date not in cards_pool:
            cards_pool[report_dir_date] = {
                "filter_data": received_card,
                "html_report": f"{report_dir_date}/index.html",
                "json_report": {},
                "root_dir": received_card["s3_root_dir"],
            }

    report_cards = list(cards_pool.items())
    processed_cards = await asyncio.gather(*[process_card(card_tuple) for card_tuple in report_cards])
    finalized_cards = [processed_card for processed_card in processed_cards if processed_card is not None]
    return finalized_cards


async def process_card(card_tuple) -> Union[dict, None]:
    import instances

    redis: redis_module.RedisClient = instances.redis
    redis_client: _redis.StrictRedis = instances.redis.redis_client

    card_date, card_value = card_tuple
    try:
        object_name = card_value["filter_data"].get("object_name")
        environment = card_value["filter_data"].get("environment", "")
        reports_cache_key = f"{test_reports_redis_key}:{environment}"  # e.g. trading-apps-reports:qa
        if not object_name:
            return None

        if not redis_client.hexists(reports_cache_key, card_date):
            j_report = json.loads(S3.get_a_s3_object(object_name))

            del j_report["config"]  # remove config details from the report to reduce report size
            del j_report["suites"]  # remove suites from the report to reduce report size
            
            card_value["json_report"] = j_report
            redis.create_card_cache(reports_cache_key, card_date, json.dumps(card_value))
            return card_value
        else:
            # logger.info(f"Card found in Redis cache: {card_date}")
            return None
    except (KeyError, json.JSONDecodeError):
        logger.info(f"Error processing card: {card_date}")
        return None


def find_s3_report_dir_objects(s3_root_dir: str, bucket_name=aws_bucket_name) -> list[str]:
    """
    Given a root_dir path for a folder in an S3 bucket, find all
    the objects inside root_dir and return a list of object keys if
    the folder exists in the S3 bucket.
    """
    s3_objects = S3.list_all_s3_objects(bucket_name)
    folder = []
    for obj in s3_objects:
        object_key = obj["Key"]
        if object_key.startswith(s3_root_dir):
            folder.append(object_key)

    return folder


def download_s3_folder(s3_root_dir: str, bucket_name=aws_bucket_name, rate_limit=0) -> str:
    """
    Given a root_dir path for a folder in an S3 bucket, download all
    the objects inside root_dir to local, maintaining the same folder
    structure as in S3 bucket.
    """
    # s3_objects = S3.list_all_s3_objects(bucket_name)
    s3_report_dir_objects = find_s3_report_dir_objects(s3_root_dir, bucket_name)
    test_report_dir = s3_root_dir.split("/")[-1]  # noqa: E201 Get the test report main dir portion from the path parts. e.g. 'trading-apps/test_reports/api/12-31-2025_08-30-00_AM' -> '12-31-2025_08-30-00_AM'

    def create_local_report_dir(relative_path: str) -> str:
        download_dir_root_path: str = "./"
        reports_dir_path = os.path.join(download_dir_root_path, test_reports_dir)  # "./test_reports"
        local_reports_dir_path = os.path.join(
            reports_dir_path, test_report_dir
        )  # "./test_reports/4-28-2025_10-01-41_AM"
        local_report_dir_rel_path = os.path.join(local_reports_dir_path, relative_path)

        local_report_sub_dir_path = os.path.dirname(local_report_dir_rel_path)
        if not os.path.exists(local_report_sub_dir_path):
            os.makedirs(local_report_sub_dir_path, exist_ok=True)
        return local_report_dir_rel_path

    for i in range(0, len(s3_report_dir_objects), rate_limit_file_batch_size):
        object_batch = s3_report_dir_objects[i : i + rate_limit_file_batch_size]
        for object_key in object_batch:
            # Transform the S3 object key into a local relative path by removing the s3_root_dir prefix and any leading slash.
            # For example, 'trading-apps/test_reports/api/12-31-2025_08-30-00_AM/some_folder/some_file.ext'
            # becomes 'some_folder/some_file.ext' for local storage.
            relative_path_parts = object_key[len(s3_root_dir) :].lstrip("/")
            local_report_card_dir_rel_path = create_local_report_dir(relative_path_parts)
            S3.download_file(object_key, local_report_card_dir_rel_path, bucket_name)

            if rate_limit > 0:
                logger.info(
                    f"S3 download folder batch {i // rate_limit_file_batch_size + 1} completed. Waiting for {rate_limit} seconds to avoid rate limiting."
                )
                time.sleep(rate_limit)
    logger.info(f"All objects from [{s3_root_dir}] in S3 bucket have been downloaded locally.")
    return test_report_dir
