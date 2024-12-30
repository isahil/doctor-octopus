import json
import os
from src.util.s3 import S3

aws_bucket_name = os.environ.get('AWS_BUCKET_NAME')
local_dir = os.environ.get('LOCAL_DIRECTORY', "../../") # path to test results directory can be changed in the .env file
reports_dir_name = os.environ.get("TEST_REPORTS_DIR", "test_reports") # test reports directory can be changed in the .env file
reports_dir = os.path.join(local_dir, reports_dir_name)

def get_a_s3_card_html_report(html):
    card = S3.get_a_s3_object(html)
    return card

def get_all_s3_cards():
    ''' Get all report cards from the S3 bucket's each object'''
    s3_objects = S3.list_s3_objects()
    reports_dir = [] # list that will be sent to the client
    # temporary dictionary to store the reports
    report_cards = {} # { folder_name: { json_report: { "object_name": object_name... }, html_report: "name.html" } }
    
    for obj in s3_objects:
        object_name = obj["Key"]
        path_parts = object_name.split("/")
        root_dir = "/".join(path_parts[:4])

        test_report_dir = path_parts[3]
        file_name = path_parts[-1]
        if test_report_dir not in report_cards:
            report_cards[test_report_dir] = {"json_report": {}, "html_report": "", "root_dir": root_dir}
        
        if file_name.endswith("report.json"):
            report_cards[test_report_dir]["json_report"] = {"object_name": object_name} # Create a new folder in the reports dict to save the contents of the folder later
        if file_name.endswith("index.html"):
            report_cards[test_report_dir]["html_report"] = object_name

    for test_report_dir in report_cards.values():
            try:
                object_name = test_report_dir["json_report"]["object_name"]
                if object_name is False: print(f"no valid object")
            except KeyError:
                del report_cards[test_report_dir]
                continue
            
            j_report = S3.get_a_s3_object(object_name)
            test_report_dir["json_report"] = json.loads(j_report)
            reports_dir.append(test_report_dir)
    return reports_dir[::-1]

def download_s3_folder(root_dir: str, bucket_name = aws_bucket_name):
    """
    Given a root_dir path for a folder in an S3 bucket, download all
    the objects inside root_dir to local, maintaining the same folder 
    structure as in S3 bucket.
    """
    # List all objects in the S3 bucket
    s3_objects = S3.list_s3_objects(bucket_name)
    
    # Loop through each object
    for obj in s3_objects:
        object_key = obj["Key"]
        
        # Only process objects that start with root_dir
        if object_key.startswith(root_dir):
            # Construct the local relative path based on object_key
            # Remove the leading 'root_dir/' portion
            relative_path = object_key[len(root_dir):].lstrip('/')
            # Join root_dir with the relative path, so local files end up in root_dir/... 
            # preserving subfolders
            test_report_dir = root_dir.split('/')[-1]
            local_root_dir = os.path.join(reports_dir, test_report_dir)
            local_path = os.path.join(local_root_dir, relative_path)

            # Create local directories if needed
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            
            # Download the file from S3 to local_path
            S3.download_file(object_key, local_path, bucket_name)

    print(f"All objects from {root_dir} in S3 bucket have been downloaded locally.")
    return test_report_dir
    