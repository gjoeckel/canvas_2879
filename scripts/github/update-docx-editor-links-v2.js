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

// Create a map of page slugs to page data for quick lookup
const pageMap = new Map();
for (const page of courseMap.pages) {
  pageMap.set(page.slug, page);
  // Also map by title (normalized)
  const normalizedTitle = page.title.replace(/_/g, ' ').toLowerCase();
  pageMap.set(normalizedTitle, page);
}

// Function to generate GitHub Pages URL from course map path
function getGitHubPagesUrl(githubPath) {
  if (!githubPath) return null;
  // Remove 'pages/' prefix if present, as GitHub Pages serves from repo root
  const cleanPath = githubPath.replace(/^pages\//, '');
  return `${GITHUB_PAGES_BASE}/${cleanPath}`;
}

// Function to find page by title text
function findPageByTitle(titleText) {
  // Try exact match first
  const normalized = titleText.toLowerCase().trim();
  for (const page of courseMap.pages) {
    const pageTitle = page.title.replace(/_/g, ' ').toLowerCase();
    if (pageTitle === normalized || page.slug === normalized) {
      return page;
    }
  }
  return null;
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
function updateLinkBlock(match, pageText, oldLinks) {
  // Extract page title from page-text
  const titleMatch = pageText.match(/>([^<]+)</);
  if (!titleMatch) return match;

  const pageTitle = titleMatch[1].trim();
  const page = findPageByTitle(pageTitle);

  if (!page) {
    console.warn(`⚠️  Page not found in course map: "${pageTitle}"`);
    return match; // Return unchanged if page not found
  }

  // Generate new links
  const viewDocxUrl = page.box?.file_url || '#';
  const editDocxUrl = page.box?.word_online_url || '#';
  const viewCanvasUrl = page.github?.with_assets?.path
    ? getGitHubPagesUrl(page.github.with_assets.path)
    : null;
  const editCanvasUrl = page.canvas?.url || '#';

  let newLinks = `<a href="${viewDocxUrl}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="${editDocxUrl}" target="_blank" rel="noopener noreferrer">edit docx</a>`;

  // Add 10px whitespace (using non-breaking space with margin)
  newLinks += ' <span style="margin-left: 10px;"></span> ';

  if (viewCanvasUrl) {
    newLinks += `<a href="${viewCanvasUrl}" target="_blank" rel="noopener noreferrer">view canvas</a>`;
  } else {
    newLinks += `<span style="color: #999;">view canvas</span>`;
  }

  newLinks += ' | ';
  newLinks += `<a href="${editCanvasUrl}" target="_blank" rel="noopener noreferrer">edit canvas</a>`;

  return `${pageText} <span class="page-links">${newLinks}</span>`;
}

// Update all link blocks in the HTML
// Pattern: <span class="page-text">...</span> <span class="page-links">...</span>
const linkPattern = /(<span class="page-text">[^<]+<\/span>)\s*<span class="page-links">([^<]*(?:<[^>]+>[^<]*<\/[^>]+>[^<]*)*)<\/span>/g;

htmlContent = htmlContent.replace(linkPattern, updateLinkBlock);

// Also handle cases where links might be in h2, h3, or li tags directly
// Pattern for h2/h3: <h2><span class="page-text">...</span> <span class="page-links">...</span></h2>
const headingPattern = /(<h[23]><span class="page-text">[^<]+<\/span>)\s*<span class="page-links">([^<]*(?:<[^>]+>[^<]*<\/[^>]+>[^<]*)*)<\/span><\/h[23]>/g;

htmlContent = htmlContent.replace(headingPattern, (match, pageText, oldLinks) => {
  const updated = updateLinkBlock(match, pageText, oldLinks);
  // Extract the tag (h2 or h3)
  const tagMatch = match.match(/<h([23])>/);
  const tag = tagMatch ? `h${tagMatch[1]}` : 'h2';
  return `<${tag}>${updated}</${tag}>`;
});

// Pattern for li: <li><span class="page-text">...</span> <span class="page-links">...</span></li>
const listItemPattern = /(<li><span class="page-text">[^<]+<\/span>)\s*<span class="page-links">([^<]*(?:<[^>]+>[^<]*<\/[^>]+>[^<]*)*)<\/span><\/li>/g;

htmlContent = htmlContent.replace(listItemPattern, (match, pageText, oldLinks) => {
  const updated = updateLinkBlock(match, pageText, oldLinks);
  return `<li>${updated}</li>`;
});

// Write updated HTML
writeFileSync(HTML_FILE_PATH, htmlContent, 'utf-8');

console.log('✅ Updated Canvas Course DOCX Editor HTML file');
console.log(`   File: ${HTML_FILE_PATH}`);
console.log(`   Pages in course map: ${courseMap.pages.length}`);
