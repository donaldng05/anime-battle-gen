from dotenv import load_dotenv
import os
import requests

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found. Check your .env file.")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

print(f"Token starts with: {HF_TOKEN[:10]}...")

def generate_image(prompt):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)

    content_type = response.headers.get("Content-Type", "")
    if response.status_code == 200 and "image" in content_type:
        return response.content
    else:
        print("Hugging Face error:")
        print("Status:", response.status_code)
        print("Content-Type:", content_type)
        print("Body:", response.text)  
        return None
