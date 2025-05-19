import os
import sys
from pathlib import Path

# ─── make sure project root is on PYTHONPATH ──────────────────────────────────
# so "import helpers.local_infer" works even when running from scripts/
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# ─── now regular imports ─────────────────────────────────────────────────
from helpers.local_infer import load_styled_pipeline

# How many samples per style
NUM_SAMPLES = 2

# battle prompts per franchise
STYLE_PROMPTS = {
    "One Piece": (
        "Monkey D. Luffy (left, straw hat, rubber limbs) vs "
        "Roronoa Zoro (right, three swords, green bandana); "
        "no other people or limbs"
    ),
    "Naruto": (
        "Naruto Uzumaki (left, blonde hair, orange jumpsuit) vs "
        "Sasuke Uchiha (right, black hair, navy outfit); "
        "no other people or limbs"
    ),
    "Jujutsu Kaisen": (
        "Satoru Gojo (left, white hair, blindfold) vs "
        "Ryomen Sukuna (right, red eyes, spiky hair); "
        "no other people or limbs"
    ),
}

# Number of steps already determined is your sweet spot
STEPS = 20

# Where to dump the outputs
OUT_DIR = PROJECT_ROOT / "bench_outputs" / "lora_checks"

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for style, prompt in STYLE_PROMPTS.items():
        print(f"\n=== Generating for style: {style!r} ===")
        # load the pipeline with the LoRA adapter baked in
        pipe = load_styled_pipeline(style)

        for i in range(1, NUM_SAMPLES + 1):
            img = pipe(prompt, num_inference_steps=STEPS).images[0]
            # filename: One_Piece_1.png, Naruto_2.png, etc.
            safe_style = style.replace(" ", "_")
            fname = f"{safe_style}_{i:02d}.png"
            path = OUT_DIR / fname
            img.save(path)
            print(f" • Saved {path}")

    print("\nDone! Inspect bench_outputs/lora_checks/ for samples.")

if __name__ == "__main__":
    main()
