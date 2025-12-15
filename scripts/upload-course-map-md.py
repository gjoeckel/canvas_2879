#!/usr/bin/env python3
"""
Upload course-map.md to Box using Box API with automatic token refresh
"""

import os
import json
import sys
import requests
from pathlib import Path

# Box API endpoints
BOX_API_BASE = "https://api.box.com/2.0"
BOX_UPLOAD_API = "https://upload.box.com/api/2.0"

# Configuration
COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
CONFIG_FILE = COURSE_DIR / ".box-api-config.json"
COURSE_MAP_PATH = COURSE_DIR / "data/current/WINTER-25-26-UPDATES/course-map.md"
BOX_FOLDER_ID = '355472814432'

def load_config():
    """Load Box OAuth configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def refresh_access_token():
    """Refresh Box access token."""
    config = load_config()
    if not config:
        raise ValueError("Box config not found")

    client_id = os.getenv('BOX_CLIENT_ID') or config.get('client_id')
    client_secret = os.getenv('BOX_CLIENT_SECRET') or config.get('client_secret')
    refresh_token = os.getenv('BOX_REFRESH_TOKEN') or config.get('refresh_token')

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing Box OAuth credentials")

    response = requests.post(
        'https://api.box.com/oauth2/token',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if response.status_code != 200:
        raise ValueError(f"Token refresh failed: {response.status_code} - {response.text}")

    tokens = response.json()
    return tokens['access_token'], tokens.get('refresh_token', refresh_token)

def get_access_token():
    """Get Box access token, refreshing if needed."""
    config = load_config()

    # Try config file first
    access_token = config.get('access_token') if config else None

    # Try environment variable
    if not access_token:
        access_token = os.getenv('BOX_ACCESS_TOKEN')

    # Try to refresh if we have refresh token
    if not access_token:
        try:
            access_token, refresh_token = refresh_access_token()
            # Update config if possible
            if config:
                config['access_token'] = access_token
                config['refresh_token'] = refresh_token
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not refresh token: {e}")

    if not access_token:
        raise ValueError("No Box access token available")

    return access_token

def upload_file_to_box(folder_id, file_path, file_name):
    """Upload a file to Box."""
    access_token = get_access_token()

    # Read file content
    with open(file_path, 'rb') as f:
        file_content = f.read()

    # Prepare upload
    files = {
        'file': (file_name, file_content, 'text/markdown')
    }

    data = {
        'parent_id': folder_id
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Upload file
    url = f'{BOX_UPLOAD_API}/files/content'
    response = requests.post(
        url,
        headers=headers,
        files=files,
        data=data
    )

    if response.status_code == 401:
        # Token expired, try refreshing
        print("Token expired, refreshing...")
        access_token, refresh_token = refresh_access_token()
        headers['Authorization'] = f'Bearer {access_token}'

        # Update config
        config = load_config()
        if config:
            config['access_token'] = access_token
            config['refresh_token'] = refresh_token
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)

        # Retry upload
        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data
        )

    if response.status_code not in [200, 201]:
        raise ValueError(f"Upload failed: {response.status_code} - {response.text}")

    return response.json()

def main():
    print(f"Reading course-map.md from {COURSE_MAP_PATH}...")

    if not COURSE_MAP_PATH.exists():
        raise FileNotFoundError(f"File not found: {COURSE_MAP_PATH}")

    print(f"Uploading course-map.md to Box folder {BOX_FOLDER_ID}...")

    try:
        result = upload_file_to_box(
            folder_id=BOX_FOLDER_ID,
            file_path=COURSE_MAP_PATH,
            file_name='course-map.md'
        )

        file_id = result['entries'][0]['id']
        print(f"✅ Uploaded course-map.md to Box")
        print(f"   File ID: {file_id}")
        print(f"   URL: https://usu.app.box.com/file/{file_id}")

    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
