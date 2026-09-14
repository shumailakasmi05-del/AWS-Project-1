# AWS-Project-1
Serverless AI Image Analysis Platform
# AWS Serverless AI Image Analysis Platform

A serverless image analysis application built with AWS that automatically analyzes uploaded images using **Amazon Rekognition** and **Amazon Bedrock** and displays the results in a web dashboard.

Project Overview

Users select an image from the web dashboard and upload it.

The application then:

1. Generates a secure **S3 presigned upload URL**
2. Uploads the image to an S3 `uploads/` folder
3. Automatically triggers an **AWS Lambda** function
4. Uses **Amazon Rekognition** to analyze the image
5. Uses **Amazon Bedrock** to generate an AI description
6. Saves the analysis as JSON in S3
7. Retrieves the results through **API Gateway**
8. Displays the results in the web dashboard

Architecture

```text
User
 │
 ▼
Web Dashboard
 │
 │ POST /upload
 ▼
API Gateway
 │
 ▼
Lambda — GetUploadUrl
 │
 ▼
S3
 │
 │ Image uploaded
 ▼
Lambda — ImageAnalyzer
 │
 ├──► Amazon Rekognition
 │     ├── Object Detection
 │     ├── Face Analysis
 │     ├── Text Detection
 │     └── Content Moderation
 │
 └──► Amazon Bedrock
       └── AI Image Summary
 │
 ▼
S3
 │
 │ JSON Analysis Report
 ▼
API Gateway
 │
 │ GET /analysis
 ▼
Web Dashboard
```

AWS Services Used

| Service                | Purpose                                     |
| ---------------------- | ------------------------------------------- |
| **Amazon S3**          | Stores uploaded images and analysis results |
| **AWS Lambda**         | Runs the image processing and API logic     |
| **Amazon Rekognition** | Analyzes images                             |
| **Amazon Bedrock**     | Generates natural-language AI summaries     |
| **Amazon API Gateway** | Provides API endpoints for the dashboard    |
| **AWS IAM**            | Controls permissions between AWS services   |

Image Analysis

Amazon Rekognition provides:

* Object and scene detection
* Face detection
* Estimated age range
* Gender estimation
* Smile detection
* Eye/mouth state
* Emotion detection
* OCR/text detection
* Content moderation

The application converts these results into a structured JSON report.

AI Summary

The structured Rekognition results are sent to **Amazon Bedrock**.

Bedrock generates a human-readable description such as:

> "The image features a portrait of a happy man in his early thirties..."

This allows the application to combine traditional computer vision with generative AI.

Security & AWS Architecture

The project uses:

* IAM roles for Lambda permissions
* S3 presigned URLs for browser uploads
* Private S3 objects
* API Gateway endpoints
* CORS configuration for browser communication
* S3 event-based Lambda processing

The browser does **not** receive AWS credentials.

Instead, the backend generates a temporary presigned URL that allows the browser to upload the selected image directly to S3.

Project Structure

```text
AWS-Image-Analysis-Dashboard/
│
├── index.html
├── style.css
├── app.js
└── start-dashboard.bat
```

### Frontend

**index.html**

* Dashboard structure
* Image upload interface
* Analysis sections

**style.css**

* Dashboard styling
* Responsive layout
* Cards and analysis sections

**app.js**

* Sends upload request to API Gateway
* Uploads image using the presigned S3 URL
* Polls for analysis results
* Displays the returned JSON data

API Endpoints

### POST `/upload`

Creates a temporary S3 presigned URL.

Example request:

```json
{
  "filename": "example.jpg"
}
```

Example response:

```json
{
  "upload_url": "https://...",
  "key": "uploads/unique-file-name.jpg",
  "filename": "unique-file-name.jpg"
}
```

### GET `/analysis`

Retrieves the completed analysis.

Example:

```text
GET /analysis?file=unique-file-name.jpg
```

What I Learned

This project gave me hands-on experience with:

* Serverless AWS architecture
* Lambda functions
* S3 event triggers
* IAM permissions
* API Gateway
* Presigned S3 URLs
* Amazon Rekognition
* Amazon Bedrock
* REST API development
* CORS
* Asynchronous cloud processing
* Connecting a frontend application to AWS services

Project Goal

The goal of this project was to build a practical serverless AI application using multiple AWS services together rather than using a single AI API.

It demonstrates how AWS services can be combined to create an automated, scalable image-processing workflow without managing servers.

Technologies

**AWS:**
S3 • Lambda • API Gateway • Rekognition • Bedrock • IAM

**Frontend:**
HTML • CSS • JavaScript

**AI/ML:**
Computer Vision • OCR • Generative AI • Content Moderation

Cost Note

This project uses AWS services that can incur charges depending on usage. Keep testing volumes small and monitor AWS billing when experimenting with the application.
## Demo

### Dashboard

![Dashboard](screenshots/dashboard.png)

### Uploading an Image

![Upload](screenshots/upload.png)

### AI Analysis Results

![Analysis Results](screenshots/analysis.png)
