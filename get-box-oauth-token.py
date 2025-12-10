#!/usr/bin/env python3
"""
Get Box OAuth 2.0 Access Token

This script helps you obtain an OAuth 2.0 access token from Box
using the Authorization Code flow.
"""

import os
import json
import requests
from pathlib import Path
from urllib.parse import urlencode, parse_qs, urlparse

BOX_AUTH_URL = "https://account.box.com/api/oauth2/authorize"
BOX_TOKEN_URL = "https://api.box.com/oauth2/token"
COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
CONFIG_FILE = COURSE_DIR / ".box-api-config.json"

def load_config():
    """Load Box OAuth configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_authorization_url(client_id, redirect_uri, scope='root_readwrite'):
    """Generate Box authorization URL.

    Valid Box scopes:
    - root_readwrite: Full read/write access to user's root folder
    - root_readonly: Read-only access to user's root folder
    - Or leave empty to use app's default scopes
    """
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': 'canvas_update'
    }

    # Add scope if provided (some apps work better without explicit scope)
    if scope:
        params['scope'] = scope

    return f"{BOX_AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(client_id, client_secret, authorization_code, redirect_uri):
    """Exchange authorization code for access token."""
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }

    response = requests.post(BOX_TOKEN_URL, data=data)

    # Check for errors and provide helpful messages
    if response.status_code != 200:
        error_detail = response.text
        print(f"❌ Error exchanging authorization code: {response.status_code}")
        print(f"   Response: {error_detail}")
        if 'invalid_grant' in error_detail:
            print("\n💡 This usually means:")
            print("   - Authorization code has expired (they expire after 30 seconds)")
            print("   - Authorization code was already used")
            print("   - Redirect URI doesn't match exactly")
        response.raise_for_status()

    return response.json()

def refresh_access_token(client_id, client_secret, refresh_token):
    """Refresh an expired access token."""
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(BOX_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()

def main():
    """Main function to get OAuth token."""
    import argparse

    parser = argparse.ArgumentParser(description='Get Box OAuth 2.0 Access Token')
    parser.add_argument('--client-id', type=str, help='Box OAuth Client ID')
    parser.add_argument('--client-secret', type=str, help='Box OAuth Client Secret')
    parser.add_argument('--redirect-uri', type=str, default='http://localhost:5000/callback',
                       help='Redirect URI (default: http://localhost:5000/callback)')
    parser.add_argument('--scope', type=str, default='root_readwrite',
                       help='OAuth scope (default: root_readwrite). Options: root_readwrite, root_readonly, or leave empty for app default')
    parser.add_argument('--authorization-code', type=str,
                       help='Authorization code from Box redirect')
    parser.add_argument('--refresh', action='store_true',
                       help='Refresh existing access token')
    args = parser.parse_args()

    config = load_config()
    oauth2_config = config.get('oauth2', {})

    # Get credentials from args, config, or prompt
    client_id = args.client_id or oauth2_config.get('client_id')
    client_secret = args.client_secret or oauth2_config.get('client_secret')
    redirect_uri = args.redirect_uri or oauth2_config.get('redirect_uri', 'http://localhost:5000/callback')
    scope = args.scope or oauth2_config.get('scope', 'root_readwrite')

    if not client_id or not client_secret:
        print("❌ Missing OAuth credentials!")
        print("\n📝 Setup:")
        print("1. Go to https://app.box.com/developers/console")
        print("2. Create/select an app with OAuth 2.0")
        print("3. Get Client ID and Client Secret")
        print("4. Set redirect URI in app settings")
        print("\nThen run:")
        print("  python3 get-box-oauth-token.py --client-id YOUR_ID --client-secret YOUR_SECRET")
        return

    if args.refresh:
        # Refresh existing token
        refresh_token = oauth2_config.get('refresh_token')
        if not refresh_token:
            print("❌ No refresh token found in config")
            return

        print("🔄 Refreshing access token...")
        token_data = refresh_access_token(client_id, client_secret, refresh_token)

        # Update config
        oauth2_config['access_token'] = token_data['access_token']
        if 'refresh_token' in token_data:
            oauth2_config['refresh_token'] = token_data['refresh_token']

        config['oauth2'] = oauth2_config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Access token refreshed!")
        print(f"   New token: {token_data['access_token'][:20]}...")
        return

    if args.authorization_code:
        # Exchange code for token
        print("🔄 Exchanging authorization code for access token...")
        token_data = exchange_code_for_token(
            client_id, client_secret, args.authorization_code, redirect_uri
        )

        # Save to config
        oauth2_config.update({
            'client_id': client_id,
            'client_secret': client_secret,
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
            'redirect_uri': redirect_uri
        })

        config['oauth2'] = oauth2_config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ OAuth token saved to {CONFIG_FILE}")
        print(f"   Access token: {token_data['access_token'][:20]}...")
        print(f"   Expires in: {token_data.get('expires_in', 'unknown')} seconds")
        return

    # Step 1: Get authorization URL
    auth_url = get_authorization_url(client_id, redirect_uri, scope)

    print("📋 Box OAuth 2.0 Setup")
    print("=" * 50)
    print("\n1️⃣  Open this URL in your browser:")
    print(f"   {auth_url}")
    print("\n2️⃣  Authorize the application")
    print(f"3️⃣  You'll be redirected to: {redirect_uri}")
    print("4️⃣  Copy the 'code' parameter from the redirect URL")
    print("\n5️⃣  Then run:")
    print(f"   python3 get-box-oauth-token.py \\")
    print(f"     --client-id {client_id} \\")
    print(f"     --client-secret {client_secret} \\")
    print(f"     --authorization-code <code_from_redirect>")
    print("\n💡 Tip: For server-to-server, consider using JWT authentication instead")

if __name__ == '__main__':
    main()

