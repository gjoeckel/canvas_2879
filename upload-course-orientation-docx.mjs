#!/usr/bin/env node
/**
 * Upload course_orientation.docx to Box 1-course-orientation folder
 */

import { getBoxClient } from '../../Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';
import { readFileSync } from 'fs';
import { Readable } from 'stream';

const FOLDER_ID = '356024870284'; // 1-course-orientation
const LOCAL_FILE_PATH = '/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/Start-Here/1-course-orientation/course_orientation.docx';
const FILE_NAME = 'course_orientation.docx';

async function uploadFile(client, folderId, fileName, filePath) {
  // Check if file already exists
  const items = await client.folders.getFolderItems(folderId, {
    queryParams: { fields: ['id', 'name', 'type'] }
  });

  const existing = items.entries.find(item => item.type === 'file' && item.name === fileName);

  // Read file content
  const fileContent = readFileSync(filePath);
  const fileStream = Readable.from(fileContent);

  if (existing) {
    console.log(`  ⚠️  File already exists (ID: ${existing.id})`);
    console.log(`  🔄 Uploading new version...`);

    // Upload new version using uploads.uploadFileVersion
    try {
      const uploadedFile = await client.uploads.uploadFileVersion(existing.id, {
        attributes: {
          name: fileName,
        },
        file: fileStream,
      });
      return uploadedFile.entries[0];
    } catch (error) {
      console.error(`  ✗ Failed to upload new version: ${error.message}`);
      throw error;
    }
  } else {
    // Upload new file
    console.log(`  📤 Uploading new file...`);
    const uploadedFile = await client.uploads.uploadFile({
      attributes: {
        name: fileName,
        parent: { id: folderId }
      },
      file: fileStream
    });

    return uploadedFile.entries[0];
  }
}

async function main() {
  try {
    console.log('📤 Uploading course_orientation.docx to Box...\n');
    console.log(`Local file: ${LOCAL_FILE_PATH}`);
    console.log(`Target folder: 1-course-orientation (${FOLDER_ID})\n`);

    const client = getBoxClient();
    console.log('✓ Box client initialized\n');

    console.log(`📦 Processing ${FILE_NAME}...`);
    const result = await uploadFile(client, FOLDER_ID, FILE_NAME, LOCAL_FILE_PATH);

    console.log(`  ✓ Uploaded successfully!`);
    console.log(`  File ID: ${result.id}`);
    console.log(`  File name: ${result.name}`);
    if (result.size) {
      console.log(`  File size: ${(result.size / 1024).toFixed(2)} KB`);
    }

    console.log('\n✅ Upload complete!');
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

main();
