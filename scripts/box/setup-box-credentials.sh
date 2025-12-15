#!/bin/bash
# Setup Box API Credentials
# This script helps set up Box API authentication

set -e

COURSE_DIR="/Users/a00288946/Projects/canvas_2879"
CONFIG_FILE="${COURSE_DIR}/.box-api-config.json"

echo "🔑 Box API Credentials Setup"
echo "=" | head -c 60 && echo ""
echo ""

# Check if config already exists
if [ -f "$CONFIG_FILE" ]; then
    echo "✅ Config file exists: $CONFIG_FILE"
    echo "   Checking for valid tokens..."

    if grep -q "access_token\|developer_token" "$CONFIG_FILE" 2>/dev/null; then
        echo "   ✅ Tokens found in config"
        echo ""
        echo "Current credentials are valid!"
        exit 0
    fi
fi

echo "📝 Choose authentication method:"
echo ""
echo "1) Developer Token (Quick - 60 min, good for uploads)"
echo "2) OAuth 2.0 (Long-term, requires Client ID/Secret)"
echo ""
read -p "Enter choice [1 or 2]: " choice

case $choice in
    1)
        echo ""
        echo "📋 Developer Token Setup"
        echo "-" | head -c 40 && echo ""
        echo ""
        echo "1. Go to: https://app.box.com/developers/console"
        echo "2. Select your app"
        echo "3. Click 'Generate Developer Token'"
        echo "4. Copy the token"
        echo ""
        read -p "Paste your Developer Token: " token

        if [ -z "$token" ]; then
            echo "❌ No token provided"
            exit 1
        fi

        # Create config file
        cat > "$CONFIG_FILE" << EOF
{
  "developer_token": "$token"
}
EOF

        echo ""
        echo "✅ Developer token saved to $CONFIG_FILE"
        echo ""
        echo "💡 Note: Developer tokens expire in 60 minutes"
        echo "   For long-term use, consider OAuth 2.0"
        ;;

    2)
        echo ""
        echo "📋 OAuth 2.0 Setup"
        echo "-" | head -c 40 && echo ""
        echo ""

        # Check for environment variables first
        client_id="${BOX_CLIENT_ID:-}"
        client_secret="${BOX_CLIENT_SECRET:-}"

        if [ -z "$client_id" ] || [ -z "$client_secret" ]; then
            echo "⚠️  BOX_CLIENT_ID and BOX_CLIENT_SECRET not found in environment"
            echo ""
            echo "Please set them first:"
            echo "  export BOX_CLIENT_ID='your_client_id'"
            echo "  export BOX_CLIENT_SECRET='your_client_secret'"
            echo ""
            echo "Or enter them now:"
            read -p "Enter Client ID: " client_id
            read -p "Enter Client Secret: " client_secret

            if [ -z "$client_id" ] || [ -z "$client_secret" ]; then
                echo "❌ Client ID and Secret are required"
                exit 1
            fi
        else
            echo "✅ Found BOX_CLIENT_ID and BOX_CLIENT_SECRET in environment"
        fi

        echo ""
        echo "🔄 Starting OAuth flow..."
        echo ""

        cd "$COURSE_DIR"
        python3 scripts/box/get-box-oauth-token.py \
            --client-id "$client_id" \
            --client-secret "$client_secret"
        ;;

    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Setup complete!"
echo ""
echo "You can now use Box API scripts:"
echo "  - Upload directory: python3 scripts/box/upload-directory-to-box.py --folder-id FOLDER_ID"
echo "  - Get file IDs: python3 scripts/box/get-box-file-ids-api.py"
