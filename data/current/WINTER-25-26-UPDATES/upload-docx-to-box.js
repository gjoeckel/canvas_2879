#!/usr/bin/env node
/**
 * Upload DOCX files to Box
 *
 * This script:
 * 1. Finds all Module and Section DOCX files
 * 2. Matches them to Box folder structure
 * 3. Uploads each DOCX file to the corresponding Box folder
 */

import { readFileSync, existsSync } from 'fs';
import { dirname, basename, join } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Import Box client - use absolute path
import { getBoxClient } from '/Users/a00288946/Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';

/**
 * Find or create Box folder by name
 */
async function findOrCreateFolder(parentFolderId, folderName) {
  const boxClient = getBoxClient();

  try {
    // List items in parent folder
    const folderItems = await boxClient.folders.getFolderItems(parentFolderId, {
      queryParams: {
        fields: ['id', 'name', 'type'],
        limit: 1000
      }
    });

    // Check if folder exists
    const existingFolder = folderItems.entries.find(
      item => item.type === 'folder' && item.name === folderName
    );

    if (existingFolder) {
      return existingFolder.id;
    }

    // Create folder if it doesn't exist
    console.log(`  ➕ Creating Box folder: ${folderName}`);
    const newFolder = await boxClient.folders.createFolder({
      name: folderName,
      parent: {
        id: parentFolderId
      }
    });

    return newFolder.id;
  } catch (error) {
    console.error(`  ❌ Error finding/creating folder ${folderName}: ${error.message}`);
    throw error;
  }
}

/**
 * Upload file to Box
 */
async function uploadFileToBox(folderId, filePath, fileName) {
  const boxClient = getBoxClient();

  try {
    // Read file as buffer
    const fileBuffer = readFileSync(filePath);
    const fileSize = (fileBuffer.length / 1024).toFixed(2);

    console.log(`  📤 Uploading: ${fileName} (${fileSize} KB)`);

    // Check if file already exists in folder
    const folderItems = await boxClient.folders.getFolderItems(folderId, {
      queryParams: {
        fields: ['id', 'name', 'type'],
        limit: 1000
      }
    });

    const existingFile = folderItems.entries.find(
      item => item.type === 'file' && item.name === fileName
    );

    if (existingFile) {
      console.log(`  ⚠️  File already exists: ${fileName} (${existingFile.id})`);
      console.log(`  💡 To update, delete the existing file first or use file versioning`);
      return {
        file_id: existingFile.id,
        file_name: fileName,
        status: 'exists',
        skipped: true
      };
    }

    // Upload file
    const { Readable } = await import('stream');
    const uploadedFile = await boxClient.uploads.uploadFile({
      attributes: {
        name: fileName,
        parent: {
          id: folderId
        }
      },
      file: Readable.from(fileBuffer)
    });

    const result = uploadedFile.entries[0];
    console.log(`  ✅ Uploaded: ${result.name} (${result.id})`);

    return {
      file_id: result.id,
      file_name: result.name,
      size: result.size,
      status: 'uploaded',
      skipped: false
    };
  } catch (error) {
    console.error(`  ❌ Error uploading ${fileName}: ${error.message}`);
    return {
      file_name: fileName,
      status: 'error',
      error: error.message,
      skipped: false
    };
  }
}

/**
 * Find all Module and Section DOCX files
 */
function findDocxFiles(rootDir) {
  const docxFiles = [];

  // Find Module DOCX files (in Module-* directories)
  const moduleFiles = execSync(
    `find "${rootDir}" -type d -name "Module-*" -exec find {} -maxdepth 1 -name "Module*.docx" -type f \\;`,
    { encoding: 'utf-8' }
  ).trim().split('\n').filter(Boolean);

  docxFiles.push(...moduleFiles);

  // Find Section DOCX files (in Section-* directories)
  const sectionFiles = execSync(
    `find "${rootDir}" -path "*/Section-*/*.docx" -name "Section*.docx" -type f`,
    { encoding: 'utf-8' }
  ).trim().split('\n').filter(Boolean);

  docxFiles.push(...sectionFiles);

  return docxFiles.sort();
}

/**
 * Get Box folder ID for a given local path
 */
async function getBoxFolderId(rootBoxFolderId, localPath, rootDir) {
  const boxClient = getBoxClient();

  // Get relative path from root
  const relativePath = localPath.replace(rootDir + '/', '');
  const pathParts = relativePath.split('/').filter(Boolean);

  // Remove filename (last part)
  pathParts.pop();

  // Start from root Box folder
  let currentFolderId = rootBoxFolderId;

  // Navigate/create folder structure
  for (const folderName of pathParts) {
    currentFolderId = await findOrCreateFolder(currentFolderId, folderName);
  }

  return currentFolderId;
}

/**
 * Main upload function
 */
async function uploadDocxFilesToBox(rootDir, rootBoxFolderId) {
  console.log('📤 Uploading DOCX files to Box...\n');
  console.log(`📁 Root directory: ${rootDir}`);
  console.log(`📦 Box folder ID: ${rootBoxFolderId}\n`);

  // Find all DOCX files
  const docxFiles = findDocxFiles(rootDir);

  if (docxFiles.length === 0) {
    console.log('⚠️  No DOCX files found');
    return;
  }

  console.log(`Found ${docxFiles.length} DOCX files:\n`);

  const results = {
    uploaded: 0,
    skipped: 0,
    errors: 0,
    files: []
  };

  for (const filePath of docxFiles) {
    const relativePath = filePath.replace(rootDir + '/', '');
    const fileName = basename(filePath);

    console.log(`📄 ${relativePath}`);

    try {
      // Get Box folder ID for this file
      const boxFolderId = await getBoxFolderId(rootBoxFolderId, filePath, rootDir);

      // Upload file
      const result = await uploadFileToBox(boxFolderId, filePath, fileName);

      results.files.push({
        path: relativePath,
        ...result
      });

      if (result.skipped) {
        results.skipped++;
      } else if (result.status === 'uploaded') {
        results.uploaded++;
      } else {
        results.errors++;
      }
    } catch (error) {
      console.error(`  ❌ Fatal error: ${error.message}`);
      results.errors++;
      results.files.push({
        path: relativePath,
        status: 'error',
        error: error.message
      });
    }

    console.log(''); // Empty line for readability
  }

  // Summary
  console.log('📊 Upload Summary:');
  console.log(`  ✅ Uploaded: ${results.uploaded}`);
  console.log(`  ⏭️  Skipped: ${results.skipped}`);
  console.log(`  ❌ Errors: ${results.errors}`);
  console.log(`  📄 Total: ${docxFiles.length}`);

  return results;
}

// Main execution
const rootDir = process.argv[2] || __dirname;
const rootBoxFolderId = process.argv[3] || '355471834847';

if (!existsSync(rootDir)) {
  console.error(`❌ Directory not found: ${rootDir}`);
  process.exit(1);
}

uploadDocxFilesToBox(rootDir, rootBoxFolderId)
  .then(() => {
    console.log('\n✅ Upload complete!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Fatal error:', error);
    process.exit(1);
  });
