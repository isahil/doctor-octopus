import json
import os
from config import local_dir, test_reports_dir, test_reports_date_format
from src.util.date import less_or_qaul_to_date_time
from src.util.s3 import S3

aws_bucket_name = os.environ.get('AWS_SDET_BUCKET_NAME')
reports_dir = os.path.join(local_dir, test_reports_dir) # Full path to the local test reports directory

def get_a_s3_card_html_report(html) -> str:
    card = S3.get_a_s3_object(html)
    return card

def get_all_s3_cards(filter: int) -> list:
    ''' Get all report cards object from the S3 bucket'''
    s3_objects = S3.list_all_s3_objects()
    print(f"Total objects found in SDET S3 bucket: {len(s3_objects)}")
    test_results = [] # List that will be sent to the client
    report_cards = {}  # Temporary dictionary to store the reports
    # { 2024-12-29-10-33-40: { json_report: { "object_name": "path/to/s3/object", ... }, html_report: "name.html", "root_dir": "trading-apps/test_reports/api/2024-12-29-10-33-40" } }
    
    for obj in s3_objects:
        object_name = obj["Key"]
        path_parts = object_name.split("/")
        if len(path_parts) < 4: continue
        root_dir_parts = path_parts[:4]
        report_dir = root_dir_parts[-1] # e.g. '12-31-2025_08-30-00_AM'

        if not less_or_qaul_to_date_time(report_dir, test_reports_date_format, filter):
            continue

        root_dir = "/".join(path_parts[:4])
        dir_name = path_parts[3]
        file_name = path_parts[-1]

        if dir_name not in report_cards:
            report_cards[dir_name] = {"json_report": {}, "html_report": "", "root_dir": root_dir}
        
        if file_name.endswith("report.json"):
            report_cards[dir_name]["json_report"] = {"object_name": object_name} # Create a new folder in the reports dict to save the contents of the folder later
        if file_name.endswith("index.html"):
            report_cards[dir_name]["html_report"] = object_name

    for dir_key, dir_value in report_cards.items():
            try:
                object_name = dir_value["json_report"]["object_name"]
                if object_name is False: print(f"no valid object")
            except KeyError:
                continue
            
            j_report = S3.get_a_s3_object(object_name)
            dir_value["json_report"] = json.loads(j_report) # Load the json report into the dictionary
            test_results.append(dir_value)
    sorted_test_results = sorted(test_results, key=lambda x: x["json_report"]["stats"]["startTime"], reverse=True)
    return sorted_test_results

def download_s3_folder(root_dir: str, bucket_name = aws_bucket_name) -> str:
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
            relative_path_parts = object_key[len(root_dir):].lstrip('/')
            test_report_dir = root_dir.split('/')[-1] # Remove the test report root dir portion from the path parts. e.g. 'trading-apps/test_reports/api/12-31-2025_08-30-00_AM' -> '12-31-2025_08-30-00_AM'
            local_root_dir = os.path.join(reports_dir, test_report_dir) # Join root_dir with the local relative path, so local files end up in 'test_reports/root_dir/...' preserving subfolders
            local_path = os.path.join(local_root_dir, relative_path_parts)

            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            
            S3.download_file(object_key, local_path, bucket_name)

    print(f"All objects from [{root_dir}] in S3 bucket have been downloaded locally.")
    return test_report_dir
    