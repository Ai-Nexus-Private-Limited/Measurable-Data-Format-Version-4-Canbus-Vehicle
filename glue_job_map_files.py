import boto3
import pandas as pd
import json
import s3fs
import hashlib

# AWS clients
s3_fs = s3fs.S3FileSystem()
sqs = boto3.client("sqs", region_name="ap-south-1")

QUEUE_URL = "https://sqs.ap-south-1.amazonaws.com/919739341273/telem-ingestion.fifo"
RAW_BUCKET = "canbus-telem-raw-eu"

# -----------------------------
# Load usecase CSV from S3
# -----------------------------
usecase_key = "config/usecase.csv"
usecase_path = f"s3://{RAW_BUCKET}/{usecase_key}"

df = pd.read_csv(usecase_path)

# -----------------------------
# Process per vehicle
# -----------------------------
for vehicle, vehicle_df in df.groupby("vehicle"):

    start_time = vehicle_df["start_time"].min()
    end_time = vehicle_df["end_time"].max()
    signals = vehicle_df["signal"].unique().tolist()

    # Find MF4 files
    mf4_files = s3_fs.glob(f"{RAW_BUCKET}/vehicle={vehicle}/**/*.mf4")

    if not mf4_files:
        print(f"No MF4 found for vehicle: {vehicle}")
        continue

    # POC: pick first MF4 file
    file_path = f"s3://{mf4_files[0]}"

    payload = {
        "vehicle": vehicle,
        "file_path": file_path,
        "signals": signals,
        "start_time": str(start_time),
        "end_time": str(end_time)
    }

    # FIFO queue requires deterministic deduplication ID
    dedup_id = hashlib.md5(
        f"{vehicle}-{file_path}-{start_time}-{end_time}".encode()
    ).hexdigest()

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageGroupId=f"vehicle-{vehicle}",
        MessageDeduplicationId=dedup_id,
        MessageBody=json.dumps(payload)
    )

    print(f"SQS message sent for vehicle: {vehicle}")

print("Glue job completed → SQS ready for ECS")
