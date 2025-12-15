#!/usr/bin/env node
/**
 * Debug script to check Box folder structure and naming
 */

import { getBoxClient } from '/Users/a00288946/Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';

const BASE_FOLDER_ID = '355471834847';
const SECTION_FOLDER_ID = '355470702235'; // Section 1 Overview folder_id

async function main() {
  const boxClient = getBoxClient();

  console.log('📁 Listing base folder contents...\n');
  const baseItems = await boxClient.folders.getFolderItems(BASE_FOLDER_ID, {
    queryParams: {
      fields: ['id', 'name', 'type'],
      limit: 100
    }
  });

  console.log('Base folder contains:');
  baseItems.entries.forEach(item => {
    if (item.type === 'folder') {
      console.log(`  📂 ${item.name} (${item.id})`);
    }
  });

  console.log('\n\n🔍 Checking section folder parent chain...\n');
  let currentFolderId = SECTION_FOLDER_ID;
  let depth = 0;

  while (currentFolderId && depth < 10) {
    const folder = await boxClient.folders.getFolderById(currentFolderId, {
      queryParams: {
        fields: ['id', 'name', 'type', 'parent']
      }
    });

    console.log(`Level ${depth}: ${folder.name} (${folder.id})`);

    if (folder.parent) {
      console.log(`  Parent: ${folder.parent.name} (${folder.parent.id})\n`);
      currentFolderId = folder.parent.id;
      depth++;
    } else {
      console.log(`  (Root folder)\n`);
      break;
    }
  }
}

main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});

