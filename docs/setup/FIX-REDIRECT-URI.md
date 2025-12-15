# Fix Redirect URI Mismatch

## Problem
You're getting a `redirect_uri_mismatch` error because the redirect URI in the OAuth request doesn't match what's configured in your Box app.

## Solution: Add Redirect URI to Box App

### Steps:

1. **Go to Box Developer Console:**
   - Visit: https://app.box.com/developers/console
   - Log in if needed

2. **Select Your App:**
   - Find and click on your app (Client ID: `3xsda5fikhvgjua3s4gj7m6syr62hkty`)

3. **Go to Configuration:**
   - Click on the "Configuration" tab

4. **Find OAuth 2.0 Credentials Section:**
   - Scroll down to "OAuth 2.0 Credentials" or "Redirect URIs"

5. **Add Redirect URI:**
   - In the "Redirect URIs" field, add:
     ```
     http://localhost:5000/callback
     ```
   - Click "Save" or "Update"

6. **Important Notes:**
   - The redirect URI must match **exactly** (including `http://` not `https://`)
   - No trailing slashes
   - Case-sensitive
   - You can add multiple redirect URIs (one per line or separated by commas, depending on the UI)

### After Adding the Redirect URI:

1. **Try the authorization again:**
   ```bash
   cd /Users/a00288946/Projects/canvas_2879
   source /Users/a00288946/Projects/canvas_grab/venv/bin/activate
   python3 get-box-oauth-token.py
   ```

2. **Open the URL it provides** in your browser

3. **Authorize the application**

4. **Copy the authorization code** from the redirect URL

5. **Exchange it for an access token:**
   ```bash
   python3 get-box-oauth-token.py --authorization-code YOUR_CODE_HERE
   ```

## Alternative Redirect URIs

If you prefer a different redirect URI, you can use:
- `http://localhost:8080/callback`
- `https://yourdomain.com/callback` (if you have a public domain)

Just make sure to:
1. Add it to Box app settings
2. Update `.box-api-config.json` with the new `redirect_uri`

## Troubleshooting

**Still getting redirect_uri_mismatch?**
- Make sure you saved the changes in Box
- Wait a few seconds for changes to propagate
- Check for typos (extra spaces, wrong protocol, etc.)
- Try clearing browser cache and cookies

**Can't find the Redirect URI field?**
- Make sure you're in the "Configuration" tab
- Look for "OAuth 2.0 Credentials" or "Application Settings"
- Some apps may have it under "Advanced Settings"

