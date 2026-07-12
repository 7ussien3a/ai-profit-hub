import os
import sys
import json
import logging
from google.oauth2 import service_account
import google.auth.transport.requests
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GoogleIndexer")

# Endpoint for Google Indexing API
INDEXING_API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

def ping_google(url: str):
    """
    Pings Google Indexing API to notify about a new or updated URL.
    Requires a valid service-account.json file in the same directory.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    service_account_path = os.path.join(base_dir, 'service-account.json')

    if not os.path.exists(service_account_path):
        logger.warning(
            "Service account file not found: %s\n"
            "Skipping Google Indexing API ping.\n"
            "Please create a GCP Service Account, download the JSON key as 'service-account.json', "
            "place it in 'site/scripts/', and add its email to Google Search Console as an Owner.",
            service_account_path
        )
        return False

    try:
        # Load credentials from service account file
        creds = service_account.Credentials.from_service_account_file(
            service_account_path, scopes=SCOPES
        )

        # Create an auth request session
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)

        # Prepare payload
        payload = {
            "url": url,
            "type": "URL_UPDATED"
        }

        # Set headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {creds.token}"
        }

        # Send request
        response = requests.post(INDEXING_API_ENDPOINT, headers=headers, json=payload)

        if response.status_code == 200:
            logger.info(f"Successfully pinged Google Indexing API for URL: {url}")
            return True
        else:
            logger.error(
                f"Failed to ping Google Indexing API for URL: {url}. "
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False

    except Exception as e:
        logger.error(f"Error while trying to ping Google Indexing API: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python google_indexer.py <url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    ping_google(target_url)
