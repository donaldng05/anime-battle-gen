import os
import requests

def fetch_images(count=20, out_dir='data/real_anime'):
    os.makedirs(out_dir, exist_ok=True)
    urls = []
    page = 1

    # Keep paging until we have enough URLs
    while len(urls) < count:
        resp = requests.get(
            'https://api.waifu.im/search',
            params={'is_nsfw': 'false', 'page': page}
        )
        resp.raise_for_status()
        data = resp.json().get('images', [])
        if not data:
            break

        for item in data:
            if len(urls) >= count:
                break
            urls.append(item['url'])
        page += 1

    if not urls:
        print("No images found—check your network or the API.")
        return

    # Download each image
    for idx, url in enumerate(urls, start=1):
        try:
            r = requests.get(url, stream=True)
            r.raise_for_status()
            ext = os.path.splitext(url.split('?')[0])[1] or '.jpg'
            filename = f"{idx:02d}{ext}"
            path = os.path.join(out_dir, filename)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"[{idx}/{len(urls)}] Saved {url} → {path}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")

if __name__ == '__main__':
    fetch_images()
