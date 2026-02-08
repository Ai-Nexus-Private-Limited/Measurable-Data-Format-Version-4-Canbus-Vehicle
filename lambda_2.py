import json
import boto3
import os

ecs_client = boto3.client("ecs")

# Environment variables (configure in Lambda settings)
CLUSTER_NAME = os.environ["ECS_CLUSTER"]
TASK_DEFINITION = os.environ["TASK_DEFINITION"]
SUBNETS = os.environ["SUBNETS"].split(",")
SECURITY_GROUPS = os.environ["SECURITY_GROUPS"].split(",")

def lambda_handler(event, context):
    try:
        for record in event["Records"]:
            # 1️⃣ Parse SQS message
            body = json.loads(record["body"])

            vehicle_id = body["vehicle"]
            mf4_path = body["file_path"]
            signals = ",".join(body["signals"])
            start_time = body["start_time"]
            end_time = body["end_time"]

            print(f"Triggering ECS for {vehicle_id} | {mf4_path}")

            # 2️⃣ Run ECS Fargate Task
            response = ecs_client.run_task(
                cluster=CLUSTER_NAME,
                launchType="FARGATE",
                taskDefinition=TASK_DEFINITION,
                networkConfiguration={
                    "awsvpcConfiguration": {
                        "subnets": SUBNETS,
                        "securityGroups": SECURITY_GROUPS,
                        "assignPublicIp": "ENABLED"
                    }
                },
                overrides={
                    "containerOverrides": [
                        {
                            "name": "canbus-decoder",
                            "environment": [
                                {"name": "MF4_S3_PATH", "value": mf4_path},
                                {"name": "REQUESTED_SIGNALS", "value": signals},
                                {"name": "VEHICLE_ID", "value": vehicle_id},
                                {"name": "START_TIME", "value": start_time},
                                {"name": "END_TIME", "value": end_time}
                            ]
                        }
                    ]
                }
            )

            print("ECS Task Started:", response["tasks"][0]["taskArn"])

        return {"status": "SUCCESS"}

    except Exception as e:
        print("ERROR:", str(e))
        raise e
