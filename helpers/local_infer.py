import torch
from diffusers import StableDiffusionPipeline
import uuid
import os

# --- Module‐level cache for the pipeline ---
_pipe = None

def load_pipeline():
    global _pipe
    if _pipe is None:
        print(">> Loading model... This can take a few minutes the first time.")
        model_id = "hakurei/waifu-diffusion"
        # Load the pipeline
        _pipe = StableDiffusionPipeline.from_pretrained(model_id)

        # Determine device
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Only enable slicing on GPU
        if device == "cuda":
            _pipe.enable_attention_slicing()

        # Move to device
        _pipe = _pipe.to(device)
        print(f">> Model loaded and ready on {device}.")
    return _pipe


def generate_and_save_image(prompt, steps: int = 30):
    print(">> Prompt:", prompt)
    pipe = load_pipeline()

    # Generate image with a reduced number of steps
    print(f">> Generating image ({steps} steps)...")
    result = pipe(prompt, num_inference_steps=steps)
    image = result.images[0]

    # Save to static/images/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_images_dir = os.path.join(base_dir, "static", "images")
    os.makedirs(static_images_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex}_test_output.png"
    output_path = os.path.join(static_images_dir, filename)
    image.save(output_path)

    print(f">> Image saved to: {output_path}")
    return output_path

# --- Simple test ---
if __name__ == "__main__":
    test_prompt = "A magical anime battle scene with glowing swords and energy blasts in a ruined city."
    output_file = generate_and_save_image(test_prompt)
    print("Image saved at:", output_file)
