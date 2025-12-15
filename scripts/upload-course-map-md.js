#!/usr/bin/env node
/**
 * Upload course-map.md to Box
 */

import { readFileSync } from 'fs';
import { executeWithRefresh } from '../../Agents/cursor-ops/mcp-box-minimal/src/box-client.js';
import { getBoxClient } from '../../Agents/cursor-ops/mcp-box-minimal/src/box-client.js';
import { Readable } from 'stream';

const COURSE_MAP_PATH = '/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/course-map.md';
const BOX_FOLDER_ID = '355472814432';

// Read the markdown file
const markdownContent = readFileSync(COURSE_MAP_PATH, 'utf-8');
const fileBuffer = Buffer.from(markdownContent, 'utf-8');

// Upload to Box with automatic token refresh
const uploadedFile = await executeWithRefresh(async (client) => {
  return await client.uploads.uploadFile({
    attributes: {
      name: 'course-map.md',
      parent: {
        id: BOX_FOLDER_ID,
      },
    },
    file: Readable.from(fileBuffer) as any,
  });
});

console.log('✅ Uploaded course-map.md to Box');
console.log(`   File ID: ${uploadedFile.entries[0].id}`);
console.log(`   URL: https://usu.app.box.com/file/${uploadedFile.entries[0].id}`);
