import os
import urllib.request

FONTS_DIR = r"d:\AntiGravity Projects\CourseMate\assets\fonts"
os.makedirs(FONTS_DIR, exist_ok=True)

URL = "https://github.com/googlefonts/RobotoMono/raw/main/fonts/ttf/RobotoMono-Regular.ttf"

def download_file(url, filename):
    path = os.path.join(FONTS_DIR, filename)
    print(f"Downloading {filename} from {url}...")
    try:
        urllib.request.urlretrieve(url, path)
        print(f"Saved to {path}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    download_file(URL, "RobotoMono-Regular.ttf")
