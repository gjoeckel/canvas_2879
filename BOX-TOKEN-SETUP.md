# Box Developer Token Setup

## Current Issue: 403 Forbidden on File Download

The Box Developer Token can read file metadata but cannot download file content (`can_download: False`).

## Solutions

### Option 1: Update Box App Permissions (Recommended)

1. Go to https://app.box.com/developers/console
2. Select your Box app
3. Go to "Configuration" → "Application Access Level"
4. Ensure the app has **"Read all files and folders"** permission
5. Generate a new Developer Token
6. Update `.box-api-config.json` with the new token

### Option 2: Create Shared Link Manually

1. Open the file in Box web interface
2. Click "Share" or the sharing icon
3. Create a shared link with "People with the link" access
4. Enable "Allow download" in the link settings
5. The script will automatically use this shared link if available

### Option 3: Use OAuth2 with Proper Scopes

For production use, consider implementing OAuth2 authentication with:
- `content:read` scope for downloading files
- `manage_shared_links` scope for creating shared links if needed

## Current Token Status

- ✅ Can read file metadata
- ❌ Cannot download file content (403 Forbidden)
- ❌ Cannot create/modify shared links

## Testing Token Permissions

Run this to check your token's permissions:

```bash
cd /Users/a00288946/Projects/canvas_2879
python3 -c "
import json
import requests
from pathlib import Path

config_file = Path('.box-api-config.json')
with open(config_file, 'r') as f:
    config = json.load(f)
token = config.get('developer_token')

headers = {'Authorization': f'Bearer {token}'}
file_id = '2071049022878'

info_url = f'https://api.box.com/2.0/files/{file_id}?fields=permissions'
response = requests.get(info_url, headers=headers)
if response.status_code == 200:
    file_info = response.json()
    perms = file_info.get('permissions', {})
    print('File Permissions:')
    for key, value in perms.items():
        print(f'  {key}: {value}')
"
```

## Next Steps

1. Update Box app permissions to allow file downloads
2. Generate a new Developer Token
3. Update `.box-api-config.json` with the new token
4. Restart the API server

