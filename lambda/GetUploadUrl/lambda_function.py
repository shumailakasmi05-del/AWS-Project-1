import boto3
import json
import os
import uuid


s3 = boto3.client("s3")

# Set BUCKET_NAME as a Lambda environment variable.
BUCKET = os.environ["BUCKET_NAME"]


def lambda_handler(event, context):

    try:

        body = json.loads(
            event.get("body") or "{}"
        )

        filename = body.get("filename")

        if not filename:

            return response(
                400,
                {
                    "error":
                        "Filename is required"
                }
            )

        # Keep only the filename
        filename = os.path.basename(filename)

        # Create a unique filename
        unique_name = (
            f"{uuid.uuid4()}-{filename}"
        )

        key = f"uploads/{unique_name}"

        # Generate a temporary S3 upload URL
        upload_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET,
                "Key": key,
                "ContentType":
                    "application/octet-stream"
            },
            ExpiresIn=300
        )

        return response(
            200,
            {
                "upload_url":
                    upload_url,

                "key":
                    key,

                "filename":
                    unique_name
            }
        )

    except Exception as e:

        print(
            f"ERROR: {repr(e)}"
        )

        return response(
            500,
            {
                "error":
                    str(e)
            }
        )


def response(status_code, body):

    return {

        "statusCode":
            status_code,

        "headers": {

            "Content-Type":
                "application/json",

            "Access-Control-Allow-Origin":
                "*",

            "Access-Control-Allow-Headers":
                "Content-Type",

            "Access-Control-Allow-Methods":
                "POST,OPTIONS"
        },

        "body":
            json.dumps(body)
    }
