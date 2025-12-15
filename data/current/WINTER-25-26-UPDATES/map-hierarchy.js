#!/usr/bin/env node
/**
 * Map module > section > LA hierarchy in course-map.json
 *
 * This script:
 * 1. Reads course-map.json
 * 2. For each page, uses Box folder_id to determine parent hierarchy
 * 3. Maps each page to its module/section position
 * 4. Updates course-map.json with hierarchy information
 */

import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Import Box client
import { getBoxClient } from '/Users/a00288946/Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';

const COURSE_MAP_PATH = join(__dirname, 'course-map.json');
const BASE_FOLDER_ID = '355471834847';

/**
 * Get file details including parent folder
 */
async function getFileInfo(fileId) {
  const boxClient = getBoxClient();
  try {
    const file = await boxClient.files.getFileById(fileId, {
      queryParams: {
        fields: ['id', 'name', 'parent']
      }
    });
    return {
      id: file.id,
      name: file.name,
      parent: file.parent ? {
        id: file.parent.id,
        name: file.parent.name
      } : null
    };
  } catch (error) {
    console.error(`Error getting file ${fileId}:`, error.message);
    return null;
  }
}

/**
 * Get folder details including parent
 */
async function getFolderInfo(folderId) {
  const boxClient = getBoxClient();
  try {
    const folder = await boxClient.folders.getFolderById(folderId, {
      queryParams: {
        fields: ['id', 'name', 'type', 'parent']
      }
    });
    return {
      id: folder.id,
      name: folder.name,
      parent: folder.parent ? {
        id: folder.parent.id,
        name: folder.parent.name
      } : null
    };
  } catch (error) {
    console.error(`Error getting folder ${folderId}:`, error.message);
    return null;
  }
}

/**
 * Traverse up the folder tree to find module folder
 */
async function findModuleFolder(folderId, baseFolderId) {
  let currentFolderId = folderId;
  const maxDepth = 10; // Safety limit
  let depth = 0;
  const path = []; // Track the path for debugging

  while (currentFolderId && depth < maxDepth) {
    const folderInfo = await getFolderInfo(currentFolderId);
    if (!folderInfo) break;

    path.push({ id: folderInfo.id, name: folderInfo.name });

    // Check if this is a module folder (handles "Module-1" and "Module 1" formats)
    const name = folderInfo.name || '';
    const moduleMatch = name.match(/^Module[- ](\d+)/i);
    if (moduleMatch) {
      const moduleNum = parseInt(moduleMatch[1], 10);
      return {
        folder_id: folderInfo.id,
        folder_name: name,
        module_number: moduleNum,
        path: path.reverse() // Reverse so it's from root to module
      };
    }


    // Stop if we've reached the base folder
    if (currentFolderId === baseFolderId) break;

    // Move to parent
    if (folderInfo.parent) {
      currentFolderId = folderInfo.parent.id;
      depth++;
    } else {
      break;
    }
  }

  return null;
}

/**
 * Get parent folder chain for a file
 */
async function getParentChainForFile(fileId, baseFolderId) {
  const fileInfo = await getFileInfo(fileId);
  if (!fileInfo || !fileInfo.parent) {
    return null;
  }

  return await findModuleFolder(fileInfo.parent.id, baseFolderId);
}

/**
 * Extract module number from folder name
 * Handles both "Module-1" and "Module 1" formats
 */
