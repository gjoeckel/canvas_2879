#!/usr/bin/env node
/**
 * Convert HTML files to DOCX for Modules and Sections
 *
 * This script:
 * 1. Finds all Module and Section HTML files
 * 2. Extracts content from HTML (removes Canvas-specific CSS/JS)
 * 3. Converts to DOCX format
 * 4. Saves DOCX files in the same directory as HTML files
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { dirname, join, basename, extname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Check if html-to-docx is installed
let HTMLtoDOCX;
try {
  HTMLtoDOCX = (await import('html-to-docx')).default;
} catch (e) {
  console.error('❌ html-to-docx package not found. Installing...');
  try {
    execSync('npm install html-to-docx', { cwd: __dirname, stdio: 'inherit' });
    HTMLtoDOCX = (await import('html-to-docx')).default;
  } catch (installError) {
    console.error('❌ Failed to install html-to-docx:', installError.message);
    process.exit(1);
  }
}

/**
 * Extract clean HTML content from Canvas HTML
 * Removes Canvas-specific CSS, JS, and wrapper elements
 */
function extractContent(htmlContent) {
  // Parse HTML to extract just the user_content div
  const userContentMatch = htmlContent.match(/<div class="user_content">([\s\S]*?)<\/div>\s*<!-- end user_content -->/);

  if (userContentMatch) {
    let content = userContentMatch[1];

    // Remove script tags
    content = content.replace(/<script[\s\S]*?<\/script>/gi, '');

    // Remove Canvas-specific data attributes
    content = content.replace(/\s+data-[^=]*="[^"]*"/g, '');

    // Remove Canvas API endpoint attributes
    content = content.replace(/\s+data-api-[^=]*="[^"]*"/g, '');

    // Clean up empty divs and spans
    content = content.replace(/<div>\s*<\/div>/g, '');
    content = content.replace(/<span>\s*<\/span>/g, '');

    // Wrap in basic HTML structure for DOCX conversion
    return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Document</title>
</head>
<body>
${content}
</body>
</html>`;
  }

  // Fallback: try to extract body content
  const bodyMatch = htmlContent.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  if (bodyMatch) {
    let content = bodyMatch[1];
    // Remove script tags
    content = content.replace(/<script[\s\S]*?<\/script>/gi, '');
    // Remove style tags
    content = content.replace(/<style[\s\S]*?<\/style>/gi, '');
    // Remove Canvas-specific elements
    content = content.replace(/<div class="original-link">[\s\S]*?<\/div>/gi, '');

    return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Document</title>
</head>
<body>
${content}
</body>
</html>`;
  }

  // Last resort: return cleaned original
  let cleaned = htmlContent
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<link[^>]*>/gi, '');

  return cleaned;
}

/**
 * Convert HTML file to DOCX
 */
async function convertHtmlToDocx(htmlPath) {
  const htmlDir = dirname(htmlPath);
  const htmlName = basename(htmlPath, extname(htmlPath));
  const docxPath = join(htmlDir, `${htmlName}.docx`);

  // Skip if DOCX already exists
  if (existsSync(docxPath)) {
    console.log(`  ⏭️  DOCX already exists: ${basename(docxPath)}`);
    return { skipped: true, path: docxPath };
  }

  try {
    // Read HTML file
    const htmlContent = readFileSync(htmlPath, 'utf-8');

    // Extract clean content
    const cleanHtml = extractContent(htmlContent);

    // Convert to DOCX
    console.log(`  🔄 Converting to DOCX...`);
    const docxBuffer = await HTMLtoDOCX(cleanHtml);

    // Write DOCX file
    writeFileSync(docxPath, docxBuffer);

    const fileSize = (docxBuffer.length / 1024).toFixed(2);
    console.log(`  ✅ Created: ${basename(docxPath)} (${fileSize} KB)`);

    return { success: true, path: docxPath, size: docxBuffer.length };
  } catch (error) {
    console.error(`  ❌ Error converting ${basename(htmlPath)}: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Find all Module and Section HTML files
 */
function findHtmlFiles(rootDir) {
  const htmlFiles = [];

  // Find Module HTML files (in Module-* directories, directly in Module-* folders)
  const moduleFiles = execSync(
    `find "${rootDir}" -type d -name "Module-*" -exec find {} -maxdepth 1 -name "Module*.html" -type f ! -name "*_local.html" \\;`,
    { encoding: 'utf-8' }
  ).trim().split('\n').filter(Boolean);

  htmlFiles.push(...moduleFiles);

  // Find Section HTML files (in Section-* directories)
  const sectionFiles = execSync(
    `find "${rootDir}" -path "*/Section-*/*.html" -name "Section*.html" -type f ! -name "*_local.html"`,
    { encoding: 'utf-8' }
  ).trim().split('\n').filter(Boolean);

  htmlFiles.push(...sectionFiles);

  return htmlFiles.sort();
}

/**
 * Main conversion function
 */
async function convertAllHtmlFiles(rootDir) {
  console.log('📄 Converting HTML files to DOCX...\n');
  console.log(`📁 Root directory: ${rootDir}\n`);

  // Find all HTML files
  const htmlFiles = findHtmlFiles(rootDir);

  if (htmlFiles.length === 0) {
    console.log('⚠️  No HTML files found');
    return;
  }

  console.log(`Found ${htmlFiles.length} HTML files:\n`);

  const results = {
    success: 0,
    skipped: 0,
    errors: 0,
    files: []
  };

  for (const htmlPath of htmlFiles) {
    const relativePath = htmlPath.replace(rootDir + '/', '');
    console.log(`📄 ${relativePath}`);

    const result = await convertHtmlToDocx(htmlPath);

    results.files.push({
      path: relativePath,
      ...result
    });

    if (result.skipped) {
      results.skipped++;
    } else if (result.success) {
      results.success++;
    } else {
      results.errors++;
    }

    console.log(''); // Empty line for readability
  }

  // Summary
  console.log('📊 Conversion Summary:');
  console.log(`  ✅ Success: ${results.success}`);
  console.log(`  ⏭️  Skipped: ${results.skipped}`);
  console.log(`  ❌ Errors: ${results.errors}`);
  console.log(`  📄 Total: ${htmlFiles.length}`);

  return results;
}

// Main execution
const rootDir = process.argv[2] || __dirname;

if (!existsSync(rootDir)) {
  console.error(`❌ Directory not found: ${rootDir}`);
  process.exit(1);
}

convertAllHtmlFiles(rootDir)
  .then(() => {
    console.log('\n✅ Conversion complete!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Fatal error:', error);
    process.exit(1);
  });
