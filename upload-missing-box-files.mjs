#!/usr/bin/env node
/**
 * Upload missing files to Box folders using Box SDK
 */

import { getBoxClient } from '../../Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';
import { readFileSync } from 'fs';
import { Readable } from 'stream';

const FOLDER_IDS = {
  '2-course-details': '356023244847',
  '3-terms-of-use': '356022969543'
};

const FILES_TO_UPLOAD = [
  {
    localPath: '/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/Start-Here/2-course-details/course_details_local.html',
    fileName: 'course_details_local.html',
    folderId: FOLDER_IDS['2-course-details'],
    folderName: '2-course-details'
  },
  {
    localPath: '/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/Start-Here/2-course-details/course_details.docx',
    fileName: 'course_details.docx',
    folderId: FOLDER_IDS['2-course-details'],
    folderName: '2-course-details'
  },
  {
    localPath: '/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/Start-Here/3-terms-of-use/terms_of_use_local.html',
    fileName: 'terms_of_use_local.html',
    folderId: FOLDER_IDS['3-terms-of-use'],
    folderName: '3-terms-of-use'
  },
  {
    localPath: '/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/Start-Here/3-terms-of-use/terms_of_use.docx',
    fileName: 'terms_of_use.docx',
    folderId: FOLDER_IDS['3-terms-of-use'],
    folderName: '3-terms-of-use'
  }
];

async function fileExists(client, folderId, fileName) {
  try {
    const items = await client.folders.getFolderItems(folderId, {
      queryParams: { fields: ['id', 'name', 'type'] }
    });
    return items.entries.some(item => item.type === 'file' && item.name === fileName);
  } catch (error) {
    return false;
  }
}

async function uploadFile(client, folderId, fileName, filePath) {
  // Check if file exists
  const exists = await fileExists(client, folderId, fileName);
  if (exists) {
    console.log(`  ⊘ File already exists, skipping upload`);
    return { skipped: true };
  }

  // Read file content
  const fileContent = readFileSync(filePath);

  // Upload file
  const uploadedFile = await client.uploads.uploadFile({
    attributes: {
      name: fileName,
      parent: { id: folderId }
    },
    file: Readable.from(fileContent)
  });

  return uploadedFile.entries[0];
}

async function main() {
  try {
    console.log('📤 Uploading missing files to Box folders...\n');

    const client = getBoxClient();
    console.log('✓ Box client initialized\n');

    let uploadedCount = 0;
    let skippedCount = 0;

    for (const fileInfo of FILES_TO_UPLOAD) {
      try {
        console.log(`📦 Uploading ${fileInfo.fileName} → ${fileInfo.folderName}/`);
        const result = await uploadFile(client, fileInfo.folderId, fileInfo.fileName, fileInfo.localPath);

        if (result.skipped) {
          skippedCount++;
        } else {
          console.log(`  ✓ Uploaded successfully (ID: ${result.id})\n`);
          uploadedCount++;
        }
      } catch (error) {
        console.error(`  ✗ Error: ${error.message}\n`);
      }
    }

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`✅ Upload complete!`);
    console.log(`   Uploaded: ${uploadedCount} files`);
    console.log(`   Skipped: ${skippedCount} files`);
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    process.exit(1);
  }
}

main();
