import json
import os
from src.util.s3 import S3

def get_a_s3_card_html_report(html):
    card = S3.get_a_s3_object(html)
    return card

def get_all_s3_cards():
    ''' get all report cards from the S3 bucket's each object'''
    s3_objects = S3.list_s3_objects()
    reports_dir = [] # list that will be sent to the client

    # temporary dictionary to store the reports
    report_cards = {} # { folder_name: { json_report: { "object_name": object_name... }, html_report: "name.html" } }
    
    for obj in s3_objects:
        object_name = obj["Key"]
        folder_name = object_name.split("/")[-2]
        file_name = object_name.split("/")[-1]
        if folder_name not in report_cards:
            report_cards[folder_name] = {"json_report": {}, "html_report": ""}
        
        if file_name.endswith(".json"):
            report_cards[folder_name]["json_report"] = {"object_name": object_name} # Create a new folder in the reports dict to save the contents of the folder later
        if file_name.endswith(".html"):
            report_cards[folder_name]["html_report"] = object_name
    
    print(f"Total reports received from S3 bucket: {len(report_cards)}")

    for folder_name in report_cards.values():
            j_report = S3.get_a_s3_object(folder_name["json_report"]["object_name"])
            folder_name["json_report"] = json.loads(j_report)
            reports_dir.append(folder_name)
    
    return reports_dir.reverse()

def download_s3_objects(bucket_name):
    ''' download all objects from the S3 bucket '''
    print(f"Downloading objects from S3 bucket: {bucket_name}...")
    objects = S3.list_s3_objects(bucket_name)
    for obj in objects:
        object_name = obj["Key"]
        reports_dir = object_name.split("/")[-3]
        folder_name = object_name.split("/")[-2]
        file_name = object_name.split("/")[-1]
        if not os.path.exists(os.path.join(reports_dir, folder_name)):
            os.makedirs(os.path.join(reports_dir, folder_name))
        file_path = os.path.join(reports_dir, f"{folder_name}/{file_name}")
        
        S3.download_file(bucket_name, object_name, file_path)
