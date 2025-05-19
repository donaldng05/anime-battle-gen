import os
import requests
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()   

# ─── Configuration ────────────────────────────────────────────────────────────
# Make sure you’ve set these two env vars:
#   export GOOGLE_API_KEY="your‐google‐api‐key"
#   export GOOGLE_CX="your‐custom‐search‐engine‐id"
API_KEY = os.getenv("GOOGLE_API_KEY")
CX      = os.getenv("GOOGLE_CX")
if not API_KEY or not CX:
    raise RuntimeError("Please set both GOOGLE_API_KEY and GOOGLE_CX environment variables.")

ENDPOINT = "https://www.googleapis.com/customsearch/v1"

# For each franchise: [specific-iconic query, general-battle query]
FRANCHISE_QUERIES = {
    "One_Piece": [
        "One Piece Luffy vs Zoro battle scene",
        "One Piece anime fight screenshot"
    ],
    "Naruto": [
        "Naruto vs Sasuke battle scene",
        "Naruto anime fight screenshot"
    ],
    "Jujutsu_Kaisen": [
        "Jujutsu Kaisen Gojo vs Sukuna fight scene",
        "Jujutsu Kaisen anime battle screenshot"
    ],
}

IMAGES_PER_QUERY = 5        # ~10 images per franchise (5 specific + 5 general)
OUT_DIR = Path("data/real_battles")

def fetch_and_save(franchise: str, query: str, count: int):
    """
    Use Google Custom Search to fetch `count` high-res images for `query`
    and save them under OUT_DIR/franchise/.
    """
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "searchType": "image",
        "safe": "high",
        "imgSize": "large",        # request large images
        "fileType": "jpg,png",
        "num": count,              # max 10
    }
    resp = requests.get(ENDPOINT, params=params)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    folder = OUT_DIR / franchise
    folder.mkdir(parents=True, exist_ok=True)

    for idx, item in enumerate(items[:count], start=1):
        url = item.get("link")
        if not url:
            continue

        ext = Path(url.split("?")[0]).suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".gif"}:
            ext = ".jpg"
        filename = f"{query.replace(' ', '_')}_{idx:02d}{ext}"
        path = folder / filename

        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"[{franchise}] Saved {path}")
        except Exception as e:
            print(f"[{franchise}] Failed to download {url}: {e}")

def main():
    for franchise, queries in FRANCHISE_QUERIES.items():
        for q in queries:
            fetch_and_save(franchise, q, IMAGES_PER_QUERY)
    print("\nDone! Check out data/real_battles/ for your images.")

if __name__ == "__main__":
    main()
