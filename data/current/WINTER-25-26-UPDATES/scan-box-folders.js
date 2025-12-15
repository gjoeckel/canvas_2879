#!/usr/bin/env node
/**
 * Scan Box folder structure and generate a complete list of all folders
 *
 * This script:
 * 1. Lists all Module folders in the base Box folder
 * 2. For each Module, lists all Section subfolders
 * 3. For each Section, lists all LA subfolders
 * 4. Outputs a structured list with Box folder IDs, names, and hierarchy
 */

import { writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { getBoxClient } from '/Users/a00288946/Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const BASE_FOLDER_ID = '355471834847';
const OUTPUT_FILE = join(__dirname, 'box-folder-structure.json');

/**
 * Extract module number from folder name (e.g., "Module-1" -> 1)
 */
function extractModuleNumber(name) {
  const match = name.match(/^Module[- ](\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

/**
 * Extract section numbers from folder name (e.g., "Section-1-2" -> { module: 1, section: 2 })
 */
function extractSectionNumbers(name) {
  const match = name.match(/^Section-(\d+)-(\d+)/i);
  if (match) {
    return {
      module: parseInt(match[1], 10),
      section: parseInt(match[2], 10)
    };
  }
  return null;
}

/**
 * Extract LA numbers from folder name (e.g., "LA-1-2-3" -> { module: 1, section: 2, la: 3 })
 */
function extractLANumbers(name) {
  const match = name.match(/^LA-(\d+)-(\d+)-(\d+)/i);
  if (match) {
    return {
      module: parseInt(match[1], 10),
      section: parseInt(match[2], 10),
      la: parseInt(match[3], 10)
    };
  }
  return null;
}

/**
 * List folder items
 */
async function listFolderItems(folderId) {
  const boxClient = getBoxClient();
  try {
    const folderItems = await boxClient.folders.getFolderItems(folderId, {
      queryParams: {
        fields: ['id', 'name', 'type'],
        limit: 1000
      }
    });

    return folderItems.entries.filter(item => item.type === 'folder');
  } catch (error) {
    console.error(`Error listing folder ${folderId}:`, error.message);
    return [];
  }
}

/**
 * Get folder details
 */
async function getFolderDetails(folderId) {
  const boxClient = getBoxClient();
  try {
    const folder = await boxClient.folders.getFolderById(folderId, {
      queryParams: {
        fields: ['id', 'name', 'type', 'modified_at']
      }
    });
    return folder;
  } catch (error) {
    console.error(`Error getting folder ${folderId}:`, error.message);
    return null;
  }
}

/**
 * Scan Box folder structure
 */
async function scanBoxStructure() {
  console.log('📁 Scanning Box folder structure...\n');

  const boxClient = getBoxClient();
  const structure = {
    base_folder_id: BASE_FOLDER_ID,
    scanned_at: new Date().toISOString(),
    start_here: null,
    modules: []
  };

  // List all folders in base folder
  console.log(`Listing folders in base folder ${BASE_FOLDER_ID}...`);
  const allFolders = await listFolderItems(BASE_FOLDER_ID);

  // Find Start Here folder
  const startHereFolder = allFolders.find(f =>
    f.name.toLowerCase().includes('start') || f.name.toLowerCase() === 'start-here'
  );

  if (startHereFolder) {
    console.log(`\n📂 Processing Start Here: ${startHereFolder.name} (${startHereFolder.id})`);

    const startHereData = {
      folder_name: startHereFolder.name,
      folder_id: startHereFolder.id,
      subfolders: []
    };

    // List subfolders in Start Here
    const startHereSubfolders = await listFolderItems(startHereFolder.id);
    console.log(`  Found ${startHereSubfolders.length} subfolders`);

    for (const subfolder of startHereSubfolders) {
      console.log(`    📂 ${subfolder.name} (${subfolder.id})`);
      startHereData.subfolders.push({
        folder_name: subfolder.name,
        folder_id: subfolder.id
      });
    }

    structure.start_here = startHereData;
  }

  // Filter Module folders
  const moduleFolders = allFolders.filter(folder => extractModuleNumber(folder.name) !== null);

  // Filter and sort Module folders
  const modules = moduleFolders
    .map(folder => ({
      folder,
      moduleNum: extractModuleNumber(folder.name)
    }))
    .filter(item => item.moduleNum !== null)
    .sort((a, b) => a.moduleNum - b.moduleNum);

  console.log(`Found ${modules.length} module folders\n`);

  // Process each module
  for (const { folder, moduleNum } of modules) {
    console.log(`📂 Processing Module ${moduleNum}: ${folder.name} (${folder.id})`);

    const moduleData = {
      module_number: moduleNum,
      folder_name: folder.name,
      folder_id: folder.id,
      sections: []
    };

    // List Section folders in this module
    const sectionFolders = await listFolderItems(folder.id);

    // Filter and sort Section folders
    const sections = sectionFolders
      .map(secFolder => ({
        folder: secFolder,
        numbers: extractSectionNumbers(secFolder.name)
      }))
      .filter(item => item.numbers && item.numbers.module === moduleNum)
      .sort((a, b) => a.numbers.section - b.numbers.section);

    console.log(`  Found ${sections.length} section folders`);

    // Process each section
    for (const { folder: sectionFolder, numbers: sectionNums } of sections) {
      console.log(`    📂 Processing Section ${sectionNums.module}-${sectionNums.section}: ${sectionFolder.name} (${sectionFolder.id})`);

      const sectionData = {
        section_number: sectionNums.section,
        folder_name: sectionFolder.name,
        folder_id: sectionFolder.id,
        las: []
      };

      // List LA folders in this section
      const laFolders = await listFolderItems(sectionFolder.id);

      // Filter and sort LA folders
      const las = laFolders
        .map(laFolder => ({
          folder: laFolder,
          numbers: extractLANumbers(laFolder.name)
        }))
        .filter(item =>
          item.numbers &&
          item.numbers.module === moduleNum &&
          item.numbers.section === sectionNums.section
        )
        .sort((a, b) => a.numbers.la - b.numbers.la);

      console.log(`      Found ${las.length} LA folders`);

      // Process each LA
      for (const { folder: laFolder, numbers: laNums } of las) {
        console.log(`        📂 Processing LA ${laNums.module}-${laNums.section}-${laNums.la}: ${laFolder.name} (${laFolder.id})`);

        const laData = {
          la_number: laNums.la,
          folder_name: laFolder.name,
          folder_id: laFolder.id
        };

        sectionData.las.push(laData);
      }

      moduleData.sections.push(sectionData);
    }

    structure.modules.push(moduleData);
    console.log('');
  }

  return structure;
}

/**
 * Main function
 */
async function main() {
  try {
    const structure = await scanBoxStructure();

    // Write to file
    console.log(`\n💾 Writing folder structure to ${OUTPUT_FILE}...`);
    writeFileSync(OUTPUT_FILE, JSON.stringify(structure, null, 2), 'utf8');

    // Print summary
    console.log('\n✅ Scan complete!\n');
    console.log('📊 Summary:');
    if (structure.start_here) {
      console.log(`  Start Here: 1 folder with ${structure.start_here.subfolders.length} subfolders`);
    }
    console.log(`  Modules: ${structure.modules.length}`);
    const totalSections = structure.modules.reduce((sum, m) => sum + m.sections.length, 0);
    const totalLAs = structure.modules.reduce((sum, m) =>
      sum + m.sections.reduce((s, sec) => s + sec.las.length, 0), 0);
    console.log(`  Sections: ${totalSections}`);
    console.log(`  LAs: ${totalLAs}`);
    const startHereCount = structure.start_here ? 1 + structure.start_here.subfolders.length : 0;
    console.log(`  Total folders: ${1 + startHereCount + structure.modules.length + totalSections + totalLAs}`);
    console.log(`\n📄 Structure saved to: ${OUTPUT_FILE}`);

  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

main();

