import os
import torch
import numpy as np
from PIL import Image
from tqdm import tqdm
from diffusers import StableDiffusionPipeline
from diffusers import (
    EulerDiscreteScheduler,
    DDIMScheduler,
    DPMSolverMultistepScheduler,
    LMSDiscreteScheduler,
)
from torchmetrics.image.fid import FrechetInceptionDistance
import lpips
import pandas as pd

# ─── CONFIG ──────────────────────────────────────────────────────────────────
MODEL_ID    = "hakurei/waifu-diffusion"
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"
PROMPT      = "A magical anime battle scene with glowing swords"
REF_DIR     = "data/real_anime/"    # folder of real anime images for FID
OUT_DIR     = "bench_outputs/"
STEPS_LIST  = [20, 25, 30]
NUM_SAMPLES = 2                    # ≥2 for valid FID
SCHEDULERS  = {
    "Euler":     EulerDiscreteScheduler,
    "DDIM":      DDIMScheduler,
    "DPMSolver": DPMSolverMultistepScheduler,
    "LMS":       LMSDiscreteScheduler,
}

# ─── SETUP METRICS ─────────────────────────────────────────────────────────────
lpips_fn = lpips.LPIPS(net="alex").to(DEVICE)

# ─── LOAD & CACHE PIPELINE ─────────────────────────────────────────────────────
pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID).to(DEVICE)
if torch.cuda.is_available():
    pipe.enable_attention_slicing()

# ─── PRELOAD REAL IMAGES FOR FID ───────────────────────────────────────────────
# Convert each reference image to a uint8 tensor and store
real_tensors = []
for fname in os.listdir(REF_DIR):
    img = Image.open(os.path.join(REF_DIR, fname)).convert("RGB")
    arr = np.array(img)  # uint8 H×W×C
    t = (
        torch.from_numpy(arr)
             .permute(2, 0, 1)  # C×H×W
             .unsqueeze(0)      # 1×C×H×W
             .to(DEVICE)
    )
    real_tensors.append(t)

# ─── PRELOAD ONE REFERENCE IMAGE FOR LPIPS ────────────────────────────────────
# We'll resize this per-generated image
ref_fname    = os.listdir(REF_DIR)[0]
ref_img_orig = Image.open(os.path.join(REF_DIR, ref_fname)).convert("RGB")

# ─── BENCHMARK LOOP ──────────────────────────────────────────────────────────
results = []

for name, SchedulerCls in SCHEDULERS.items():
    # swap in the scheduler
    pipe.scheduler = SchedulerCls.from_config(pipe.scheduler.config)

    for steps in STEPS_LIST:
        # Initialize a fresh FID metric for this (scheduler, steps)
        fid_temp = FrechetInceptionDistance(feature=2048).to(DEVICE)
        # Feed all real images
        for t_real in real_tensors:
            fid_temp.update(t_real, real=True)

        lp_accum = 0.0
        for i in range(NUM_SAMPLES):
            # 1) Generate
            out = pipe(PROMPT, num_inference_steps=steps)
            gen_img = out.images[0].convert("RGB")

            # 2) Save for inspection
            os.makedirs(f"{OUT_DIR}/{name}", exist_ok=True)
            path = f"{OUT_DIR}/{name}/{steps}_s{i+1}.png"
            gen_img.save(path)

            # 3) Prepare uint8 tensor for FID
            arr_gen = np.array(gen_img)
            t_uint8 = (
                torch.from_numpy(arr_gen)
                     .permute(2, 0, 1)
                     .unsqueeze(0)
                     .to(DEVICE)
            )
            fid_temp.update(t_uint8, real=False)

            # 4) Prepare float tensor for LPIPS
            t_float = t_uint8.float() / 255.0
            # resize reference to match
            ref_resized = ref_img_orig.resize(gen_img.size, resample=Image.BILINEAR)
            arr_ref2     = np.array(ref_resized)
            t_ref_float  = (
                torch.from_numpy(arr_ref2)
                     .permute(2, 0, 1)
                     .unsqueeze(0)
                     .float()
                     .to(DEVICE) / 255.0
            )
            lp_accum += lpips_fn(t_float * 2 - 1, t_ref_float * 2 - 1).item()

        # 5) Compute metrics
        fid_score = fid_temp.compute().item()
        lp_avg    = lp_accum / NUM_SAMPLES

        results.append({
            "scheduler": name,
            "steps": steps,
            "fid": fid_score,
            "lpips": lp_avg
        })

# ─── REPORT ──────────────────────────────────────────────────────────────────
df = pd.DataFrame(results)
print("FID scores:")
print(df.pivot(index="steps", columns="scheduler", values="fid"))
print("\nLPIPS scores:")
print(df.pivot(index="steps", columns="scheduler", values="lpips"))

# Save CSV for further analysis
df.to_csv("bench_results.csv", index=False)
