# helpers/local_infer.py

import os, uuid, time
import torch
from datetime import datetime
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

# ── Caches ──
_pipe = None
_styled_pipes: dict[str, StableDiffusionXLPipeline] = {}

# ── Map dropdown → local LoRA paths ──
STYLE_LORA_FILES = {
    "One Piece":      "models/wano_saga_lora.safetensors",
    "Naruto":         "models/naruto_or_style_lora.safetensors",
    "Jujutsu Kaisen": "models/jujutsu_kaisen_sdxl_lora.safetensors",
}

def load_pipeline():
    global _pipe
    if _pipe is None:
        print(">> Loading SDXL 1.0 base model…")
        _pipe = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            # only use fp16 if you have a GPU; on CPU it'll default to fp32
            torch_dtype=torch.float16 if torch.cuda.is_available() else None,
            variant="fp16"
        )

        device = "cuda" if torch.cuda.is_available() else "cpu"
        _pipe = _pipe.to(device)

        # swap in your preferred scheduler
        _pipe.scheduler = DPMSolverMultistepScheduler.from_config(_pipe.scheduler.config)
        # disable safety for offline use
        _pipe.safety_checker = lambda images, **kwargs: (images, [False] * len(images))

        print(f">> SDXL 1.0 pipeline ready on {device}.")
    return _pipe

def load_styled_pipeline(style: str | None = None):
    base = load_pipeline()
    if not style or style not in STYLE_LORA_FILES:
        return base

    if style in _styled_pipes:
        return _styled_pipes[style]

    lora_path = STYLE_LORA_FILES[style]
    print(f">> Loading LoRA for style '{style}' from {lora_path}")
    base.load_lora_weights(lora_path, weight=0.7)
    _styled_pipes[style] = base
    return base

def generate_and_save_image(prompt: str,
                            steps: int = 20,
                            style: str | None = None) -> str:
    pipe = load_styled_pipeline(style)
    start = time.perf_counter()
    result = pipe(prompt, num_inference_steps=steps, guidance_scale=8.5)
    elapsed = time.perf_counter() - start

    # … (logging + saving unchanged) …
    filename = f"{uuid.uuid4().hex}_output.png"
    out_dir = os.path.join("static","images")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    result.images[0].save(path)
    print(f">> Took {elapsed:.1f}s, saved to {path}")
    return path
