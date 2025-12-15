#!/usr/bin/env node
/**
 * Update Box file IDs from a specific folder
 * Folder ID: 356056033736
 */

import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { getBoxClient } from '/Users/a00288946/Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const COURSE_MAP_FILE = join(__dirname, 'course-map.json');
const SOURCE_FOLDER_ID = '356056033736';

/**
 * Get all files from the Box folder, mapped by filename
 */
async function getFilesFromBoxFolder(folderId) {
  const boxClient = getBoxClient();

  console.log(`📂 Fetching files from Box folder ${folderId}...`);

  try {
    const items = await boxClient.folders.getFolderItems(folderId, {
      queryParams: {
        fields: ['id', 'name', 'type', 'modified_at'],
        limit: 1000
      }
    });

    const files = {};
    for (const item of items.entries) {
      if (item.type === 'file' && item.name.endsWith('.docx') && !item.name.includes('~$')) {
        // Normalize filename for matching
        const normalizedName = item.name.toLowerCase().replace(/[^a-z0-9]/g, '');
        files[normalizedName] = {
          file_id: item.id,
          file_name: item.name,
          modified_at: item.modified_at
        };
        console.log(`  ✓ Found: ${item.name} (${item.id})`);
      }
    }

    console.log(`\n📊 Found ${Object.keys(files).length} DOCX files\n`);
    return files;
  } catch (error) {
    console.error(`❌ Error fetching folder items:`, error.message);
    throw error;
  }
}

/**
 * Normalize filename for matching
 */
function normalizeFilename(filename) {
  if (!filename) return '';
  return filename.toLowerCase()
    .replace(/[^a-z0-9]/g, '')
    .replace(/^module/, 'module')
    .replace(/^section/, 'section')
    .replace(/\.docx$/, '');
}

/**
 * Find matching file in Box files map
 */
function findMatchingFile(boxFiles, targetFileName) {
  if (!targetFileName) return null;

  const normalized = normalizeFilename(targetFileName);

  // Try exact match first
  if (boxFiles[normalized]) {
    return boxFiles[normalized];
  }

  // Try partial matches
  for (const [key, file] of Object.entries(boxFiles)) {
    if (key.includes(normalized) || normalized.includes(key)) {
      return file;
    }
  }

  return null;
}

/**
 * Update course map with Box file IDs
 */
async function updateCourseMap(courseMap, boxFiles) {
  let updatedCount = 0;

  // Update Start Here pages
  if (courseMap.start_here && courseMap.start_here.subfolders) {
    for (const page of courseMap.start_here.subfolders) {
      if (page.box && page.box.file_name) {
        const match = findMatchingFile(boxFiles, page.box.file_name);
        if (match) {
          page.box.file_id = match.file_id;
          page.box.file_url = `https://usu.app.box.com/file/${match.file_id}`;
          page.box.word_online_url = `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${match.file_id}&sharedAccessCode=`;
          if (match.modified_at) {
            page.box.modified_at = match.modified_at;
          }
          updatedCount++;
          console.log(`  ✓ Updated: ${page.title} -> ${match.file_id}`);
        }
      }
    }
  }

  // Update Modules
  function updatePage(page, type) {
    if (page.box && page.box.file_name) {
      const match = findMatchingFile(boxFiles, page.box.file_name);
      if (match) {
        page.box.file_id = match.file_id;
        page.box.file_url = `https://usu.app.box.com/file/${match.file_id}`;
        page.box.word_online_url = `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${match.file_id}&sharedAccessCode=`;
        if (match.modified_at) {
          page.box.modified_at = match.modified_at;
        }
        updatedCount++;
        console.log(`  ✓ Updated: ${page.title} -> ${match.file_id}`);
      }
    }

    // Recursively update sections and LAs
    if (page.sections) {
      for (const section of page.sections) {
        updatePage(section, 'section');
        if (section.las) {
          for (const la of section.las) {
            updatePage(la, 'la');
          }
        }
      }
    }
  }

  if (courseMap.modules) {
    for (const module of courseMap.modules) {
      updatePage(module, 'module');
    }
  }

  return updatedCount;
}

/**
 * Main function
 */
async function main() {
  console.log('🔍 Updating Box file IDs from folder...\n');

  // Read course map
  console.log('📖 Reading course-map.json...');
  const courseMap = JSON.parse(readFileSync(COURSE_MAP_FILE, 'utf8'));

  // Get files from Box folder
  const boxFiles = await getFilesFromBoxFolder(SOURCE_FOLDER_ID);

  if (Object.keys(boxFiles).length === 0) {
    console.log('⚠️  No DOCX files found in the folder. Aborting.');
    return;
  }

  // Update course map
  console.log('🔄 Updating course-map.json with Box file IDs...\n');
  const updatedCount = await updateCourseMap(courseMap, boxFiles);

  // Update metadata
  courseMap.metadata.last_updated = new Date().toISOString();

  // Write updated course map
  console.log(`\n💾 Writing updated course-map.json...`);
  writeFileSync(COURSE_MAP_FILE, JSON.stringify(courseMap, null, 2), 'utf8');

  console.log(`\n✅ Update complete!`);
  console.log(`📊 Updated ${updatedCount} pages with Box file IDs from folder ${SOURCE_FOLDER_ID}`);
  console.log(`📄 Saved to: ${COURSE_MAP_FILE}`);
}

main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});

