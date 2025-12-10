# Box OAuth 2.0 Setup Instructions

## Step 1: Authorize the Application

1. **Open this URL in your browser:**
   ```
   https://account.box.com/api/oauth2/authorize?response_type=code&client_id=3xsda5fikhvgjua3s4gj7m6syr62hkty&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fcallback&scope=content%3Aread+read_all_files_and_folders&state=canvas_update
   ```

2. **Log in to Box** (if not already logged in)

3. **Authorize the application** - Click "Grant access to Box"

4. **You'll be redirected** to `http://localhost:5000/callback?code=XXXXX&state=canvas_update`

5. **Copy the `code` parameter** from the URL (the part after `code=` and before `&state`)

## Step 2: Exchange Authorization Code for Access Token

Run this command with the authorization code you copied:

```bash
cd /Users/a00288946/Projects/canvas_2879
source /Users/a00288946/Projects/canvas_grab/venv/bin/activate
python3 get-box-oauth-token.py --authorization-code YOUR_CODE_HERE
```

Replace `YOUR_CODE_HERE` with the actual code from the redirect URL.

## Step 3: Verify Configuration

The script will automatically save the access token to `.box-api-config.json`. You can verify it worked:

```bash
python3 -c "
import json
from pathlib import Path
config = json.load(open(Path('.box-api-config.json')))
oauth2 = config.get('oauth2', {})
if oauth2.get('access_token'):
    print('✅ OAuth 2.0 access token configured!')
    print(f'   Token: {oauth2[\"access_token\"][:20]}...')
else:
    print('❌ OAuth 2.0 access token not found')
"
```

## Step 4: Test File Download

Once the OAuth token is configured, the `update-canvas-from-docx.py` script will automatically use it (it prefers OAuth tokens over Developer Tokens).

Try updating a Canvas page:

```bash
python3 update-canvas-from-docx.py \
  --box-file-id 2071049022878 \
  --canvas-page-slug course-orientation
```

## Token Refresh

OAuth access tokens expire after 1 hour. To refresh:

```bash
python3 get-box-oauth-token.py --refresh
```

## Troubleshooting

### Redirect URI Mismatch

If you get an error about redirect URI, make sure:
1. The redirect URI in your Box app settings matches: `http://localhost:5000/callback`
2. Go to https://app.box.com/developers/console
3. Select your app → Configuration → OAuth 2.0 Credentials
4. Add `http://localhost:5000/callback` to "Redirect URIs"

### Invalid Authorization Code

- Authorization codes expire after 30 seconds
- Make sure you copy the entire code (it's usually quite long)
- If it expired, just run the authorization flow again

### 403 Forbidden After Setup

- Make sure your Box app has the correct scopes enabled:
  - `content:read`
  - `read_all_files_and_folders`
- Check app permissions in Box Developer Console

