import os
import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Configuration
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
SITEMAP_FILE = os.path.join(os.path.dirname(__file__), "..", "sitemap.xml")
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

def get_access_token():
    if not os.path.exists(CREDENTIALS_FILE):
        print("\u274c Error: credentials.json not found in the site/ folder.")
        print("Please follow the setup instructions to create a Service Account key.")
        sys.exit(1)
        
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        request = Request()
        credentials.refresh(request)
        return credentials.token
    except Exception as e:
        print(f"\u274c Error authenticating with Google: {e}")
        sys.exit(1)

def get_recent_urls_from_sitemap(hours_ago=24):
    if not os.path.exists(SITEMAP_FILE):
        print(f"\u274c Error: {SITEMAP_FILE} not found.")
        sys.exit(1)

    recent_urls = []
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    
    try:
        tree = ET.parse(SITEMAP_FILE)
        root = tree.getroot()
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        for url in root.findall('ns:url', namespace):
            loc = url.find('ns:loc', namespace).text
            lastmod = url.find('ns:lastmod', namespace)
            
            if lastmod is not None:
                try:
                    # Parse the ISO format date
                    mod_time = datetime.fromisoformat(lastmod.text.replace('Z', '+00:00'))
                    if mod_time > cutoff_time:
                        recent_urls.append(loc)
                except ValueError:
                    pass
    except Exception as e:
        print(f"\u274c Error parsing sitemap: {e}")
        
    return recent_urls

def notify_google(urls):
    if not urls:
        print("\u2139\ufe0f No recent URLs found in sitemap.xml to index.")
        return

    print(f"\ud83d\udd04 Found {len(urls)} URLs modified in the last 24 hours. Requesting indexing...")
    token = get_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    success_count = 0
    for url in urls:
        payload = {
            "url": url,
            "type": "URL_UPDATED"
        }
        
        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload)
            if response.status_code == 200:
                print(f"\u2705 Success: {url}")
                success_count += 1
            elif response.status_code == 429:
                print(f"\u26a0\ufe0f Quota exceeded for today: {url}")
                break
            else:
                print(f"\u274c Failed: {url} | Status: {response.status_code} | Response: {response.text}")
        except Exception as e:
            print(f"\u274c Request error for {url}: {e}")

    print(f"\n\ud83c\udfaf Finished. Successfully requested indexing for {success_count} out of {len(urls)} URLs.")

if __name__ == "__main__":
    recent_urls = get_recent_urls_from_sitemap(hours_ago=24)
    notify_google(recent_urls)
