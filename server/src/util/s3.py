import os
import boto3

aws_bucket_name = os.environ.get('AWS_BUCKET_NAME')
aws_bucket_region = os.environ.get('AWS_BUCKET_REGION')
aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

class S3Client:
    def __init__(self):
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_bucket_region
        )
        self.S3 = session.client('s3')

    def get_a_s3_object(self, object_name, bucket_name = aws_bucket_name) -> bytes:
        '''
        # Call S3 client to get a s3 object
        '''
        response = self.S3.get_object(Bucket=bucket_name, Key=object_name)
        return response['Body'].read()
    
    def list_s3_objects(self, bucket_name = aws_bucket_name) -> list:
        '''
        # Call S3 client to list s3 objects
        '''
        response = self.S3.list_objects_v2(Bucket=bucket_name)
        objects = response.get('Contents', [])
        # for obj in objects:
        #     print(f"Key: {obj['Key']}, Size: {obj['Size']}")
        return objects

    def download_file(self, object_key, local_path, bucket_name = aws_bucket_name) -> None:
        '''
        # Call S3 client to download a file
        '''
        self.S3.download_file(bucket_name, object_key, local_path)
    
S3 = S3Client()
