#!/usr/bin/env python3
"""
Test script to set Box file permissions for "Reviewing" mode
Tests with Course Orientation DOCX file first
"""

import os
import json
import requests
from pathlib import Path

BOX_API_BASE_URL = 'https://api.box.com/2.0'
BOX_API_CONFIG_FILE = Path('.box-api-config.json')

# Course Orientation file ID
COURSE_ORIENTATION_FILE_ID = '2071049022878'

def load_box_config():
    """Load Box API configuration."""
    config = {}

    # Try environment variable first
    developer_token = os.getenv('BOX_DEVELOPER_TOKEN')
    if developer_token:
        config['developer_token'] = developer_token
        print('📖 Using BOX_DEVELOPER_TOKEN from environment')

    # Try config file
    if BOX_API_CONFIG_FILE.exists():
        with open(BOX_API_CONFIG_FILE, 'r') as f:
            file_config = json.load(f)
            config.update(file_config)
            print(f'📖 Loaded configuration from {BOX_API_CONFIG_FILE}')

    return config

def get_file_info(access_token, file_id):
    """Get file information from Box API."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    url = f'{BOX_API_BASE_URL}/files/{file_id}'
    params = {
        'fields': 'id,name,shared_link,permissions'
    }

    response = requests.get(url, headers=headers, params=params)
    return response

def update_shared_link(access_token, file_id, access_level='open', can_edit=False, can_download=True):
    """Update shared link settings for a file."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    url = f'{BOX_API_BASE_URL}/files/{file_id}'

    # Set permissions for "view and comment" (reviewing mode)
    # can_edit=False means they can comment but not directly edit
    payload = {
        'shared_link': {
            'access': access_level,
            'permissions': {
                'can_download': can_download,
                'can_edit': can_edit  # False = view and comment only
            }
        }
    }

    response = requests.put(url, headers=headers, json=payload)
    return response

def main():
    print('📦 Box Reviewing Mode Test Script')
    print('=' * 50)

    # Load configuration
    config = load_box_config()
    access_token = config.get('developer_token') or config.get('access_token')

    if not access_token:
        print('\n❌ No Box API access token found!')
        print('\n📝 Setup:')
        print('  1. Get Developer Token from: https://app.box.com/developers/console')
        print('  2. Set environment variable:')
        print('     export BOX_DEVELOPER_TOKEN="your_token_here"')
        print('\n  Or create .box-api-config.json:')
        print('  {')
        print('    "developer_token": "your_token_here"')
        print('  }')
        return

    print(f'\n📄 Testing with Course Orientation file (ID: {COURSE_ORIENTATION_FILE_ID})')

    # Get current file info
    print('\n1️⃣ Getting current file information...')
    response = get_file_info(access_token, COURSE_ORIENTATION_FILE_ID)

    if response.status_code == 401:
        print('❌ Authentication failed (401)')
        print('   Your token may have expired. Please refresh it.')
        print(f'   Response: {response.text[:200]}')
        return
    elif response.status_code != 200:
        print(f'❌ Error getting file info: {response.status_code}')
        print(f'   Response: {response.text[:200]}')
        return

    file_info = response.json()
    print(f'✅ File found: {file_info.get("name", "Unknown")}')

    current_shared_link = file_info.get('shared_link')
    if current_shared_link:
        print(f'   Current shared link: {current_shared_link.get("url", "N/A")}')
        print(f'   Current permissions: {current_shared_link.get("permissions", {})}')
    else:
        print('   No shared link currently set')

    # Update shared link to "view and comment" mode
    print('\n2️⃣ Updating shared link to "view and comment" mode...')
    print('   (This should encourage Reviewing mode in Office Online)')

    response = update_shared_link(
        access_token,
        COURSE_ORIENTATION_FILE_ID,
        access_level='open',
        can_edit=False,  # False = view and comment only
        can_download=True
    )

    if response.status_code == 200:
        updated_file = response.json()
        print('✅ Shared link updated successfully!')

        new_shared_link = updated_file.get('shared_link', {})
        if new_shared_link:
            print(f'   New shared link: {new_shared_link.get("url", "N/A")}')
            print(f'   New permissions: {new_shared_link.get("permissions", {})}')

            # Generate Office Online link
            office_online_url = f"https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={COURSE_ORIENTATION_FILE_ID}&sharedAccessCode="
            print(f'\n🔗 Test Office Online link:')
            print(f'   {office_online_url}')
            print(f'\n📝 Next steps:')
            print(f'   1. Open the link above')
            print(f'   2. Check if it opens in Reviewing mode')
            print(f'   3. If not, manually switch to Reviewing mode in Word Online')
    else:
        print(f'❌ Error updating shared link: {response.status_code}')
        print(f'   Response: {response.text[:500]}')
        if response.status_code == 403:
            print('\n   Note: You may need "Editor" or "Co-owner" permissions on the file')
        elif response.status_code == 401:
            print('\n   Note: Your token may have expired. Please refresh it.')

if __name__ == '__main__':
    main()

