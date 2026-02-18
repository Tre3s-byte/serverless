import runpod
import torch
from diffusers import StableDiffusionPipeline
import base64
from io import BytesIO
import os
from dotenv import load_dotenv

# Environment variables
load_dotenv()
token = os.getenv("HF_TOKEN")

# HF model
MODEL_ID = "runwayml/stable-diffusion-v1-5"

# Check if there is a GPU, use the CPU if not
device = "cuda" if torch.cuda.is_available() else "cpu"

# float32 for CPU, 16 for GPU (it will use less memory and be a little faster)
torch_dtype = torch.float16 if device == "cuda" else torch.float32

# SD pipeline; the model will be loaded once
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype = torch_dtype,
    use_auth_token=token
)

# Move the SD pipeline to device according to previous verification
pipe = pipe.to(device)

# Fragment it into parts avoiding out of memory error 
pipe.enable_attention_slicing()

# 1. Input validation and default values
def validate_input(event):
    # Extract prompt, without throwing error if not exists
    input_data = event.get("input", {})
    prompt = input_data.get("prompt")

    # Not prompt or just whitespace validation
    if not prompt or not prompt.strip():
        raise ValueError("No prompt provided")

    #Default values
    steps = int(input_data.get("steps", 30))
    guidance = float(input_data.get("guidance", 7.5))
    return prompt, steps, guidance


# 2. Image generation
def generate_image(prompt, steps, guidance):
    #Inference mode and autocast (better performance on gpu)
    with torch.inference_mode():
        if device == "cuda":
            with torch.cuda.amp.autocast():
                image = pipe(
                    prompt,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    width=512,
                    height=512
                ).images[0]
        else: #CPU
            image = pipe(
                prompt,
                num_inference_steps=steps,
                guidance_scale=guidance,
                width=512,
                height=512
            ).images[0]
    return image
# 3. PIL to base64 then to JSON
def encode_image(image):
    buffered = BytesIO() #Avoids temp file, will load to memory
    image.save(buffered, format="PNG") #Buffer binary data (PNG format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8") # Buffer data to base64 text 

#Serverless handler
def handler(event):
    try:
        prompt, steps, guidance = validate_input(event)
        image = generate_image(prompt, steps, guidance)
        image_b64 = encode_image(image)
        return {"image_base64": image_b64}
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})