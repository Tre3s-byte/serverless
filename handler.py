import runpod
import torch
from diffusers import StableDiffusionPipeline
import base64
from io import BytesIO

#Load model globally so it's only loaded once per container
MODEL_ID = "runwayml/stable-diffusion-v1-5"

device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype = torch_dtype
)

pipe = pipe.to(device)
pipe.enable_attention_slicing()

# 1. Validate input
def validate_input(event):
    input_data = event.get("input", {})
    prompt = input_data.get("prompt")
    #Validate prompt to ensure it's not empty or just whitespace
    if not prompt or not prompt.strip():
        raise ValueError("No prompt provided")
    #Set default steps and guidance
    steps = int(input_data.get("steps", 30))
    guidance = float(input_data.get("guidance", 7.5))
    return prompt, steps, guidance


# 2. Generate image with Stable Diffusion
def generate_image(prompt, steps, guidance):
    #Added inference mode and autocast for better performance on GPU
    with torch.inference_mode():
        if device == "cuda":
            with torch.cuda.amp.autocast():
                image = pipe(
                    prompt,
                    num_inference_steps=steps,
                    guidance_scale=guidance
                    width=512,
                    height=512
                ).images[0] # Take first generated image
        else:
            image = pipe(
                prompt,
                num_inference_steps=steps,
                guidance_scale=guidance
                width=512,
                height=512
            ).images[0]
    return image
# 3. Encode to base64 and return
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def handler(event):
    try:
        prompt, steps, guidance = validate_input(event)
        image = generate_image(prompt, steps, guidance)
        image_b64 = encode_image(image)
        return {"image_base64": image_b64}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test local
    result = handler({
        "input": {
            "prompt": "a cyberpunk cat",
            "steps": 20,
            "guidance": 7.5
        }
    })
    print(result)
else:
    # Modo RunPod
    runpod.serverless.start({"handler": handler})