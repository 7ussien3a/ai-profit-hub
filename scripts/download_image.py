import urllib.request
import urllib.error
import sys
from pathlib import Path

url = "https://image.pollinations.ai/prompt/Avataar%20AI%20video%20generation%20cultural%20awareness%20india%20technology?width=1280&height=720&nologo=true"
output_path = Path(__file__).resolve().parent.parent / "images" / "article73-avataar-ai.jpg"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        with open(output_path, 'wb') as f:
            f.write(response.read())
    print("Image downloaded successfully.")
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
