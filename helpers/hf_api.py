import os
from dotenv import load_dotenv
import requests

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/prompthero/waifu-diffusion"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_image(prompt):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content
