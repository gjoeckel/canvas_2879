# Quick OAuth 2.0 Setup Guide

## Important: Authorization Codes Expire in 30 Seconds!

Box authorization codes expire very quickly. You need to:
1. Get the authorization URL
2. Authorize immediately
3. Copy the code from the redirect URL
4. Run the exchange command **immediately** (within 30 seconds)

## Step-by-Step Process

### 1. Get Authorization URL
```bash
cd /Users/a00288946/Projects/canvas_2879
source /Users/a00288946/Projects/canvas_grab/venv/bin/activate
python3 get-box-oauth-token.py
```

### 2. Open the URL in Browser
Copy the URL from step 1 and open it in your browser.

### 3. Authorize the Application
Click "Grant access to Box"

### 4. Copy the Code IMMEDIATELY
You'll be redirected to: `http://localhost:5000/callback?code=XXXXX&state=canvas_update`

**Copy the entire code value** (the part after `code=` and before `&state`)

### 5. Exchange Code for Token (DO THIS IMMEDIATELY!)
```bash
python3 get-box-oauth-token.py --authorization-code YOUR_CODE_HERE
```

**Run this command within 30 seconds of getting the code!**

## One-Liner Alternative

If you're quick, you can do it all at once:

```bash
# Get the URL, open it, authorize, then immediately run:
python3 get-box-oauth-token.py --authorization-code $(echo "PASTE_CODE_HERE")
```

## Troubleshooting

**"Authorization code has expired"**
- The code expired (they only last 30 seconds)
- Solution: Get a new authorization code and exchange it immediately

**"redirect_uri_mismatch"**
- Make sure `http://localhost:5000/callback` is added to your Box app's redirect URIs
- Check for exact match (no trailing slash, correct protocol)

**"invalid_scope"**
- Make sure `root_readwrite` scope is enabled in your Box app settings
- Or try without specifying a scope (use app defaults)

## After Successful Setup

Once you have the access token saved, you can refresh it anytime:
```bash
python3 get-box-oauth-token.py --refresh
```

