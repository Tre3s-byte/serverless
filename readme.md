Stable Diffusion Serverless Worker with RunPod

This project deploys a Stable Diffusion v1.5 image generation worker using RunPod Serverless.
The worker receives a text prompt via HTTP request and returns a generated image encoded in base64.

The repository contains only the necessary files:

handler.py

Dockerfile

requirements.txt

No client script is required. You can interact directly using curl.

How It Works

The container starts and loads the Stable Diffusion model once.

RunPod listens for incoming jobs.

A request is sent to the endpoint.

The handler generates the image.

The image is returned as a base64 string inside JSON.

The endpoint must be used with /runsync to wait for the job to complete.

Project Structure

handler.py
Main serverless handler. Loads the model globally and processes incoming prompts.

Dockerfile
Builds the container image with all dependencies.

requirements.txt
Python dependencies required for the project.

Environment Variables

You must provide a HuggingFace token:

HF_TOKEN=your_huggingface_token

This is required to download the model:
runwayml/stable-diffusion-v1-5

Deploying to RunPod

Build and push your Docker image to Docker Hub.

Create a new Serverless Endpoint in RunPod.

Use your Docker image.

Set the required environment variable HF_TOKEN.

Deploy.

Sending a Request

Use the synchronous endpoint:

curl -s -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync

-H "Content-Type: application/json"
-H "Authorization: YOUR_RUNPOD_API_KEY"
-d '{"input":{"prompt":"cyberpunk city"}}'
| jq -r '.output.image_base64'
| base64 -d > image.png

This will generate image.png in your current directory.

Important: do not use /run unless you plan to manually poll the job status.

Example Input

{
"input": {
"prompt": "a futuristic cyberpunk city",
"steps": 30,
"guidance": 7.5
}
}

Parameters:

prompt, required
steps, optional, default 30
guidance, optional, default 7.5

Response Format

{
"status": "COMPLETED",
"output": {
"image_base64": "..."
}
}

The image must be decoded from base64 to PNG.

Notes

The model loads once per container start to improve performance.
GPU is used automatically if available.
For testing, always use /runsync to avoid handling queue polling manually.
