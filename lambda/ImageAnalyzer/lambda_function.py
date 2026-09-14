import boto3
import json
import urllib.parse
from datetime import datetime, timezone


s3 = boto3.client("s3")

rekognition = boto3.client("rekognition")

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

MODEL_ID = "amazon.nova-micro-v1:0"


def lambda_handler(event, context):

    bucket = event["Records"][0]["s3"]["bucket"]["name"]

    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"]
    )

    print(f"Processing: {key}")

    if not key.startswith("uploads/"):
        print("File is not inside uploads/ - skipping")

        return {
            "statusCode": 200,
            "body": "Skipped"
        }

    image = {
        "S3Object": {
            "Bucket": bucket,
            "Name": key
        }
    }

    try:

        # =====================================================
        # 1. OBJECT / SCENE DETECTION
        # =====================================================

        labels_response = rekognition.detect_labels(
            Image=image,
            MaxLabels=15,
            MinConfidence=70
        )

        objects = []

        for label in labels_response.get("Labels", []):

            objects.append({
                "name": label["Name"],
                "confidence": round(
                    label["Confidence"],
                    2
                )
            })

        # =====================================================
        # 2. FACE ANALYSIS
        # =====================================================

        faces_response = rekognition.detect_faces(
            Image=image,
            Attributes=["ALL"]
        )

        faces = []

        for index, face in enumerate(
            faces_response.get("FaceDetails", []),
            start=1
        ):

            emotions = []

            for emotion in face.get("Emotions", []):

                emotions.append({
                    "emotion": emotion["Type"],
                    "confidence": round(
                        emotion["Confidence"],
                        2
                    )
                })

            strongest_emotion = None

            if emotions:
                strongest_emotion = max(
                    emotions,
                    key=lambda x: x["confidence"]
                )

            faces.append({

                "face_id": index,

                "detection_confidence": round(
                    face["Confidence"],
                    2
                ),

                "estimated_age": {
                    "min": face.get(
                        "AgeRange",
                        {}
                    ).get("Low"),

                    "max": face.get(
                        "AgeRange",
                        {}
                    ).get("High")
                },

                "gender": face.get(
                    "Gender",
                    {}
                ).get("Value"),

                "smiling": face.get(
                    "Smile",
                    {}
                ).get("Value"),

                "eyes_open": face.get(
                    "EyesOpen",
                    {}
                ).get("Value"),

                "mouth_open": face.get(
                    "MouthOpen",
                    {}
                ).get("Value"),

                "eyeglasses": face.get(
                    "Eyeglasses",
                    {}
                ).get("Value"),

                "sunglasses": face.get(
                    "Sunglasses",
                    {}
                ).get("Value"),

                "strongest_emotion": strongest_emotion,

                "emotions": emotions
            })

        # =====================================================
        # 3. TEXT / OCR
        # =====================================================

        text_response = rekognition.detect_text(
            Image=image
        )

        text_detected = []

        for detection in text_response.get(
            "TextDetections",
            []
        ):

            if detection.get("Type") == "LINE":

                text_detected.append({

                    "text":
                        detection["DetectedText"],

                    "confidence":
                        round(
                            detection["Confidence"],
                            2
                        )
                })

        # =====================================================
        # 4. CONTENT MODERATION
        # =====================================================

        moderation_response = (
            rekognition.detect_moderation_labels(
                Image=image,
                MinConfidence=70
            )
        )

        moderation_labels = []

        for label in moderation_response.get(
            "ModerationLabels",
            []
        ):

            moderation_labels.append({

                "category":
                    label["Name"],

                "confidence":
                    round(
                        label["Confidence"],
                        2
                    )
            })

        if moderation_labels:
            safety_status = "Review Required"
        else:
            safety_status = "No Issues Detected"

        # =====================================================
        # 5. DATA FOR BEDROCK
        # =====================================================

        vision_data = {

            "objects": objects,

            "face_count":
                len(faces),

            "faces": faces,

            "text": text_detected,

            "moderation":
                moderation_labels
        }

        # =====================================================
        # 6. BEDROCK AI DESCRIPTION
        # =====================================================

        prompt = f"""
You are an image analysis assistant.

Create a concise, natural-language description of an image
using ONLY the verified computer-vision information below.

Do NOT invent details.

Mention:
- the main objects or scene
- number of people
- notable facial emotions when available
- visible text when available
- important safety information if applicable

Write 2-4 natural sentences.

Computer vision results:

{json.dumps(vision_data, indent=2)}
"""

        bedrock_response = bedrock.converse(

            modelId=MODEL_ID,

            messages=[
                {
                    "role": "user",

                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],

            inferenceConfig={

                "maxTokens": 200,

                "temperature": 0.2
            }
        )

        ai_description = (
            bedrock_response
            ["output"]
            ["message"]
            ["content"][0]
            ["text"]
        )

        # =====================================================
        # 7. CLEAN FINAL REPORT
        # =====================================================

        result = {

            "report_type":
                "AWS Image Analysis Report",

            "version":
                "1.0",

            "image": {

                "file_name":
                    key.split("/")[-1],

                "s3_key":
                    key
            },

            "summary": {

                "description":
                    ai_description
            },

            "objects": {

                "count":
                    len(objects),

                "detected":
                    objects
            },

            "faces": {

                "count":
                    len(faces),

                "detected":
                    faces
            },

            "text": {

                "detected":
                    len(text_detected) > 0,

                "items":
                    text_detected
            },

            "safety": {

                "status":
                    safety_status,

                "issues":
                    moderation_labels
            },

            "metadata": {

                "analyzed_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),

                "analysis_services": [

                    "Amazon Rekognition",

                    "Amazon Bedrock"
                ],

                "lambda_request_id":
                    context.aws_request_id
            }
        }

        # =====================================================
        # 8. SAVE REPORT TO S3
        # =====================================================

        filename = key.split("/")[-1]

        result_key = (
            f"results/{filename}.json"
        )

        s3.put_object(

            Bucket=bucket,

            Key=result_key,

            Body=json.dumps(
                result,
                indent=2
            ),

            ContentType="application/json"
        )

        print(
            f"Analysis complete: {result_key}"
        )

        print(
            f"AI Summary: {ai_description}"
        )

        return {

            "statusCode": 200,

            "body":
                json.dumps(result)
        }

    except Exception as e:

        print(
            f"ERROR: {str(e)}"
        )

        raise e
