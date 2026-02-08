import boto3

glue = boto3.client("glue")

def lambda_handler(event, context):
    response = glue.start_job_run(
        JobName="glue job map files",
        Arguments={
            "--env": "prod",
            "--run_date": "2026-01-19"
        }
    )

    return {
        "status": "started",
        "job_run_id": response["JobRunId"]
    }
