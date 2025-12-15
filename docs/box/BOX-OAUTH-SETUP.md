# Box OAuth 2.0 Setup Guide

## Overview

Using Box OAuth 2.0 provides better permissions and access control compared to Developer Tokens. OAuth 2.0 allows you to request specific scopes (permissions) needed for your application.

## OAuth 2.0 Flow Options

### Option 1: Client Credentials Grant (Server-to-Server)
Best for server-side applications that need to access files on behalf of the app itself.

**Required:**
- Client ID
- Client Secret
- JWT (JSON Web Token) for authentication

### Option 2: Authorization Code Grant (User Authorization)
Best for applications that need to access files on behalf of a specific user.

**Required:**
- Client ID
- Client Secret
- Authorization code (obtained from user consent)
- Access token and refresh token

## Setup Steps

### 1. Create Box Application

1. Go to https://app.box.com/developers/console
2. Click "Create New App"
3. Choose "Custom App"
4. Select "Server Authentication (with JWT)" for server-to-server, or "OAuth 2.0" for user authorization
5. Note your **Client ID** and **Client Secret**

### 2. Configure Application Scopes

In your Box app settings, ensure these scopes are enabled:
- `content:read` - Read file content
- `read_all_files_and_folders` - Read all files (if needed)
- `manage_shared_links` - Create/manage shared links (optional)

### 3. For Server Authentication (JWT)

1. Generate a **Public Key ID** and **Private Key** in your Box app
2. Download the private key (JSON config file)
3. Store credentials securely

### 4. For OAuth 2.0 (User Authorization)

1. Set **Redirect URI** in app settings (e.g., `http://localhost:5000/callback`)
2. Implement OAuth flow to get authorization code
3. Exchange authorization code for access token and refresh token

## Implementation

The updated code will support both:
- Developer Token (current method, limited permissions)
- OAuth 2.0 Access Token (better permissions, can download files)

## Configuration File Format

Update `.box-api-config.json`:

```json
{
  "developer_token": "your_dev_token_here",
  "oauth2": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "access_token": "your_access_token",
    "refresh_token": "your_refresh_token",
    "redirect_uri": "http://localhost:5000/callback"
  }
}
```

Or for JWT (Server Authentication):

```json
{
  "jwt": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "public_key_id": "your_public_key_id",
    "private_key": "path/to/private_key.json",
    "enterprise_id": "your_enterprise_id"
  }
}
```

## Benefits of OAuth 2.0

- ✅ Better permissions control (specific scopes)
- ✅ Can download file content (with `content:read` scope)
- ✅ Can create/manage shared links
- ✅ More secure than Developer Tokens
- ✅ Supports token refresh for long-running applications

