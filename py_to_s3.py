import boto3
import os
import json

AWS_REGION = "ap-south-1"
S3_BUCKET = "canbus-telem-raw-eu"
LOCAL_FOLDER = os.getcwd()  # Change to your local folder
aws_config_path = r"C:\Users\ADMIN\OneDrive\Desktop\Project2\Measurable-Data-Format-Version-4-Canbus-Vehicle\aws_config.json"


def get_aws_keys():
    try:
        file=open(file=aws_config_path, mode="r")
        data = json.load(file)
        return data["aws_access_key"], data["aws_secret_access_key"]
    finally:
        if "file" in locals():
            file.close()

def upload_folder_to_s3(local_folder, bucket, aws_access_key, aws_secret_access_key):
    s3_client = boto3.client("s3", region_name=AWS_REGION, aws_access_key=aws_access_key, aws_secret_access_key=aws_secret_access_key)

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            
            # Create S3 object path relative to folder
            relative_path = os.path.relpath(local_path, local_folder)
            s3_path = relative_path.replace("\\", "/")  # for Windows paths
            
            try:
                s3_client.upload_file(local_path, bucket, s3_path)
                print(f"Uploaded: {local_path} → s3://{bucket}/{s3_path}")
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")


aws_access_key, aws_secret_access_key = get_aws_keys()
upload_folder_to_s3(LOCAL_FOLDER, S3_BUCKET, aws_access_key, aws_secret_access_key)
