#!/usr/bin/env node
/**
 * Recursively scan Box folder 356056033736 and its subfolders for all DOCX files
 * Then update course-map.json with the correct Box file IDs
 */

import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { getBoxClient } from '/Users/a00288946/Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const COURSE_MAP_FILE = join(__dirname, 'course-map.json');
const ROOT_FOLDER_ID = '356056033736';

/**
 * Recursively scan folder for all DOCX files
 */
async function scanFolderRecursively(folderId, depth = 0, maxDepth = 10) {
  if (depth > maxDepth) {
    console.log(`  ⚠️  Max depth reached at ${depth}`);
    return [];
  }

  const boxClient = getBoxClient();
  const indent = '  '.repeat(depth);
  const files = [];

  try {
    const items = await boxClient.folders.getFolderItems(folderId, {
      queryParams: {
        fields: ['id', 'name', 'type', 'modified_at'],
        limit: 1000
      }
    });

    // Process files first
    for (const item of items.entries) {
      if (item.type === 'file' && item.name.endsWith('.docx') && !item.name.includes('~$')) {
        files.push({
          file_id: item.id,
          file_name: item.name,
          folder_id: folderId,
          modified_at: item.modified_at
        });
        console.log(`${indent}📄 ${item.name} (${item.id})`);
      }
    }

    // Then process folders recursively (skip node_modules and other irrelevant folders)
    const folders = items.entries.filter(item =>
      item.type === 'folder' &&
      !item.name.startsWith('.') &&
      item.name !== 'node_modules'
    );
    for (const folder of folders) {
      console.log(`${indent}📁 ${folder.name}/ (${folder.id})`);
      const subFiles = await scanFolderRecursively(folder.id, depth + 1, maxDepth);
      files.push(...subFiles);
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 150));
    }
  } catch (error) {
    console.error(`${indent}❌ Error scanning folder ${folderId}:`, error.message);
    if (error.statusCode === 401) {
      throw new Error('Authentication error - Box token may be expired');
    }
  }

  return files;
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
 * Find matching file in Box files array
 */
function findMatchingFile(boxFiles, targetFileName) {
  if (!targetFileName) return null;

  const normalized = normalizeFilename(targetFileName);

  // Try exact match first
  for (const file of boxFiles) {
    const fileNormalized = normalizeFilename(file.file_name);
    if (fileNormalized === normalized) {
      return file;
    }
  }

  // Try partial matches (in case of slight naming differences)
  for (const file of boxFiles) {
    const fileNormalized = normalizeFilename(file.file_name);
    if (fileNormalized.includes(normalized) || normalized.includes(fileNormalized)) {
      return file;
    }
  }

  return null;
}

/**
 * Update course map with Box file IDs
 */
function updateCourseMap(courseMap, boxFiles) {
  let updatedCount = 0;
  const unmatchedFiles = [];

  // Update Start Here pages
  if (courseMap.start_here && courseMap.start_here.subfolders) {
    for (const page of courseMap.start_here.subfolders) {
      if (page.box && page.box.file_name) {
        const match = findMatchingFile(boxFiles, page.box.file_name);
        if (match) {
          page.box.file_id = match.file_id;
          page.box.file_url = `https://usu.app.box.com/file/${match.file_id}`;
          page.box.word_online_url = `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${match.file_id}&sharedAccessCode=`;
          page.box.folder_id = match.folder_id;
          if (match.modified_at) {
            page.box.modified_at = match.modified_at;
          }
          updatedCount++;
          console.log(`  ✓ Updated: ${page.title} -> ${match.file_id}`);
        } else {
          unmatchedFiles.push(`Start Here: ${page.title} (${page.box.file_name})`);
        }
      }
    }
  }

  // Update Modules, Sections, and LAs recursively
  function updatePage(page, type) {
    if (page.box && page.box.file_name) {
      const match = findMatchingFile(boxFiles, page.box.file_name);
      if (match) {
        page.box.file_id = match.file_id;
        page.box.file_url = `https://usu.app.box.com/file/${match.file_id}`;
        page.box.word_online_url = `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${match.file_id}&sharedAccessCode=`;
        page.box.folder_id = match.folder_id;
        if (match.modified_at) {
          page.box.modified_at = match.modified_at;
        }
        updatedCount++;
        console.log(`  ✓ Updated: ${page.title} -> ${match.file_id}`);
      } else {
        unmatchedFiles.push(`${type}: ${page.title} (${page.box.file_name})`);
      }
    }

    // Recursively update sections and LAs
    if (page.sections) {
      for (const section of page.sections) {
        updatePage(section, 'Section');
        if (section.las) {
          for (const la of section.las) {
            updatePage(la, 'LA');
          }
        }
      }
    }
  }

  if (courseMap.modules) {
    for (const module of courseMap.modules) {
      updatePage(module, 'Module');
    }
  }

  return { updatedCount, unmatchedFiles };
}

/**
 * Main function
 */
async function main() {
  console.log('🔍 Scanning Box folder recursively for DOCX files...\n');
  console.log(`📂 Root folder: ${ROOT_FOLDER_ID}\n`);

  // Scan folder recursively
  const boxFiles = await scanFolderRecursively(ROOT_FOLDER_ID);

  console.log(`\n📊 Found ${boxFiles.length} DOCX files total\n`);

  if (boxFiles.length === 0) {
    console.log('⚠️  No DOCX files found. Aborting.');
    return;
  }

  // Read course map
  console.log('📖 Reading course-map.json...');
  const courseMap = JSON.parse(readFileSync(COURSE_MAP_FILE, 'utf8'));

  // Update course map
  console.log('\n🔄 Updating course-map.json with Box file IDs...\n');
  const { updatedCount, unmatchedFiles } = updateCourseMap(courseMap, boxFiles);

  // Update metadata
  courseMap.metadata.last_updated = new Date().toISOString();

  // Write updated course map
  console.log(`\n💾 Writing updated course-map.json...`);
  writeFileSync(COURSE_MAP_FILE, JSON.stringify(courseMap, null, 2), 'utf8');

  console.log(`\n✅ Update complete!`);
  console.log(`📊 Updated ${updatedCount} pages with Box file IDs`);
  console.log(`📄 Saved to: ${COURSE_MAP_FILE}`);

  if (unmatchedFiles.length > 0) {
    console.log(`\n⚠️  ${unmatchedFiles.length} pages could not be matched:`);
    for (const unmatched of unmatchedFiles) {
      console.log(`   - ${unmatched}`);
    }
  }
}

main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});

