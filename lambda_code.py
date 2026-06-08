import json
import boto3

from datetime import datetime
import uuid
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)
s3 = boto3.client("s3")

BUCKET_NAME = "my-bedrock-logs-bucket"

def lambda_handler(event, context):

    method = event.get(
        "requestContext",
        {}
    ).get(
        "http",
        {}
    ).get(
        "method"
    )

    # Handle OPTIONS request
    if method == "OPTIONS":

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": ""
        }

    try:

        body = json.loads(event["body"])

        prompt_data = body["prompt"]

        payload = {
            "prompt": prompt_data,
            "max_gen_len": 512,
            "temperature": 0.5,
            "top_p": 0.9
        }

        response = bedrock.invoke_model(
            modelId="meta.llama3-70b-instruct-v1:0",
            body=json.dumps(payload),
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(
            response["body"].read()
        )

        response_text = response_body["generation"]
           # Create log object
        log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": str(uuid.uuid4()),
        "user_prompt": user_prompt,
        "bedrock_response": model_response
        }

      # S3 object path
    s3_key = f"logs/{datetime.utcnow().strftime('%Y/%m/%d')}/{uuid.uuid4()}.json"

    # Upload to S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(log_data),
        ContentType="application/json"
    )

    return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "response": response_text
            })
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }