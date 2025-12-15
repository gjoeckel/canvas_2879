#!/usr/bin/env node
/**
 * Move files in Box Start Here folder to correct subfolders
 */

// Box folder IDs
const ROOT_FOLDER_ID = '355472814432';
const FOLDER_IDS = {
  '1-course-orientation': '356024870284',
  '2-course-details': '356023244847',
  '3-terms-of-use': '356022969543'
};

// File mappings: fileName -> target folder
const FILE_MAPPINGS = {
  // Course Orientation files
  '1235426.png': '1-course-orientation',
  '1235470.png': '1-course-orientation',
  '1235475.png': '1-course-orientation',
  '1235530.png': '1-course-orientation',
  '1235607.png': '1-course-orientation',
  '1235615.png': '1-course-orientation',
  'course_orientation.docx': '1-course-orientation',
  'course_orientation.html': '1-course-orientation',
  'course_orientation_local.html': '1-course-orientation',
  'course orientation_local.html': '1-course-orientation', // Note: different name in Box

  // Course Details files
  'course_details.html': '2-course-details',
  'course_details_local.html': '2-course-details',
  'course_details.docx': '2-course-details',

  // Terms of Use files
  'terms_of_use.html': '3-terms-of-use',
  'terms_of_use_local.html': '3-terms-of-use',
  'terms_of_use.docx': '3-terms-of-use'
};

async function fileExistsInFolder(accessToken, folderId, fileName) {
  try {
    const response = await fetch(`https://api.box.com/2.0/folders/${folderId}/items?fields=id,name,type`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    if (!response.ok) return false;

    const data = await response.json();
    return data.entries.some(item => item.type === 'file' && item.name === fileName);
  } catch (error) {
    return false;
  }
}

async function moveFile(accessToken, fileId, targetFolderId, fileName, retries = 3) {
  // Check if file already exists in target folder
  const exists = await fileExistsInFolder(accessToken, targetFolderId, fileName);
  if (exists) {
    console.log(`  ⊘ File already exists in target folder, skipping move`);
    return { skipped: true };
  }

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await fetch(`https://api.box.com/2.0/files/${fileId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          parent: { id: targetFolderId }
        })
      });

      if (response.status === 409 && attempt < retries) {
        // Wait before retrying (409 = name temporarily reserved)
        const waitTime = attempt * 1000; // 1s, 2s, 3s
        console.log(`  ⏳ Waiting ${waitTime}ms before retry...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
        continue;
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      if (attempt === retries) {
        throw new Error(`Failed to move ${fileName}: ${error.message}`);
      }
      // Continue to retry
    }
  }
}

async function main() {
  const accessToken = process.env.BOX_ACCESS_TOKEN;
  if (!accessToken) {
    console.error('❌ BOX_ACCESS_TOKEN environment variable is required');
    process.exit(1);
  }

  console.log('🔄 Moving files to correct folders in Box...\n');

  // Get all items in root folder
  console.log('📋 Fetching files from root folder...');
  const response = await fetch(`https://api.box.com/2.0/folders/${ROOT_FOLDER_ID}/items?fields=id,name,type`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to list folder: ${response.status}`);
  }

  const data = await response.json();
  const files = data.entries.filter(item => item.type === 'file');

  console.log(`✓ Found ${files.length} files\n`);

  // Move files to appropriate folders
  let movedCount = 0;
  let skippedCount = 0;

  for (const file of files) {
    const fileName = file.name;

    // Skip .DS_Store
    if (fileName === '.DS_Store') {
      console.log(`⊘ Skipping: ${fileName}`);
      skippedCount++;
      continue;
    }

    const targetFolder = FILE_MAPPINGS[fileName];

    if (!targetFolder) {
      console.log(`⚠️  No mapping for: ${fileName}`);
      skippedCount++;
      continue;
    }

    const targetFolderId = FOLDER_IDS[targetFolder];

    try {
      console.log(`📦 Moving ${fileName} → ${targetFolder}/`);
      await moveFile(accessToken, file.id, targetFolderId, fileName);
      console.log(`  ✓ Moved successfully\n`);
      movedCount++;
    } catch (error) {
      console.error(`  ✗ Error: ${error.message}\n`);
    }
  }

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`✅ Move complete!`);
  console.log(`   Moved: ${movedCount} files`);
  console.log(`   Skipped: ${skippedCount} files`);
}

main().catch(error => {
  console.error('\n❌ Error:', error.message);
  process.exit(1);
});
