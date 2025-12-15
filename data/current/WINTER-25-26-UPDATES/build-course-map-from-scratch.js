#!/usr/bin/env node
/**
 * Build course-map.json from scratch using Box folder structure and filesystem
 *
 * This script:
 * 1. Reads box-folder-structure.json (folder IDs from Box)
 * 2. Scans filesystem for DOCX files and HTML files
 * 3. Optionally merges existing course-map.json data
 * 4. Builds hierarchical JSON structure (start_here, modules > sections > las)
 */

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from 'fs';
import { join, dirname, basename, extname, relative } from 'path';
import { fileURLToPath } from 'url';
import { getBoxClient } from '/Users/a00288946/Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const BOX_STRUCTURE_FILE = join(__dirname, 'box-folder-structure.json');
const EXISTING_COURSE_MAP_FILE = join(__dirname, 'course-map.json');
const OUTPUT_FILE = join(__dirname, 'course-map.json');
const BASE_DIR = __dirname;
const GITHUB_PAGES_DIR = join(__dirname, '../../../github-pages');
const REPO_BASE_PATH = 'data/current/WINTER-25-26-UPDATES';

/**
 * Convert filename to slug
 */
function filenameToSlug(filename) {
  return basename(filename, extname(filename))
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/_/g, '-')
    .replace(/[^a-z0-9-]/g, '');
}

/**
 * Convert filename to title
 */
