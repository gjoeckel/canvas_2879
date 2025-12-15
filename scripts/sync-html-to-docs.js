#!/usr/bin/env node
/**
 * Sync local HTML files to docs/ folder for GitHub Pages deployment
 *
 * Copies all *_local.html files from data/current/WINTER-25-26-UPDATES/
 * to docs/data/current/WINTER-25-26-UPDATES/ maintaining directory structure
 */

import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync, existsSync } from 'fs';
import { join, dirname, relative } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const REPO_ROOT = join(__dirname, '..');
const SOURCE_DIR = join(REPO_ROOT, 'data/current/WINTER-25-26-UPDATES');
const DEST_DIR = join(REPO_ROOT, 'docs/data/current/WINTER-25-26-UPDATES');

/**
 * Recursively copy HTML files maintaining directory structure
 */
function syncHtmlFiles(sourcePath, destPath) {
  let copiedCount = 0;
  let createdDirs = 0;

  function processDirectory(src, dest) {
    // Create destination directory if it doesn't exist
    if (!existsSync(dest)) {
      mkdirSync(dest, { recursive: true });
      createdDirs++;
      console.log(`  📁 Created: ${relative(SOURCE_DIR, dest)}`);
    }

    // Read source directory
    const entries = readdirSync(src);

    for (const entry of entries) {
      const srcPath = join(src, entry);
      const destPath = join(dest, entry);
      const stat = statSync(srcPath);

      if (stat.isDirectory()) {
        // Recursively process subdirectories
        processDirectory(srcPath, destPath);
      } else if (stat.isFile() && entry.endsWith('_local.html')) {
        // Copy HTML file
        const content = readFileSync(srcPath, 'utf8');
        writeFileSync(destPath, content, 'utf8');
        copiedCount++;
        console.log(`  📄 Copied: ${relative(SOURCE_DIR, srcPath)}`);
      }
      // Skip other file types
    }
  }

  processDirectory(sourcePath, destPath);

  return { copiedCount, createdDirs };
}

/**
 * Main function
 */
async function main() {
  console.log('🔄 Syncing HTML files to docs/ folder for GitHub Pages...\n');
  console.log(`Source: ${SOURCE_DIR}`);
  console.log(`Destination: ${DEST_DIR}\n`);

  if (!existsSync(SOURCE_DIR)) {
    console.error(`❌ Error: Source directory does not exist: ${SOURCE_DIR}`);
    process.exit(1);
  }

  try {
    const { copiedCount, createdDirs } = syncHtmlFiles(SOURCE_DIR, DEST_DIR);

    console.log(`\n✅ Sync complete!`);
    console.log(`   📁 Directories created: ${createdDirs}`);
    console.log(`   📄 Files copied: ${copiedCount}`);
    console.log(`\n💡 Next steps:`);
    console.log(`   1. Review changes: git status`);
    console.log(`   2. Commit: git add docs/data/`);
    console.log(`   3. Push: git push origin main`);
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();

