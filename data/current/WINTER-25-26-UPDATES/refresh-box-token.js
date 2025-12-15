#!/usr/bin/env node
/**
 * Refresh Box OAuth Access Token
 *
 * Uses BOX_REFRESH_TOKEN to get a new BOX_ACCESS_TOKEN
 */

import { BoxOAuth, OAuthConfig } from 'box-node-sdk';

const CLIENT_ID = process.env.BOX_CLIENT_ID;
const CLIENT_SECRET = process.env.BOX_CLIENT_SECRET;
const REFRESH_TOKEN = process.env.BOX_REFRESH_TOKEN;

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error('❌ BOX_CLIENT_ID and BOX_CLIENT_SECRET must be set');
  process.exit(1);
}

if (!REFRESH_TOKEN) {
  console.error('❌ BOX_REFRESH_TOKEN must be set');
  console.error('   Run get-oauth-token.js to get initial tokens');
  process.exit(1);
}

console.log('🔄 Refreshing Box OAuth access token...\n');

const config = new OAuthConfig({
  clientId: CLIENT_ID,
  clientSecret: CLIENT_SECRET,
});

const oauth = new BoxOAuth({ config });

try {
  // Refresh the access token
  const tokenInfo = await oauth.getTokensRefreshGrant(REFRESH_TOKEN);

  const newAccessToken = tokenInfo.accessToken;
  const newRefreshToken = tokenInfo.refreshToken || REFRESH_TOKEN; // Use new refresh token if provided

  console.log('✅ Access token refreshed successfully!\n');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📝 Update your environment:\n');
  console.log(`export BOX_ACCESS_TOKEN="${newAccessToken}"`);
  if (newRefreshToken !== REFRESH_TOKEN) {
    console.log(`export BOX_REFRESH_TOKEN="${newRefreshToken}"`);
  }
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  console.log('Then run: source ~/.zshrc');
  console.log('Or set it in your current shell session.\n');

} catch (error) {
  console.error('❌ Error refreshing token:', error.message);
  console.error('\n💡 You may need to re-authorize:');
  console.error('   node /Users/a00288946/Agents/cursor-ops/mcp-box-minimal/scripts/get-oauth-token.js');
  process.exit(1);
}
