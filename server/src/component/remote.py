import asyncio
import time
import json
import os
from typing import Union
import redis as _redis
from config import (
    test_environments,
    test_protocols,
    test_reports_dir,
    test_reports_redis_key,
    rate_limit_file_batch_size,
)
from src.component.validation import validate
from src.utils.helper import performance_log
from src.utils.s3 import S3
from src.utils.logger import logger
from src.utils.env_loader import get_aws_sdet_bucket_name
from src.utils.date_time_helper import convert_unix_to_iso8601_time, get_unix_time
import src.utils.redis as redis_module

aws_bucket_name = get_aws_sdet_bucket_name()


def total_s3_objects() -> int:
    total = S3.list_all_s3_objects()
    return len(total)


@performance_log
async def get_cards_from_s3_and_cache(expected_filter_dict: dict):
    """Get all report cards object from the S3 bucket"""
    s3_objects = S3.list_all_s3_objects()
    transformed_cards = transform_s3_objects_to_filter_dict(s3_objects)
    validated_cards_dict = validate_transformed_cards_w_filter_dict(transformed_cards, expected_filter_dict)
    validated_cards_list = list(validated_cards_dict.items())
    await asyncio.gather(*[process_card(card_tuple) for card_tuple in validated_cards_list])


def transform_s3_objects_to_filter_dict(s3_objects: list[dict]) -> list[dict]:
    """Process only JSON report objects from S3 bucket"""
    return [card for s3_object in s3_objects if (card := transform_s3_object_to_filter_dict(s3_object)) is not None]


def transform_s3_object_to_filter_dict(s3_object: dict) -> Union[dict, None]:
    object_name = s3_object["Key"]
    path_parts = object_name.split("/")

    if (len(path_parts) < 6) or not object_name.endswith("report.json"):
        return None

    return {
        "object_name": object_name,  # 'trading-apps/test_reports/loan/qa/api/12-31-2025_08-30-00_AM/report.json'
        "app": path_parts[2],
        "product": path_parts[2],
        "environment": path_parts[3],
        "protocol": path_parts[4],
        "day": path_parts[5],
        "file_type": "json",
        "s3_root_dir": "/".join(path_parts[:6]),
    }


def validate_transformed_cards_w_filter_dict(transformed_cards: list[dict], expected_filter_dict: dict) -> dict:
    """Validate the received S3 object filter data against expected filter data"""
    validation_results = [(card, validate(card, expected_filter_dict)) for card in transformed_cards]
    validated_cards = [card for card, error in validation_results if error is None]

    cards_pool = {}  # { "report_dir_date": { "json_report": {"object_name": "object_name_value"}, "html_report": "object_name_value", "root_dir": "" }}
    for validated_card in validated_cards:
        report_dir_date = validated_card["day"]
        if report_dir_date not in cards_pool:
            cards_pool[report_dir_date] = {
                "filter_data": validated_card,
                "json_report": {},
                "root_dir": validated_card["s3_root_dir"],
            }

    return cards_pool


async def process_card(card_tuple: tuple[str, dict]) -> Union[dict, None]:
    """
    Check if the card is already cached in Redis. If not, download the JSON report from S3,
    process it, and cache it in Redis

    :param card_tuple: Tuple containing card date and card value
    """
    import instances

    redis: redis_module.RedisClient = instances.redis
    redis_client: _redis.StrictRedis = instances.redis.redis_client

    card_date, card_value = card_tuple
    protocol = card_value["filter_data"].get("protocol")
    try:
        object_name = card_value["filter_data"].get("object_name")
        environment = card_value["filter_data"].get("environment")
        if not object_name or not environment or not protocol:
            logger.error(f"object_name, environment, or protocol missing for protocol: {protocol} [{card_date}]")
            return
        reports_cache_key = f"{test_reports_redis_key}:{environment}:{protocol}"  # e.g. trading-apps-reports:qa:ui

        if not redis_client.hexists(reports_cache_key, card_date):
            j_report = json.loads(S3.get_a_s3_object(object_name))
            j_report = process_json(j_report, card_date)
            card_value["json_report"] = j_report
            logger.info(f"Caching card in Redis for protocol: {protocol} [{card_date}]")
            redis.create_card_cache(reports_cache_key, card_date, json.dumps(card_value))

    except (KeyError, json.JSONDecodeError) as e:
        logger.info(f"Error processing card for protocol: {protocol} [{card_date}] - {type(e).__name__} - {str(e)}")


def identify_runner(json_report: dict, card_date: str) -> str:
    """Identify the test runner from the JSON report structure. Must not use stats key as it is common across runners."""
    keys = list(json_report.keys())
    if "config" in keys and "suites" in keys:
        return "playwright"
    if "collectors" in keys and "tests" in keys:
        return "pytest"
    if "aggregate" in keys and "intermediate" in keys:
        return "artillery"
    else:
        logger.info(f"[{card_date}] Unable to identify test runner from JSON report structure.")
        return "unknown"


