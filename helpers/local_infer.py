import torch
from diffusers import StableDiffusionPipeline
import uuid
import os

def load_pipeline():
    print(">> Loading model... This can take a few minutes the first time.")
    model_id = "hakurei/waifu-diffusion"
    pipe = StableDiffusionPipeline.from_pretrained(model_id)
    print(">> Model loaded.")
    return pipe

def generate_and_save_image(prompt):
    print(">> Prompt:", prompt)
    pipe = load_pipeline()

    # Choose device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f">> Using device: {device}")
    pipe = pipe.to(device)

    # Generate image
    print(">> Generating image...")
    image = pipe(prompt).images[0]

    # ✅ Build correct absolute path to outer static/images/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # one level up from helpers/
    static_images_dir = os.path.join(base_dir, "static", "images")
    os.makedirs(static_images_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex}_test_output.png"
    output_path = os.path.join(static_images_dir, filename)
    image.save(output_path)

    print(f">> Image saved to: {output_path}")
    return output_path

# --- Testing ---
if __name__ == "__main__":
    test_prompt = "A magical anime battle scene with glowing swords and energy blasts in a ruined city."
    output_file = generate_and_save_image(test_prompt)
    print("Image saved at:", output_file)
