import json
import os
from concurrent.futures import ThreadPoolExecutor
from config import local_dir, test_reports_dir
from src.util.s3 import S3
from src.component.card.validation import validate

aws_bucket_name = os.environ.get("AWS_SDET_BUCKET_NAME")
reports_dir = os.path.join(local_dir, test_reports_dir)  # Full path to the local test reports directory


def get_a_s3_card_html_report(html) -> str:
    card = S3.get_a_s3_object(html)
    return card

def total_s3_objects() -> int:
    total = S3.list_all_s3_objects()
    return len(total)

async def get_all_s3_cards(sio, sid, expected_filter_data: dict) -> list:
    """Get all report cards object from the S3 bucket with improved performance"""
    
    def process_s3_object(obj):
        object_name = obj["Key"]
        path_parts = object_name.split("/")
        
        if len(path_parts) < 6:
            return None
            
        return {
            "object_name": object_name,
            "report_dir_date": path_parts[5],
            "protocol": path_parts[4],
            "environment": path_parts[3],
            "app": path_parts[2],
            "file_type": "json" if object_name.endswith("report.json") else "html" if object_name.endswith("index.html") else None,
            "root_dir": "/".join(path_parts[:6])
        }

    # Get all S3 objects in parallel
    s3_objects = S3.list_all_s3_objects()
    
    # Process objects in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        processed_objects = list(filter(None, executor.map(process_s3_object, s3_objects)))
    
    # Group objects by report_dir_date
    grouped_objects = {}
    for obj in processed_objects:
        received_filter_data = {
            "app": obj["app"],
            "environment": obj["environment"],
            "protocol": obj["protocol"],
            "day": obj["report_dir_date"],
        }
        
        if validate(received_filter_data, expected_filter_data):
            continue
            
        if obj["file_type"]:
            if obj["report_dir_date"] not in grouped_objects:
                grouped_objects[obj["report_dir_date"]] = {
                    "json_report": {},
                    "html_report": "",
                    "root_dir": obj["root_dir"]
                }
            
            if obj["file_type"] == "json":
                grouped_objects[obj["report_dir_date"]]["json_report"] = {"object_name": obj["object_name"]}
            else:
                grouped_objects[obj["report_dir_date"]]["html_report"] = obj["object_name"]

    # Process JSON reports in parallel
    async def process_card(card):
        try:
            object_name = card["json_report"].get("object_name")
            if not object_name:
                return None
            
            j_report = S3.get_a_s3_object(object_name)
            card["json_report"] = json.loads(j_report)
            await sio.emit("cards", card, room=sid)
            return card
        except (KeyError, json.JSONDecodeError):
            return None

    # Process cards concurrently
    results = []
    for card in grouped_objects.values():
        if processed := await process_card(card):
            results.append(processed)

    # Sort results by start time
    sorted_results = sorted(
        results,
        key=lambda x: x["json_report"]["stats"]["startTime"],
        reverse=True
    )

    if not sorted_results:
        await sio.emit("cards", False, room=sid)
    
    return sorted_results

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