def process_json(json_report: dict, card_date: str) -> dict:
    """Process the JSON report to remove unnecessary details and normalize stats"""

    if "stats" not in json_report:
        json_report["stats"] = {"startTime": "", "expected": 0, "unexpected": 0, "skipped": 0, "flaky": 0}

    stats = json_report.get("stats", {})
    runner = identify_runner(json_report, card_date)
    stats["runner"] = runner

    if runner == "playwright":
        del json_report["config"]
        del json_report["suites"]

    if runner == "pytest":
        del json_report["collectors"]
        del json_report["tests"]
        summary = json_report.get("summary", {})  # e.g. {'passed': 10, 'failed': 2, 'deselected': 1, ...}
        duration = json_report.get("duration")
        stats["duration"] = duration

        for key, value in summary.items():
            if key == "passed":
                stats["expected"] = value
            elif key == "failed":
                stats["unexpected"] = value
            elif key == "deselected":
                stats["skipped"] = value
            else:
                stats[key] = value

    if runner == "artillery":
        aggregate = json_report.get("aggregate", {})
        counters = aggregate.get("counters")  # e.g. {'vusers.completed': 100, 'vusers.failed': 5, ...}
        duration = aggregate.get("lastCounterAt", 0) - aggregate.get("firstCounterAt", 0)
        stats["duration"] = duration
        # Use aggregate.firstCounterAt for startTime. Convert from milliseconds to seconds.
        first_counter_timestamp = aggregate.get("firstCounterAt")
        stats["startTime"] = (
            convert_unix_to_iso8601_time(first_counter_timestamp // 1000) if first_counter_timestamp else ""
        )

        del json_report["intermediate"]
        del aggregate["summaries"]
        del aggregate["histograms"]

        for key, value in counters.items():
            if key == "vusers.completed":
                stats["expected"] = value
            elif key == "vusers.failed":
                stats["unexpected"] = value
            else:
                stats[key] = value

    if not stats.get("startTime"):
        # Fall back: client card requires startTime to be set for sorting logic.
        time = convert_unix_to_iso8601_time(get_unix_time())
        stats["startTime"] = time
        logger.info(f"[{card_date}] has no startTime in stats, setting to current time: {time}")

    return json_report


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
        if s3_root_dir in object_key:
            folder.append(object_key)

    return folder


def download_s3_folder(s3_root_dir: str, bucket_name=aws_bucket_name, rate_limit=0) -> str:
    """
    Given a root_dir path for a folder in an S3 bucket, download all
    the objects inside root_dir to local, maintaining the same folder
    structure as in S3 bucket.
    """
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
            date_index = object_key.find(test_report_dir) # Find the index of the date folder in the object key
            if date_index != -1:
                # Extract everything after the date folder (e.g., 'index.html', 'subfolder/file.json')
                relative_path_parts = object_key[date_index + len(test_report_dir):].lstrip("/")
                local_report_card_dir_rel_path = create_local_report_dir(relative_path_parts)
                S3.download_file(object_key, local_report_card_dir_rel_path, bucket_name)

            if rate_limit > 0:
                logger.info(
                    f"S3 download folder batch {i // rate_limit_file_batch_size + 1} completed. Waiting for {rate_limit} seconds to avoid rate limiting."
                )
                time.sleep(rate_limit)
    logger.info(f"All objects from [{s3_root_dir}] in S3 bucket have been downloaded locally.")
    return test_report_dir


def get_cards_from_cache(expected_filter_data: dict) -> list[dict]:
    """Get the cards from the memory. If the memorty data doesn't match, fetch the cards from the cache"""
    import instances

    environment = expected_filter_data.get("environment")
    protocol = expected_filter_data.get("protocol")
    day = int(expected_filter_data.get("day", 1))

    if not environment or not protocol:
        logger.error(
            "Environment and Protocol must be specified in expected_filter_data for get_cards_from_cache function"
        )
        return []

    envs_to_check = test_environments if environment == "all" else [environment]
    protocols_to_check = test_protocols if protocol == "all" else [protocol]
    filtered_cards: list[dict] = []

    redis = instances.redis

    # Iterate through all environment and protocol combinations
    for env in envs_to_check:
        for proto in protocols_to_check:
            reports_cache_key = f"{test_reports_redis_key}:{env}:{proto}"  # e.g. trading-apps-reports:qa:ui
            logger.info(f"Fetch cards from cache env: {env} | day: {day} | protocol: {proto}")

            cached_cards = redis.get_all_cached_cards(reports_cache_key)
            if cached_cards and isinstance(cached_cards, dict):
                for _, received_card_data in cached_cards.items():
                    received_card_data = json.loads(received_card_data)
                    received_filter_data = received_card_data.get("filter_data")
                    error = validate(received_filter_data, expected_filter_data)
                    if error:
                        # logger.warning(f"Card filter data validation failed: {error}")
                        continue
                    filtered_cards.append(received_card_data)

    sorted_cards = sorted(filtered_cards, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
    return sorted_cards
