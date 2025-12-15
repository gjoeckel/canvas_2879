#!/usr/bin/env node
/**
 * Update Canvas Course DOCX Editor HTML file with new link structure
 *
 * New format: view docx | edit docx [10px whitespace] view canvas | edit canvas
 *
 * This script updates existing links in place, preserving the HTML structure.
 */

import { readFileSync, writeFileSync } from 'fs';

// Configuration
const COURSE_MAP_PATH = '/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/course-map.json';
const HTML_FILE_PATH = '/Users/a00288946/Projects/canvas_2879/github-pages/index.html';
const GITHUB_PAGES_BASE = 'https://gjoeckel.github.io/canvas_2879';

// Read course map
const courseMap = JSON.parse(readFileSync(COURSE_MAP_PATH, 'utf-8'));

// Create a map of Box file IDs to page data for quick lookup
const boxFileIdMap = new Map();
for (const page of courseMap.pages) {
  if (page.box?.file_id) {
    boxFileIdMap.set(page.box.file_id, page);
  }
}

// Also create a map by Canvas URL for fallback lookup
const canvasUrlMap = new Map();
for (const page of courseMap.pages) {
  if (page.canvas?.url) {
    canvasUrlMap.set(page.canvas.url, page);
  }
}

// Function to generate GitHub Pages URL from course map path
function getGitHubPagesUrl(githubPath) {
  if (!githubPath) return null;
  // Remove 'pages/' prefix if present, as GitHub Pages serves from repo root
  const cleanPath = githubPath.replace(/^pages\//, '');
  return `${GITHUB_PAGES_BASE}/${cleanPath}`;
}

// Read HTML file
let htmlContent = readFileSync(HTML_FILE_PATH, 'utf-8');

// Update instructions
const newInstructions = `<p>Each page in the Canvas course has been converted into a DOCX file and uploaded to Box. Each page listed below has four links:</p>
    <ul>
        <li><strong>view docx:</strong> opens the docx file in the Box viewer.</li>
        <li><strong>edit docx:</strong> opens the docx file in the Box Microsoft Word Online editor.</li>
        <li><strong>view canvas:</strong> opens an HTML file with page content.</li>
        <li><strong>edit canvas:</strong> opens the Canvas page for editing.</li>
    </ul>`;

// Replace old instructions
htmlContent = htmlContent.replace(
  /<p>Each page in the Canvas course has been converted into a docx file\. All docx files are uploaded to Box\. Each page has three links:.*?<\/ol>/s,
  newInstructions
);

// Function to update a single link block
function updateLinkBlock(linkBlock) {
  // Extract Box file ID from view docx link
  const boxFileIdMatch = linkBlock.match(/\/file\/(\d+)/);
  if (!boxFileIdMatch) {
    return linkBlock; // Return unchanged if no Box file ID found
  }

  const boxFileId = boxFileIdMatch[1];
  const page = boxFileIdMap.get(boxFileId);

  // Extract existing URLs as fallback
  const viewDocxMatch = linkBlock.match(/<a[^>]*href="([^"]*\/file\/\d+[^"]*)"[^>]*>view docx<\/a>/);
  const editDocxMatch = linkBlock.match(/<a[^>]*href="([^"]*fileId=\d+[^"]*)"[^>]*>edit docx<\/a>/);
  const viewCanvasMatch = linkBlock.match(/<a[^>]*href="([^"]*github\.io[^"]*)"[^>]*>view canvas<\/a>/);

  // Check for Canvas URL in "view canvas" link (some old links have Canvas URL as "view canvas")
  const canvasUrlInViewCanvas = linkBlock.match(/<a[^>]*href="(https:\/\/usucourses\.instructure\.com\/courses\/2879\/pages\/[^"]*)"[^>]*>view canvas<\/a>/);

  // Check for separate edit canvas link
  const editCanvasMatch = linkBlock.match(/<a[^>]*href="(https:\/\/usucourses\.instructure\.com\/courses\/2879\/pages\/[^"]*)"[^>]*>edit canvas<\/a>/);

  // Try to find page by Canvas URL if not found by Box file ID
  let foundPage = page;
  if (!foundPage && (canvasUrlInViewCanvas || editCanvasMatch)) {
    const canvasUrl = editCanvasMatch?.[1] || canvasUrlInViewCanvas?.[1];
    if (canvasUrl) {
      foundPage = canvasUrlMap.get(canvasUrl);
    }
  }

  // Get URLs - prefer course map, fallback to extracted URLs
  const viewDocxUrl = foundPage?.box?.file_url || viewDocxMatch?.[1] || `https://usu.app.box.com/file/${boxFileId}`;
  const editDocxUrl = foundPage?.box?.word_online_url || editDocxMatch?.[1] || `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${boxFileId}`;
  const viewCanvasUrl = foundPage?.github?.with_assets?.path
    ? getGitHubPagesUrl(foundPage.github.with_assets.path)
    : (viewCanvasMatch?.[1] || null);

  // For edit canvas, use Canvas URL from course map, or from existing link, or from "view canvas" if it's actually a Canvas URL
  let editCanvasUrl = foundPage?.canvas?.url || editCanvasMatch?.[1];
  if (!editCanvasUrl && canvasUrlInViewCanvas) {
    // The "view canvas" link is actually pointing to Canvas - use it for edit canvas
    editCanvasUrl = canvasUrlInViewCanvas[1];
  }
  if (!editCanvasUrl) {
    editCanvasUrl = '#';
  }

  // Build new links with 10px whitespace
  let newLinks = `<a href="${viewDocxUrl}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="${editDocxUrl}" target="_blank" rel="noopener noreferrer">edit docx</a>`;
  newLinks += ' <span style="margin-left: 10px;"></span> ';

  if (viewCanvasUrl) {
    newLinks += `<a href="${viewCanvasUrl}" target="_blank" rel="noopener noreferrer">view canvas</a>`;
  } else {
    newLinks += `<span style="color: #999;">view canvas</span>`;
  }

  newLinks += ' | ';
  newLinks += `<a href="${editCanvasUrl}" target="_blank" rel="noopener noreferrer">edit canvas</a>`;

  // Replace the link block, preserving surrounding structure
  return linkBlock.replace(/<span class="page-links">.*?<\/span>/, `<span class="page-links">${newLinks}</span>`);
}

