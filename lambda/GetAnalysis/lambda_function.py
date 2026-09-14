import boto3
import json
import os


s3 = boto3.client("s3")

# Set BUCKET_NAME as a Lambda environment variable.
BUCKET = os.environ["BUCKET_NAME"]


def lambda_handler(event, context):

    try:

        # Get query parameters
        query = event.get(
            "queryStringParameters"
        ) or {}

        filename = query.get("file")

        # Make sure a filename was provided
        if not filename:

            return make_response(
                400,
                {
                    "error":
                        "Missing file parameter"
                }
            )

        # Only allow the filename itself
        filename = filename.split("/")[-1]

        # Location of the JSON result
        result_key = (
            f"results/{filename}.json"
        )

        # Get result from S3
        s3_response = s3.get_object(

            Bucket=BUCKET,

            Key=result_key
        )

        # Read JSON
        data = json.loads(

            s3_response["Body"]
            .read()
            .decode("utf-8")
        )

        # Return JSON to dashboard
        return make_response(
            200,
            data
        )

    except s3.exceptions.NoSuchKey:

        return make_response(
            404,
            {
                "error":
                    "Analysis not found"
            }
        )

    except Exception as e:

        print(
            f"ERROR: {str(e)}"
        )

        return make_response(
            500,
            {
                "error":
                    "Internal server error"
            }
        )


def make_response(status_code, body):

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
                "GET,OPTIONS"
        },

        "body":
            json.dumps(body)
    }
