#!/usr/bin/env node

/**
 * Update CSS and image paths in HTML files to use GitHub Pages absolute URLs
 *
 * Converts:
 * - Relative CSS paths: ../../../../../../assets/css/... → https://gjoeckel.github.io/canvas_2879/assets/css/...
 * - Relative image paths: src="1235647.png" → src="https://gjoeckel.github.io/canvas_2879/data/current/WINTER-25-26-UPDATES/.../1235647.png"
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const GITHUB_BASE_URL = 'https://gjoeckel.github.io/canvas_2879';
const DATA_ROOT = path.join(__dirname);

// Find all HTML files
function findHtmlFiles(dir) {
  const files = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...findHtmlFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      files.push(fullPath);
    }
  }

  return files;
}

// Calculate the relative path from HTML file to the repo root
function getRelativePathToRepo(htmlFilePath) {
  // htmlFilePath is like: /path/to/repo/data/current/WINTER-25-26-UPDATES/Module-1/.../file.html
  // We need to find where 'data' is relative to repo root
  const parts = htmlFilePath.split(path.sep);
  const dataIndex = parts.indexOf('data');

  if (dataIndex === -1) {
    throw new Error(`Could not find 'data' directory in path: ${htmlFilePath}`);
  }

  // Count levels from HTML file to 'data' directory
  // e.g., data/current/WINTER-25-26-UPDATES/Module-1/Section-1-2/LA-1-2-1/file.html
  // data = 0, current = 1, WINTER-25-26-UPDATES = 2, Module-1 = 3, Section-1-2 = 4, LA-1-2-1 = 5, file.html = 6
  // So we need to go up (6 - 0) = 6 levels to get to 'data', then up 1 more to get to repo root

  const dataPath = parts.slice(0, dataIndex + 1).join(path.sep);
  const relativeParts = path.relative(dataPath, path.dirname(htmlFilePath)).split(path.sep);
  const levelsUp = relativeParts.filter(p => p !== '.' && p !== '').length + 1; // +1 to get past 'data' to repo root

  return {
    levelsUp,
    pathFromData: path.relative(dataPath, path.dirname(htmlFilePath)),
    fileName: path.basename(htmlFilePath),
    fullPathFromRepo: path.relative(parts.slice(0, dataIndex).join(path.sep), htmlFilePath)
  };
}

// Update CSS paths in HTML content
function updateCssPaths(htmlContent, relativeInfo) {
  // Match: href="../../../../../../assets/css/..."
  // Replace with: href="https://gjoeckel.github.io/canvas_2879/assets/css/..."
  const cssPattern = /href=["']([^"']*\/assets\/css\/[^"']+)["']/g;

  return htmlContent.replace(cssPattern, (match, cssPath) => {
    // If it's already an absolute URL, skip it
    if (cssPath.startsWith('http://') || cssPath.startsWith('https://')) {
      return match;
    }

    // Extract just the assets/css/... part
    const assetsMatch = cssPath.match(/assets\/css\/.+/);
    if (assetsMatch) {
      const githubPath = `${GITHUB_BASE_URL}/${assetsMatch[0]}`;
      return match.replace(cssPath, githubPath);
    }

    return match;
  });
}

// Update image paths in HTML content
function updateImagePaths(htmlContent, htmlFilePath, relativeInfo) {
  // Match: src="1235647.png" or src="./1235647.png" or src="../image.png"
  // Images are in the same directory as the HTML file
  const imgPattern = /src=["']([^"']+\.(png|jpg|jpeg|gif|svg|webp))["']/gi;

  return htmlContent.replace(imgPattern, (match, imgPath) => {
    // If it's already an absolute URL, skip it
    if (imgPath.startsWith('http://') || imgPath.startsWith('https://')) {
      return match;
    }

    // If it's a relative path, resolve it relative to the HTML file's directory
    const htmlDir = path.dirname(htmlFilePath);
    const resolvedPath = path.resolve(htmlDir, imgPath);

    // Convert to path relative to repo root
    // Find where 'data' is in the resolved path
    const parts = resolvedPath.split(path.sep);
    const dataIndex = parts.indexOf('data');

    if (dataIndex !== -1) {
      // Path from repo root: data/current/WINTER-25-26-UPDATES/...
      const repoRelativePath = parts.slice(dataIndex).join('/');
      const githubPath = `${GITHUB_BASE_URL}/${repoRelativePath}`;
      return match.replace(imgPath, githubPath);
    }

    // Fallback: try to construct from relativeInfo
    const imgFileName = path.basename(imgPath);
    const htmlDirFromData = relativeInfo.pathFromData.replace(/\\/g, '/');
    const githubPath = `${GITHUB_BASE_URL}/data/current/WINTER-25-26-UPDATES/${htmlDirFromData}/${imgFileName}`;

    return match.replace(imgPath, githubPath);
  });
}

// Process a single HTML file
function processHtmlFile(htmlFilePath) {
  console.log(`Processing: ${htmlFilePath}`);

  const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
  const relativeInfo = getRelativePathToRepo(htmlFilePath);

  let updatedContent = htmlContent;
  updatedContent = updateCssPaths(updatedContent, relativeInfo);
  updatedContent = updateImagePaths(updatedContent, htmlFilePath, relativeInfo);

  if (updatedContent !== htmlContent) {
    fs.writeFileSync(htmlFilePath, updatedContent, 'utf8');
    console.log(`  ✓ Updated paths`);
    return true;
  } else {
    console.log(`  - No changes needed`);
    return false;
  }
}

// Main execution
function main() {
  console.log('🔄 Updating CSS and image paths for GitHub Pages...\n');

  const htmlFiles = findHtmlFiles(DATA_ROOT);
  console.log(`Found ${htmlFiles.length} HTML files\n`);

  let updatedCount = 0;
  for (const htmlFile of htmlFiles) {
    if (processHtmlFile(htmlFile)) {
      updatedCount++;
    }
  }

  console.log(`\n✅ Updated ${updatedCount} of ${htmlFiles.length} HTML files`);
  console.log('\n📝 Next steps:');
  console.log('   1. Review the changes');
  console.log('   2. Run: node scripts/sync-html-to-docs.js');
  console.log('   3. Commit and push to GitHub');
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { processHtmlFile, updateCssPaths, updateImagePaths };

