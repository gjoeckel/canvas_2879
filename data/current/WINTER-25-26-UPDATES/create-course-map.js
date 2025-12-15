#!/usr/bin/env node
/**
 * Create course map from Box uploads, Canvas page links, and GitHub information
 *
 * This script:
 * 1. Reads Box upload summary to get Box file IDs
 * 2. Reads Canvas page links to get Canvas URLs
 * 3. Generates course map with all information
 * 4. Saves course map locally and optionally to Box
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { dirname, join, basename } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Import Box client for uploading course map with automatic token refresh
import { executeWithRefresh } from '/Users/a00288946/Agents/cursor-ops/mcp-box-minimal/dist/box-client.js';

/**
 * Parse Box upload summary to extract file IDs
 */
function parseBoxUploadSummary(summaryPath) {
  const summary = readFileSync(summaryPath, 'utf-8');
  const files = [];

  // Extract file information from summary
  // Format: "1. ✅ `Module-1/Module 1_ Document Content.docx` (32.17 KB)"
  //         "   - Box File ID: `2072501663155`"
  //         "   - Box Folder: `355472828832` (Module-1)"

  const lines = summary.split('\n');
  let currentFile = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Module or Section file (format: "1. ✅ `Module-1/Module 1_ Document Content.docx`")
    const fileMatch = line.match(/^\d+\.\s+✅\s+`([^`]+)`/);
    if (fileMatch) {
      // Save previous file if exists
      if (currentFile && currentFile.box_file_id) {
        files.push({ ...currentFile });
      }

      currentFile = {
        path: fileMatch[1],
        name: basename(fileMatch[1])
      };
      continue;
    }

    // Also check for format without leading number (in Section lists)
    const fileMatch2 = line.match(/^(\d+)\.\s+✅\s+`([^`]+)`/);
    if (fileMatch2 && !currentFile) {
      currentFile = {
        path: fileMatch2[2],
        name: basename(fileMatch2[2])
      };
      continue;
    }

    // Box File ID (format: "   - Box File ID: `2072501663155`")
    if (currentFile && line.includes('Box File ID:')) {
      const idMatch = line.match(/Box File ID: `(\d+)`/);
      if (idMatch) {
        currentFile.box_file_id = idMatch[1];
      }
      continue;
    }

    // Box Folder ID (format: "   - Box Folder: `355472828832` (Module-1)")
    if (currentFile && line.includes('Box Folder:')) {
      const folderMatch = line.match(/Box Folder: `(\d+)`/);
      if (folderMatch) {
        currentFile.box_folder_id = folderMatch[1];
      }
      // Save file when we find folder ID (or if we have file ID and hit next section)
      if (currentFile.box_file_id) {
        files.push({ ...currentFile });
        currentFile = null;
      }
      continue;
    }

    // If we hit a new section header, save current file if it has a file ID
    if (currentFile && currentFile.box_file_id &&
        (line.match(/^\*\*Module \d+\*\*/) || line.match(/^### /) || line.match(/^## /))) {
      files.push({ ...currentFile });
      currentFile = null;
    }
  }

  // Save any remaining file at end
  if (currentFile && currentFile.box_file_id) {
    files.push({ ...currentFile });
  }

  return files;
}

/**
 * Load Canvas page links
 */
function loadCanvasPageLinks(linksPath) {
  const links = JSON.parse(readFileSync(linksPath, 'utf-8'));
  const linkMap = new Map();

  for (const [key, value] of Object.entries(links)) {
    if (value.canvas_url) {
      // Extract page slug from Canvas URL
      const urlMatch = value.canvas_url.match(/\/pages\/([^\/]+)/);
      const slug = urlMatch ? urlMatch[1] : null;

      linkMap.set(key, {
        title: value.title,
        canvas_url: value.canvas_url,
        slug: slug
      });
    }
  }

  return linkMap;
}

/**
 * Match file name to Canvas page link
 */
function findCanvasLink(fileName, canvasLinks) {
  // Try exact match first
  for (const [key, value] of canvasLinks.entries()) {
    if (key.includes(fileName.replace('.docx', '')) ||
        key.includes(fileName.replace('.docx', '.html'))) {
      return value;
    }
  }

  // Try partial match
  const fileNameBase = fileName
    .replace(/\.docx$/i, '')
    .replace(/^Module\s+(\d+)\s*:\s*/i, 'Module $1: ')
    .replace(/^Section\s+(\d+)\s*:\s*/i, 'Section $1: ');

  for (const [key, value] of canvasLinks.entries()) {
    if (key.toLowerCase().includes(fileNameBase.toLowerCase()) ||
        value.title.toLowerCase().includes(fileNameBase.toLowerCase())) {
      return value;
    }
  }

  return null;
}

/**
 * Generate page slug from file name
 */
function fileNameToSlug(fileName) {
  return fileName
    .replace(/\.docx?$/i, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Generate page ID from file name
 */
function fileNameToId(fileName) {
  return fileNameToSlug(fileName);
}

/**
 * Generate page title from file name
 */
function fileNameToTitle(fileName) {
  return fileName
    .replace(/\.docx?$/i, '')
    .trim();
}

/**
 * Generate GitHub paths
 */
function generateGitHubPaths(slug, fileName) {
  return {
    source_docx: {
      path: `pages/${slug}/${slug}.docx`,
      branch: 'main'
    },
    canvas_copy: {
      path: `pages/${slug}/canvas-copy.html`,
      branch: 'main'
    },
    with_assets: {
      path: `pages/${slug}/index.html`,
      branch: 'main'
    }
  };
}

/**
 * Create course map
 */
function createCourseMap(boxFiles, canvasLinks, config) {
  const now = new Date().toISOString();

  const courseMap = {
    schema_version: '1.0',
    course: {
      id: config.courseId || '2879',
      name: config.courseName || 'Document Accessibility',
      canvas_url: config.canvasUrl || 'https://usucourses.instructure.com/courses/2879',
      semester: config.semester || 'Winter 2025-26',
      instructor: config.instructor || ''
    },
    metadata: {
      created: now,
      last_updated: now,
      last_synced: null,
      version: '1.0.0'
    },
    repositories: config.repositories || {
      main: {
        url: config.githubRepo || 'https://github.com/username/canvas_2879',
        branch: 'main',
        path: 'data/current/WINTER-25-26-UPDATES'
      }
    },
    box: {
      folder_id: config.boxRootFolderId || '355471834847',
      folder_url: `https://usu.app.box.com/folder/${config.boxRootFolderId || '355471834847'}`,
      base_path: '/WINTER-25-26-UPDATES'
    },
    pages: []
  };

  // Process each Box file
  let order = 1;
  for (const file of boxFiles) {
    const slug = fileNameToSlug(file.name);
    const pageId = fileNameToId(file.name);
    const title = fileNameToTitle(file.name);

    // Find matching Canvas link
    const canvasLink = findCanvasLink(file.name, canvasLinks);

    // Determine page type (module or section)
    const isModule = file.name.match(/^Module\s+\d+/i);
    const isSection = file.name.match(/^Section\s+\d+/i);

    const page = {
      id: pageId,
      slug: slug,
      title: title,
      order: order++,
      status: 'draft',
      canvas: canvasLink ? {
        url: canvasLink.canvas_url,
        page_id: canvasLink.slug || null,
        published: false,
        published_at: null
      } : {},
      github: {
        repository: 'main',
        ...generateGitHubPaths(slug, file.name)
      },
      box: {
        file_id: file.box_file_id,
        file_name: file.name,
        file_url: `https://usu.app.box.com/file/${file.box_file_id}`,
        word_online_url: `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${file.box_file_id}`,
        folder_id: file.box_folder_id,
        modified_at: null,
        version: 1
      },
      sync: {
        last_synced: null,
        sync_status: 'pending',
        sync_errors: []
      },
      metadata: {
        type: isModule ? 'module' : isSection ? 'section' : 'page',
        created: now
      }
    };

    courseMap.pages.push(page);
  }

  return courseMap;
}

/**
 * Upload course map to Box with automatic token refresh
 */
async function uploadCourseMapToBox(courseMap, boxFolderId) {
  try {
    const courseMapJson = JSON.stringify(courseMap, null, 2);
    const courseMapBuffer = Buffer.from(courseMapJson, 'utf-8');

    console.log(`📤 Uploading course map to Box folder: ${boxFolderId}...`);

    const { Readable } = await import('stream');

    // Use executeWithRefresh to handle token expiration automatically
    const uploadedFile = await executeWithRefresh(async (boxClient) => {
      return await boxClient.uploads.uploadFile({
        attributes: {
          name: 'course-map.json',
          parent: {
            id: boxFolderId
          }
        },
        file: Readable.from(courseMapBuffer)
      });
    });

    const result = uploadedFile.entries[0];
    console.log(`  ✅ Uploaded: course-map.json (${result.id})`);

    return {
      file_id: result.id,
      file_name: result.name,
      box_url: `https://usu.app.box.com/file/${result.id}`
    };
  } catch (error) {
    console.error(`  ❌ Error uploading course map: ${error.message}`);
    throw error;
  }
}

/**
 * Main function
 */
async function main() {
  const rootDir = process.argv[2] || __dirname;
  const configPath = process.argv[3] || join(__dirname, '../../config');

  console.log('🗺️  Creating course map...\n');

  // Load Box upload summary
  const boxSummaryPath = join(rootDir, 'BOX-UPLOAD-SUMMARY.md');
  if (!existsSync(boxSummaryPath)) {
    console.error(`❌ Box upload summary not found: ${boxSummaryPath}`);
    process.exit(1);
  }

  console.log('📦 Loading Box file information...');
  const boxFiles = parseBoxUploadSummary(boxSummaryPath);
  console.log(`  ✓ Found ${boxFiles.length} Box files\n`);

  // Load Canvas page links
  let canvasLinksPath = join(configPath, 'canvas-page-links.json');
  if (!existsSync(canvasLinksPath)) {
    // Try absolute path
    canvasLinksPath = '/Users/a00288946/Projects/canvas_2879/config/canvas-page-links.json';
    if (!existsSync(canvasLinksPath)) {
      console.error(`❌ Canvas page links not found: ${canvasLinksPath}`);
      process.exit(1);
    }
  }

  console.log('🎓 Loading Canvas page links...');
  const canvasLinks = loadCanvasPageLinks(canvasLinksPath);
  console.log(`  ✓ Found ${canvasLinks.size} Canvas page links\n`);

  // Configuration
  const config = {
    courseId: '2879',
    courseName: 'Document Accessibility',
    canvasUrl: 'https://usucourses.instructure.com/courses/2879',
    semester: 'Winter 2025-26',
    boxRootFolderId: '355471834847',
    githubRepo: 'https://github.com/gjoeckel/canvas_2879'
  };

  // Create course map
  console.log('📝 Generating course map...');
  const courseMap = createCourseMap(boxFiles, canvasLinks, config);
  console.log(`  ✓ Created course map with ${courseMap.pages.length} pages\n`);

  // Save locally
  const localPath = join(rootDir, 'course-map.json');
  writeFileSync(localPath, JSON.stringify(courseMap, null, 2));
  console.log(`💾 Saved course map: ${localPath}\n`);

  // Upload to Box
  console.log('📤 Uploading course map to Box...');
  try {
    const uploadResult = await uploadCourseMapToBox(courseMap, config.boxRootFolderId);
    console.log(`  ✅ Course map uploaded to Box: ${uploadResult.box_url}\n`);
  } catch (error) {
    console.error(`  ⚠️  Failed to upload to Box: ${error.message}`);
    console.error(`  💡 Course map saved locally at: ${localPath}\n`);
  }

  // Summary
  console.log('📊 Course Map Summary:');
  console.log(`  Course: ${courseMap.course.name} (${courseMap.course.id})`);
  console.log(`  Pages: ${courseMap.pages.length}`);
  console.log(`  Modules: ${courseMap.pages.filter(p => p.metadata.type === 'module').length}`);
  console.log(`  Sections: ${courseMap.pages.filter(p => p.metadata.type === 'section').length}`);
  console.log(`  With Canvas URLs: ${courseMap.pages.filter(p => p.canvas?.url).length}`);
  console.log(`  With Box File IDs: ${courseMap.pages.filter(p => p.box?.file_id).length}`);

  console.log('\n✅ Course map creation complete!');
}

main().catch((error) => {
  console.error('\n❌ Fatal error:', error);
  process.exit(1);
});