function extractModuleNumber(name) {
  const match = name.match(/Module[- ](\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

/**
 * Extract section number from folder/page name
 * Handles both "Section-1" and "Section 1" formats
 * Also handles "Section-X-Y" where Y is the section number
 */
function extractSectionNumber(name) {
  // Try "Section-X-Y" format first (e.g., "Section-1-1")
  const sectionXYMatch = name.match(/Section[- ](\d+)[- ](\d+)/i);
  if (sectionXYMatch) {
    return parseInt(sectionXYMatch[2], 10); // Return the Y (section number)
  }
  // Try "Section X" or "Section-X" format
  const match = name.match(/Section[- ](\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

/**
 * Extract module number from section folder name
 * Handles "Section-X-Y" format where X is the module number
 */
function extractModuleNumberFromSection(name) {
  const match = name.match(/^Section-(\d+)-\d+/i);
  return match ? parseInt(match[1], 10) : null;
}

/**
 * Determine hierarchy for a page based on its folder and metadata
 */
async function determineHierarchy(page, baseFolderId, courseMap) {
  const hierarchy = {
    module: null,
    section: null,
    la: null
  };

  // If it's a module page, set module info
  if (page.metadata?.type === 'module') {
    const moduleNum = extractModuleNumber(page.title || page.id);
    if (moduleNum) {
      hierarchy.module = {
        number: moduleNum,
        id: page.id,
        title: page.title,
        folder_id: page.box?.folder_id
      };
    }
    return hierarchy;
  }

  // For sections and LAs, find parent module by traversing up from file's parent folder
  if (page.box?.file_id) {
    const moduleInfo = await getParentChainForFile(page.box.file_id, baseFolderId);
    if (moduleInfo) {
      hierarchy.module = {
        number: moduleInfo.module_number,
        folder_id: moduleInfo.folder_id,
        folder_name: moduleInfo.folder_name
      };
    } else {
      // Fallback: try to extract module number from section folder name (Section-X-Y format)
      if (page.box?.folder_id) {
        const folderInfo = await getFolderInfo(page.box.folder_id);
        if (folderInfo) {
          const moduleNum = extractModuleNumberFromSection(folderInfo.name);
          if (moduleNum) {
            // Find the module page in the course map
            const modulePage = courseMap.pages.find(p =>
              p.metadata?.type === 'module' && extractModuleNumber(p.title || p.id) === moduleNum
            );
            if (modulePage) {
              hierarchy.module = {
                number: moduleNum,
                id: modulePage.id,
                title: modulePage.title,
                folder_id: modulePage.box?.folder_id
              };
            }
          }
        }
      }
    }
  }

  // If it's a section page, set section info
  if (page.metadata?.type === 'section') {
    const sectionNum = extractSectionNumber(page.title || page.id);
    if (sectionNum) {
      hierarchy.section = {
        number: sectionNum,
        id: page.id,
        title: page.title,
        folder_id: page.box?.folder_id
      };
    }
  }

  // TODO: LA pages would be handled similarly
  // if (page.metadata?.type === 'la') { ... }

  return hierarchy;
}

/**
 * Main function
 */
async function main() {
  console.log('📖 Reading course-map.json...');
  const courseMap = JSON.parse(readFileSync(COURSE_MAP_PATH, 'utf8'));

  console.log(`\n🔍 Mapping hierarchy for ${courseMap.pages.length} pages...`);

  // Process each page
  for (let i = 0; i < courseMap.pages.length; i++) {
    const page = courseMap.pages[i];
    console.log(`\n[${i + 1}/${courseMap.pages.length}] Processing: ${page.title || page.id}`);

    const hierarchy = await determineHierarchy(page, BASE_FOLDER_ID, courseMap);

    // Add hierarchy to page
    if (!page.hierarchy) {
      page.hierarchy = {};
    }
    page.hierarchy = hierarchy;

    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  // Update metadata
  courseMap.metadata.last_updated = new Date().toISOString();

  // Write back to file
  console.log('\n💾 Writing updated course-map.json...');
  writeFileSync(COURSE_MAP_PATH, JSON.stringify(courseMap, null, 2), 'utf8');

  console.log('✅ Hierarchy mapping complete!');

  // Print summary
  console.log('\n📊 Summary:');
  const modules = courseMap.pages.filter(p => p.metadata?.type === 'module');
  const sections = courseMap.pages.filter(p => p.metadata?.type === 'section');
  console.log(`  Modules: ${modules.length}`);
  console.log(`  Sections: ${sections.length}`);
  console.log(`  Total pages: ${courseMap.pages.length}`);
}

main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});

