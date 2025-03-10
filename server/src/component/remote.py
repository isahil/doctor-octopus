import json
import os
from config import local_dir, test_reports_dir, test_reports_date_format
from src.util.date import less_or_eqaul_to_date_time
from src.util.s3 import S3

aws_bucket_name = os.environ.get("AWS_SDET_BUCKET_NAME")
reports_dir = os.path.join(local_dir, test_reports_dir)  # Full path to the local test reports directory


def get_a_s3_card_html_report(html) -> str:
    card = S3.get_a_s3_object(html)
    return card

def total_s3_objects() -> int:
    total = S3.list_all_s3_objects()
    return len(total)

async def get_all_s3_cards(sio, sid, filter: dict) -> list:
    """Get all report cards object from the S3 bucket"""
    environment_filter = filter.get("environment")
    day_filter = int(filter.get("day"))

    s3_objects = S3.list_all_s3_objects()
    results = []  # List that will be sent to the client
    cards = {}  # Temporary dictionary to store the reports
    # { 2024-12-29-10-33-40: { json_report: { "object_name": "path/to/s3/object", ... }, html_report: "name.html", "root_dir": "trading-apps/test_reports/api/2024-12-29-10-33-40" } }

    for obj in s3_objects:
        object_name = obj["Key"]
        path_parts = object_name.split("/")

        if len(path_parts) < 6:
            continue

        root_dir_parts = path_parts[:6]
        root_dir_path = "/".join(root_dir_parts)

        report_dir = path_parts[5]  # e.g. '12-31-2025_08-30-00_AM'
        environment = path_parts[3]  # e.g. 'dev'
        file_name = path_parts[-1]

        if environment_filter and environment_filter != environment:
            continue
        if not less_or_eqaul_to_date_time(report_dir, test_reports_date_format, day_filter):
            continue

        if report_dir not in cards:
            cards[report_dir] = {"json_report": {}, "html_report": "", "root_dir": root_dir_path}

        if file_name.endswith("report.json"):
            cards[report_dir]["json_report"] = {
                "object_name": object_name
            }  # Create a new folder in the reports dict to save the contents of the folder later
        if file_name.endswith("index.html"):
            cards[report_dir]["html_report"] = object_name

    for _, card in cards.items():
        try:
            object_name = card["json_report"]["object_name"]
            if object_name is False:
                print("no valid object")
        except KeyError:
            continue

        j_report = S3.get_a_s3_object(object_name)
        card["json_report"] = json.loads(j_report)  # Load the json report into the dictionary
        results.append(card)
        await sio.emit("cards", card, room=sid)
    sorted_test_results = sorted(results, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
    if len(sorted_test_results) == 0:
        await sio.emit("cards", False, room=sid)
    return sorted_test_results


def download_s3_folder(root_dir: str, bucket_name=aws_bucket_name) -> str:
    """
    Given a root_dir path for a folder in an S3 bucket, download all
    the objects inside root_dir to local, maintaining the same folder
    structure as in S3 bucket.
    """
    s3_objects = S3.list_all_s3_objects(bucket_name)
    test_report_dir = None

    for obj in s3_objects:
        object_key = obj["Key"]

        # Only process objects that start with root_dir
        if object_key.startswith(root_dir):
            # Construct the local relative path from the object_key
            relative_path_parts = object_key[len(root_dir) :].lstrip("/")
            test_report_dir = root_dir.split("/")[-1]  # noqa: E201 Remove the test report root dir portion from the path parts. e.g. 'trading-apps/test_reports/api/12-31-2025_08-30-00_AM' -> '12-31-2025_08-30-00_AM'
            local_root_dir = os.path.join(
                reports_dir, test_report_dir
            )  # Join root_dir with the local relative path, so local files end up in 'test_reports/root_dir/...' preserving subfolders
            local_path = os.path.join(local_root_dir, relative_path_parts)

            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            S3.download_file(object_key, local_path, bucket_name)

    print(f"All objects from [{root_dir}] in S3 bucket have been downloaded locally.")
    return test_report_dir
