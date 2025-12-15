#!/usr/bin/env node
/**
 * Check contents of Box folder 356056033736
 */

import { getBoxClient } from '/Users/a00288946/Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';

const FOLDER_ID = '356056033736';

async function main() {
  console.log(`📂 Checking contents of Box folder ${FOLDER_ID}...\n`);

  const boxClient = getBoxClient();

  try {
    const items = await boxClient.folders.getFolderItems(FOLDER_ID, {
      queryParams: {
        fields: ['id', 'name', 'type', 'modified_at'],
        limit: 1000
      }
    });

    console.log(`📊 Found ${items.entries.length} items:\n`);

    const files = items.entries.filter(item => item.type === 'file');
    const folders = items.entries.filter(item => item.type === 'folder');

    console.log(`📄 Files (${files.length}):`);
    for (const file of files) {
      console.log(`  - ${file.name} (${file.id})`);
    }

    console.log(`\n📁 Folders (${folders.length}):`);
    for (const folder of folders) {
      console.log(`  - ${folder.name} (${folder.id})`);
    }

    console.log(`\n🔍 Looking for DOCX files...`);
    const docxFiles = files.filter(f => f.name.endsWith('.docx') && !f.name.includes('~$'));
    console.log(`  Found ${docxFiles.length} DOCX files:`);
    for (const file of docxFiles) {
      console.log(`    - ${file.name} (${file.id})`);
    }

  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.statusCode) {
      console.error(`   Status: ${error.statusCode}`);
    }
    process.exit(1);
  }
}

main();

