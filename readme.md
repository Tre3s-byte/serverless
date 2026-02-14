<p align="center">
  <h1 align="center">Stable Diffusion Serverless Worker</h1>
  <p align="center">
    RunPod Serverless · Stable Diffusion v1.5 · GPU Ready
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/RunPod-Serverless-purple" />
  <img src="https://img.shields.io/badge/Model-StableDiffusion_v1.5-blue" />
  <img src="https://img.shields.io/badge/GPU-CUDA-green" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" />
</p>

---

## Overview

This project deploys a **Stable Diffusion v1.5** image generation worker using **RunPod Serverless**.

The worker:

- Receives a text prompt via HTTP request
- Generates an image
- Returns it encoded as base64 inside JSON

No client script is required. Interaction is done directly using `curl`.

---

## Architecture

Client (curl)
│
▼
RunPod Serverless Endpoint
│
▼
handler.py
│
▼
Stable Diffusion Pipeline
│
▼
Base64 Image → JSON Response

yaml
Copy code

The model loads once when the container starts for better performance.

---

## Project Structure

.
├── handler.py
├── Dockerfile
└── requirements.txt

yaml
Copy code

**handler.py**  
Main serverless entry point. Loads the model globally and processes prompts.

**Dockerfile**  
Defines the container environment.

**requirements.txt**  
Python dependencies.

---

## Environment Variable

You must provide a HuggingFace token:

````bash
HF_TOKEN=your_huggingface_token
Required to download:

bash
Copy code
runwayml/stable-diffusion-v1-5
Deployment
Build and push your Docker image to Docker Hub.

Create a new Serverless Endpoint in RunPod.

Select your Docker image.

Add HF_TOKEN as environment variable.

Deploy.

Sending a Request
Use the synchronous endpoint:

bash
Copy code
curl -s -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_RUNPOD_API_KEY" \
  -d '{"input":{"prompt":"cyberpunk city"}}' \
| jq -r '.output.image_base64' \
| base64 -d > image.png
This will generate image.png in your current directory.

Important:
Use /runsync to wait for completion.
Do not use /run unless you implement job polling.

Example Input
json
Copy code
{
  "input": {
    "prompt": "a futuristic cyberpunk city",
    "steps": 30,
    "guidance": 7.5
  }
}
Parameters
Parameter	Required	Default	Description
prompt	Yes	—	Text description
steps	No	30	Inference steps
guidance	No	7.5	Guidance scale

Response Format
json
Copy code
{
  "status": "COMPLETED",
  "output": {
    "image_base64": "..."
  }
}
The image must be decoded from base64 to PNG.

Performance Notes
Model loads once per container start.

Uses GPU automatically if available.

Mixed precision enabled on CUDA.

Optimized for 512x512 generation.

<p align="center"> Built for clean, minimal serverless inference. </p> ```
````
