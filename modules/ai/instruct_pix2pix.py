import io
import torch
from PIL import Image
import requests
from io import BytesIO
from diffusers import ControlNetModel, StableDiffusionControlNetPipeline, UniPCMultistepScheduler

def transform_image_with_prompt(image, prompt):
    # Set the device for computation
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Initialize the ControlNet model and pipeline
    checkpoint = "lllyasviel/control_v11e_sd15_ip2p"
    controlnet = ControlNetModel.from_pretrained(checkpoint, torch_dtype=torch.float16).to(device)
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16,
        safety_checker = None,
        requires_safety_checker = False
    ).to(device)

    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_model_cpu_offload()

    # Use a fixed generator for reproducibility, remove or modify for varied results
    generator = torch.manual_seed(0)

    # Generate the image based on the prompt
    transformed_image = pipe(prompt, num_inference_steps=30, generator=generator, image=image).images[0]

    # Convert PIL image to byte array
    img_io = io.BytesIO()
    transformed_image.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

