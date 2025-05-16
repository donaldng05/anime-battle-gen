import time
import torch
from diffusers import StableDiffusionPipeline
from diffusers import (
    EulerDiscreteScheduler,
    DDIMScheduler,
    DPMSolverMultistepScheduler,
    LMSDiscreteScheduler,
)

MODEL_ID = "hakurei/waifu-diffusion"
DEVICE   = "cpu"  # switch to "cuda" if you have a GPU
PIPE     = StableDiffusionPipeline.from_pretrained(MODEL_ID).to(DEVICE)

# Disable the built-in safety checker by overriding run_safety_checker directly:
PIPE.run_safety_checker = lambda images, device, dtype: (images, [False] * len(images))

# Optional: if you ever run on GPU, you can still enable slicing
if torch.cuda.is_available():
    PIPE.enable_attention_slicing()

SCHEDULERS = {
    "Euler":     EulerDiscreteScheduler,
    "DDIM":      DDIMScheduler,
    "DPMSolver": DPMSolverMultistepScheduler,
    "LMS":       LMSDiscreteScheduler,
}

for name, SchedulerCls in SCHEDULERS.items():
    # swap in this scheduler
    PIPE.scheduler = SchedulerCls.from_config(PIPE.scheduler.config)

    # 1-step probe timing
    start = time.perf_counter()
    _ = PIPE("test prompt", num_inference_steps=1)
    step_time = time.perf_counter() - start

    # extrapolate to other step counts
    print(
        f"{name}: {step_time:.2f}s/step  → "
        f"20 steps: {step_time * 20:.1f}s, "
        f"25 steps: {step_time * 25:.1f}s, "
        f"30 steps: {step_time * 30:.1f}s"
    )