function filenameToTitle(filename) {
  return basename(filename, extname(filename))
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Find DOCX file in a directory
 */
function findDocxInDir(dir) {
  try {
    const entries = readdirSync(dir);
    const docxFiles = entries.filter(e => e.endsWith('.docx') && !e.includes('~$'));
    if (docxFiles.length > 0) {
      return docxFiles[0]; // Return first DOCX file
    }
  } catch (err) {
    // Ignore errors
  }
  return null;
}

/**
 * Find local HTML file in a directory
 */
function findLocalHtmlInDir(dir) {
  try {
    const entries = readdirSync(dir);
    const htmlFiles = entries.filter(e => e.endsWith('_local.html'));
    if (htmlFiles.length > 0) {
      return htmlFiles[0]; // Return first local HTML file
    }
  } catch (err) {
    // Ignore errors
  }
  return null;
}

/**
 * Get Box file ID from folder (find DOCX file in folder)
 */
async function getBoxFileIdFromFolder(folderId) {
  const boxClient = getBoxClient();
  try {
    const items = await boxClient.folders.getFolderItems(folderId, {
      queryParams: {
        fields: ['id', 'name', 'type'],
        limit: 1000
      }
    });

    const docxFile = items.entries.find(item =>
      item.type === 'file' && item.name.endsWith('.docx') && !item.name.includes('~$')
    );

    return docxFile ? docxFile.id : null;
  } catch (error) {
    console.error(`Error getting file from folder ${folderId}:`, error.message);
    return null;
  }
}

/**
 * Build page data structure
 */
function buildPageData(item, type, folderPath, folderId) {
  const docxFilename = findDocxInDir(folderPath);
  const localHtmlFilename = findLocalHtmlInDir(folderPath);

  const slug = docxFilename ? filenameToSlug(docxFilename) : null;
  const title = docxFilename ? filenameToTitle(docxFilename) : item.title || '';

  // Build GitHub paths
  const githubPathBase = slug ? `pages/${slug}` : null;

  const pageData = {
    id: slug || `unknown-${type}`,
    title: title,
    folder_name: item.folder_name,
    box_folder_id: folderId,
    order: item.order || 0,
    status: 'draft',
    canvas: {
      url: null,
      page_id: slug || null,
      published: false,
      published_at: null
    },
    github: {
      repository: 'main',
      source_docx: githubPathBase ? {
        path: `${githubPathBase}/${slug}.docx`,
        branch: 'main'
      } : null,
      canvas_copy: githubPathBase ? {
        path: `${githubPathBase}/canvas-copy.html`,
        branch: 'main'
      } : null,
      with_assets: githubPathBase ? {
        path: `${githubPathBase}/index.html`,
        branch: 'main'
      } : null,
      local_html_path: localHtmlFilename ?
        relative(GITHUB_PAGES_DIR, join(folderPath, localHtmlFilename))
          .replace(/\\/g, '/') : null
    },
    box: {
      file_id: null, // Will be populated from Box
      file_name: docxFilename || null,
      file_url: null,
      word_online_url: null,
      folder_id: folderId,
      modified_at: null,
      version: 1
    },
    sync: {
      last_synced: null,
      sync_status: 'pending',
      sync_errors: []
    },
    metadata: {
      type: type,
      created: new Date().toISOString()
    }
  };

  return pageData;
}

/**
 * Build start here structure
 */
async function buildStartHere(startHereData) {
  if (!startHereData) return null;

  const startHerePath = join(BASE_DIR, startHereData.folder_name);
  const subfolders = [];

  for (const subfolder of startHereData.subfolders) {
    const subfolderPath = join(startHerePath, subfolder.folder_name);
    const folderId = subfolder.folder_id;

    // Get Box file ID
    const fileId = await getBoxFileIdFromFolder(folderId);

    const pageData = buildPageData(subfolder, 'start_here', subfolderPath, folderId);

    // Extract order from folder name (e.g., "1-course-orientation" -> 1)
    const orderMatch = subfolder.folder_name.match(/^(\d+)-/);
    pageData.order = orderMatch ? parseInt(orderMatch[1], 10) : 0;

    // Extract slug from folder name
    const slugMatch = subfolder.folder_name.match(/^\d+-(.+)$/);
    if (slugMatch) {
      pageData.id = slugMatch[1];
      pageData.title = slugMatch[1].split('-').map(w =>
        w.charAt(0).toUpperCase() + w.slice(1)
      ).join(' ');
    }

    if (fileId) {
      pageData.box.file_id = fileId;
      pageData.box.file_url = `https://usu.app.box.com/file/${fileId}`;
      pageData.box.word_online_url = `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${fileId}&sharedAccessCode=`;
    }

    // Build Canvas URL
    if (pageData.id) {
      pageData.canvas.url = `https://usucourses.instructure.com/courses/2879/pages/${pageData.id}`;
      pageData.canvas.page_id = pageData.id;
    }

    subfolders.push(pageData);

    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  return {
    folder_name: startHereData.folder_name,
    folder_id: startHereData.folder_id,
    subfolders: subfolders
  };
}

/**
 * Build LA structure
 */
async function buildLAs(las, sectionPath, moduleNum, sectionNum) {
  const laPages = [];

  for (const la of las) {
    const laPath = join(sectionPath, la.folder_name);
    const folderId = la.folder_id;

    // Get Box file ID
    const fileId = await getBoxFileIdFromFolder(folderId);

    const pageData = buildPageData(la, 'la', laPath, folderId);
    pageData.order = la.la_number;

    if (fileId) {
      pageData.box.file_id = fileId;
      pageData.box.file_url = `https://usu.app.box.com/file/${fileId}`;
      pageData.box.word_online_url = `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${fileId}&sharedAccessCode=`;
    }

    // Build Canvas URL
    if (pageData.id) {
      pageData.canvas.url = `https://usucourses.instructure.com/courses/2879/pages/${pageData.id}`;
      pageData.canvas.page_id = pageData.id;
    }

    laPages.push(pageData);

    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  return laPages;
}

/**
 * Build section structure
 */
async function buildSections(sections, modulePath, moduleNum) {
  const sectionPages = [];

  for (const section of sections) {
    const sectionPath = join(modulePath, section.folder_name);
    const folderId = section.folder_id;

    // Get Box file ID
    const fileId = await getBoxFileIdFromFolder(folderId);

    const pageData = buildPageData(section, 'section', sectionPath, folderId);
    pageData.order = section.section_number;

    // Try to infer title from DOCX filename or use a default
    if (!pageData.title || pageData.title === '') {
      pageData.title = `Section ${section.section_number}`;
    }

    if (fileId) {
      pageData.box.file_id = fileId;
      pageData.box.file_url = `https://usu.app.box.com/file/${fileId}`;
      pageData.box.word_online_url = `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${fileId}&sharedAccessCode=`;
    }

    // Build Canvas URL
    if (pageData.id) {
      pageData.canvas.url = `https://usucourses.instructure.com/courses/2879/pages/${pageData.id}`;
      pageData.canvas.page_id = pageData.id;
    }

    // Build LAs
    pageData.las = await buildLAs(section.las, sectionPath, moduleNum, section.section_number);

    sectionPages.push(pageData);

    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  return sectionPages;
}

/**
 * Build module structure
 */
async function buildModules(modules) {
  const modulePages = [];

  for (const module of modules) {
    const modulePath = join(BASE_DIR, module.folder_name);
    const folderId = module.folder_id;

    console.log(`\n📂 Processing Module ${module.module_number}: ${module.folder_name}`);

    // Get Box file ID
    const fileId = await getBoxFileIdFromFolder(folderId);

    const pageData = buildPageData(module, 'module', modulePath, folderId);
    pageData.order = module.module_number;

    // Try to infer title from DOCX filename or use a default
    if (!pageData.title || pageData.title === '') {
      pageData.title = `Module ${module.module_number}`;
    }

    if (fileId) {
      pageData.box.file_id = fileId;
      pageData.box.file_url = `https://usu.app.box.com/file/${fileId}`;
      pageData.box.word_online_url = `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${fileId}&sharedAccessCode=`;
    }

    // Build Canvas URL
    if (pageData.id) {
      pageData.canvas.url = `https://usucourses.instructure.com/courses/2879/pages/${pageData.id}`;
      pageData.canvas.page_id = pageData.id;
    }

    // Build sections
    console.log(`  Building ${module.sections.length} sections...`);
    pageData.sections = await buildSections(module.sections, modulePath, module.module_number);

    modulePages.push(pageData);

    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 200));
  }

  return modulePages;
}

/**
 * Merge existing data if available
 */
function mergeExistingData(newStructure, existingMap) {
  // TODO: Implement merging logic to preserve existing Canvas URLs, GitHub paths, etc.
  // For now, return new structure as-is
  return newStructure;
}

/**
 * Main function
 */
async function main() {
  console.log('🏗️  Building course-map.json from scratch...\n');

  // Read Box folder structure
  console.log('📖 Reading box-folder-structure.json...');
  const boxStructure = JSON.parse(readFileSync(BOX_STRUCTURE_FILE, 'utf8'));

  // Read existing course map if available (for merging data)
  let existingMap = null;
  if (existsSync(EXISTING_COURSE_MAP_FILE)) {
    console.log('📖 Reading existing course-map.json (for reference)...');
    try {
      existingMap = JSON.parse(readFileSync(EXISTING_COURSE_MAP_FILE, 'utf8'));
    } catch (err) {
      console.log('  ⚠️  Could not read existing course map, proceeding without merge');
    }
  }

  // Build course map structure
  const courseMap = {
    schema_version: '1.0',
    course: {
      id: '2879',
      name: 'Document Accessibility',
      canvas_url: 'https://usucourses.instructure.com/courses/2879',
      semester: 'Winter 2025-26',
      instructor: ''
    },
    metadata: {
      created: new Date().toISOString(),
      last_updated: new Date().toISOString(),
      last_synced: null,
      version: '1.0.0'
    },
    repositories: {
      main: {
        url: 'https://github.com/gjoeckel/canvas_2879',
        branch: 'main',
        path: REPO_BASE_PATH
      }
    },
    box: {
      folder_id: boxStructure.base_folder_id,
      folder_url: `https://usu.app.box.com/folder/${boxStructure.base_folder_id}`,
      base_path: '/WINTER-25-26-UPDATES'
    },
    start_here: null,
    modules: []
  };

  // Build Start Here
  if (boxStructure.start_here) {
    console.log('\n📂 Building Start Here structure...');
    courseMap.start_here = await buildStartHere(boxStructure.start_here);
  }

  // Build Modules
  console.log('\n📂 Building Modules structure...');
  courseMap.modules = await buildModules(boxStructure.modules);

  // Merge with existing data if available
  if (existingMap) {
    console.log('\n🔄 Merging with existing data...');
    // For now, skip merge - we'll use the new structure
    // TODO: Implement proper merge to preserve existing Canvas URLs, etc.
  }

  // Write output
  console.log('\n💾 Writing course-map.json...');
  writeFileSync(OUTPUT_FILE, JSON.stringify(courseMap, null, 2), 'utf8');

  // Print summary
  console.log('\n✅ Build complete!\n');
  console.log('📊 Summary:');
  if (courseMap.start_here) {
    console.log(`  Start Here: ${courseMap.start_here.subfolders.length} pages`);
  }
  console.log(`  Modules: ${courseMap.modules.length}`);
  const totalSections = courseMap.modules.reduce((sum, m) => sum + (m.sections?.length || 0), 0);
  const totalLAs = courseMap.modules.reduce((sum, m) =>
    sum + (m.sections?.reduce((s, sec) => s + (sec.las?.length || 0), 0) || 0), 0);
  console.log(`  Sections: ${totalSections}`);
  console.log(`  LAs: ${totalLAs}`);
  console.log(`  Total pages: ${(courseMap.start_here?.subfolders.length || 0) + courseMap.modules.length + totalSections + totalLAs}`);
  console.log(`\n📄 Saved to: ${OUTPUT_FILE}`);
}

main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});