// Pattern to match any link block with view docx - use non-greedy and more specific
// Match the entire page-links span, but be careful not to match across multiple spans
const linkBlockPattern = /<span class="page-links">([^<]*(?:<[^>]+>[^<]*<\/[^>]+>[^<]*)*?)<\/span>/g;

htmlContent = htmlContent.replace(linkBlockPattern, (match, linkContent) => {
  // Only update if it contains "view docx" and doesn't already have the new format
  if (match.includes('view docx') && !match.includes('margin-left: 10px')) {
    return updateLinkBlock(match);
  }
  return match;
});

// Remove duplicate content - find where script ends and remove everything after it until </body>
const scriptEndMatch = htmlContent.match(/(<\/script>)/);
if (scriptEndMatch) {
  const scriptEndIndex = scriptEndMatch.index + scriptEndMatch[0].length;
  const bodyEndIndex = htmlContent.lastIndexOf('</body>');

  if (bodyEndIndex > scriptEndIndex) {
    // Check if there's duplicate content between script end and body end
    const afterScript = htmlContent.substring(scriptEndIndex, bodyEndIndex).trim();
    if (afterScript.includes('<h2>') || afterScript.includes('<h3>')) {
      // Remove duplicate content, keep only the script and closing tags
      htmlContent = htmlContent.substring(0, scriptEndIndex) + '\n</body>\n</html>';
    }
  }
}

// Clean up any duplicate links within the same span (shouldn't happen, but just in case)
htmlContent = htmlContent.replace(/<span class="page-links">(.*?)<\/span>\s*<a[^>]*>view canvas<\/a>\s*\|\s*<a[^>]*>edit canvas<\/a><\/span>/g,
  '<span class="page-links">$1</span>');

// Write updated HTML
writeFileSync(HTML_FILE_PATH, htmlContent, 'utf-8');

console.log('✅ Updated Canvas Course DOCX Editor HTML file');
console.log(`   File: ${HTML_FILE_PATH}`);
console.log(`   Pages in course map: ${courseMap.pages.length}`);
