/**
 * Asana Status Display (MVP)
 * Handles loading and displaying task statuses on pages
 * Works with the new 3-column layout (Asana, Box, Canvas)
 */

import { fetchTask, extractCustomFieldValues, fetchCustomFieldDefinitions, asanaColorToCSS } from './asana-api.js';
import { ASANA_PROJECT_ID, ASANA_WORKSPACE_ID } from './asana-config.js';

// Task mapping cache
let taskMapping = null;

/**
 * Load task mapping from JSON file
 */
async function loadTaskMapping() {
  if (taskMapping) {
    return taskMapping; // Already loaded
  }

  try {
    // Use path relative to the HTML file location
    // Works both locally (http://localhost:8000/) and on GitHub Pages (https://gjoeckel.github.io/canvas_2879/)
    // Remove filename and trailing slashes to get base directory
    let basePath = window.location.pathname.replace(/\/[^/]*$/, '').replace(/\/$/, '') || '';
    // Ensure leading slash for absolute path
    if (basePath && !basePath.startsWith('/')) {
      basePath = '/' + basePath;
    }
    const dataPath = `${basePath}/data/asana-task-mapping.json`;
    const response = await fetch(dataPath);
    if (!response.ok) {
      throw new Error(`Failed to load task mapping: ${response.status}`);
    }
    taskMapping = await response.json();
    return taskMapping;
  } catch (error) {
    console.error('Error loading task mapping:', error);
    return {};
  }
}

/**
 * Extract page ID from Canvas edit URL
 */
function extractPageIdFromCanvasUrl(url) {
  if (!url) return null;
  const match = url.match(/\/pages\/([^\/\?]+)\/edit/);
  return match ? match[1] : null;
}

/**
 * Get task ID for a page element by extracting page ID from Canvas URL
 */
async function getTaskIdForPageElement(element) {
  // Find the Canvas edit link in the Canvas column
  const columnsContainer = element.nextElementSibling;
  if (!columnsContainer || !columnsContainer.classList.contains('page-links-columns')) {
    return null;
  }

  const canvasColumn = columnsContainer.querySelector('.canvas-column');
  if (!canvasColumn) {
    return null;
  }

  const canvasEditLink = canvasColumn.querySelector('a[href*="/edit"]');
  if (!canvasEditLink) {
    return null;
  }

  const canvasUrl = canvasEditLink.getAttribute('href');
  const pageId = extractPageIdFromCanvasUrl(canvasUrl);
  if (!pageId) {
    return null;
  }

  // Look up in task mapping
  const mapping = await loadTaskMapping();
  return mapping[pageId] || null;
}

/**
 * Update the 3-column links with Asana task data
 */
function updateLinkColumns(taskId, fields, columnsContainer) {
  const focusUrl = `https://app.asana.com/1/${ASANA_WORKSPACE_ID}/project/${ASANA_PROJECT_ID}/task/${taskId}?focus=true`;

  // Update Asana column
  const asanaColumn = columnsContainer.querySelector('.asana-column');
  if (asanaColumn) {
    // Update update ? status (with color badge styling)
    const updateQuestion = asanaColumn.querySelector('[data-asana-field="update ?"]');
    if (updateQuestion) {
      const fieldData = fields['update ?'] || { value: 'review', color: null };
      updateQuestion.textContent = fieldData.value;
      // Only apply badge styling if we have a color (i.e., not the "-" placeholder)
      if (fieldData && typeof fieldData === 'object' && fieldData.color !== null && fieldData.color !== undefined && fieldData.value !== '  -') {
        const colors = asanaColorToCSS(fieldData.color);
        updateQuestion.style.backgroundColor = colors.backgroundColor;
        updateQuestion.style.color = colors.color;
        updateQuestion.classList.add('asana-badge');
      } else {
        // Reset styles for placeholder
        updateQuestion.style.backgroundColor = '';
        updateQuestion.style.color = '';
        updateQuestion.classList.remove('asana-badge');
      }
    }

    // Update open task link
    const openLink = asanaColumn.querySelector('.open-asana-link');
    if (openLink) {
      openLink.href = focusUrl;
      openLink.setAttribute('data-task-id', taskId);
    }

    // Update refresh task link
    const refreshLink = asanaColumn.querySelector('.refresh-asana-link');
    if (refreshLink) {
      refreshLink.setAttribute('data-task-id', taskId);
    }
  }

  // Update Box column
  const boxColumn = columnsContainer.querySelector('.box-column');
  if (boxColumn) {
    // Update docx update status (with color badge styling)
    const docxUpdate = boxColumn.querySelector('[data-asana-field="docx update"]');
    if (docxUpdate) {
      const fieldData = fields['docx update'] || { value: '  -', color: null };
      // Only update textContent if value is NOT the placeholder (preserve HTML placeholder)
      if (fieldData.value !== '  -') {
        docxUpdate.textContent = fieldData.value;
      }
      // Only apply badge styling if we have a color (i.e., not the "-" placeholder)
      if (fieldData && typeof fieldData === 'object' && fieldData.color !== null && fieldData.color !== undefined && fieldData.value !== '  -') {
        const colors = asanaColorToCSS(fieldData.color);
        docxUpdate.style.backgroundColor = colors.backgroundColor;
        docxUpdate.style.color = colors.color;
        docxUpdate.classList.add('asana-badge');
      } else {
        // Reset styles if no color (placeholder)
        docxUpdate.style.backgroundColor = '';
        docxUpdate.style.color = '';
        docxUpdate.classList.remove('asana-badge');
      }
    }

    // Update docx review status (with color badge styling)
    const docxReview = boxColumn.querySelector('[data-asana-field="docx review"]');
    if (docxReview) {
      const fieldData = fields['docx review'] || { value: '  -', color: null };
      // Only update textContent if value is NOT the placeholder (preserve HTML placeholder)
      if (fieldData.value !== '  -') {
        docxReview.textContent = fieldData.value;
      }
      // Only apply badge styling if we have a color (i.e., not the "-" placeholder)
      if (fieldData && typeof fieldData === 'object' && fieldData.color !== null && fieldData.color !== undefined && fieldData.value !== '  -') {
        const colors = asanaColorToCSS(fieldData.color);
        docxReview.style.backgroundColor = colors.backgroundColor;
        docxReview.style.color = colors.color;
        docxReview.classList.add('asana-badge');
      } else {
        // Reset styles if no color (placeholder)
        docxReview.style.backgroundColor = '';
        docxReview.style.color = '';
        docxReview.classList.remove('asana-badge');
      }
    }
  }

  // Update Canvas column
  const canvasColumn = columnsContainer.querySelector('.canvas-column');
  if (canvasColumn) {
    // Update canvas update status (with color badge styling)
    const canvasUpdate = canvasColumn.querySelector('[data-asana-field="canvas update"]');
    if (canvasUpdate) {
      const fieldData = fields['canvas update'];
      if (!fieldData) {
        // Field not found in response - keep default placeholder, skip this field
        // Continue to next field instead of returning
      } else {
        // Only update textContent if value is NOT the placeholder (preserve HTML placeholder)
        if (fieldData.value !== '  -') {
          canvasUpdate.textContent = fieldData.value;
        }
        // Only apply badge styling if we have a color (i.e., not the "-" placeholder)
        if (fieldData.color !== null && fieldData.color !== undefined && fieldData.value !== '  -') {
          const colors = asanaColorToCSS(fieldData.color);
          canvasUpdate.style.backgroundColor = colors.backgroundColor;
          canvasUpdate.style.color = colors.color;
          canvasUpdate.classList.add('asana-badge');
        } else {
          // Reset styles if no color (placeholder)
          canvasUpdate.style.backgroundColor = '';
          canvasUpdate.style.color = '';
          canvasUpdate.classList.remove('asana-badge');
        }
      }
    }

    // Update canvas review status (with color badge styling)
    const canvasReview = canvasColumn.querySelector('[data-asana-field="canvas review"]');
    if (canvasReview) {
      const fieldData = fields['canvas review'];
      if (!fieldData) {
        // Field not found in response - keep default placeholder, skip this field
        // Continue to next field instead of returning
      } else {
        // Only update textContent if value is NOT the placeholder (preserve HTML placeholder)
        if (fieldData.value !== '  -') {
          canvasReview.textContent = fieldData.value;
        }
        // Only apply badge styling if we have a color (i.e., not the "-" placeholder)
        if (fieldData.color !== null && fieldData.color !== undefined && fieldData.value !== '  -') {
          const colors = asanaColorToCSS(fieldData.color);
          canvasReview.style.backgroundColor = colors.backgroundColor;
          canvasReview.style.color = colors.color;
          canvasReview.classList.add('asana-badge');
        } else {
          // Reset styles if no color (placeholder)
          canvasReview.style.backgroundColor = '';
          canvasReview.style.color = '';
          canvasReview.classList.remove('asana-badge');
        }
      }
    }
  }

  // Setup refresh button event listener
  const refreshLink = columnsContainer.querySelector('.refresh-asana-link');
  if (refreshLink) {
    // Remove existing listener by cloning
    const newRefreshLink = refreshLink.cloneNode(true);
    refreshLink.parentNode.replaceChild(newRefreshLink, refreshLink);

    newRefreshLink.addEventListener('click', async (e) => {
      e.preventDefault();
      const targetTaskId = newRefreshLink.getAttribute('data-task-id');
      if (targetTaskId) {
        // Get task name from the heading first (for immediate display)
        const pageElement = columnsContainer.previousElementSibling;
        let taskName = 'task';
        if (pageElement) {
          const pageText = pageElement.querySelector('.page-text');
          if (pageText) {
            taskName = pageText.textContent.trim();
          }
        }

        // Show message
        const messageDiv = document.getElementById('asana-refresh-message');
        if (messageDiv) {
          messageDiv.textContent = `Refreshing ${taskName} task....`;
        }

        try {
          const refreshedTask = await fetchTask(targetTaskId);
          // Use task name from API response if available (more accurate)
          if (refreshedTask.name) {
            taskName = refreshedTask.name;
          }
          const refreshedFields = await extractCustomFieldValues(refreshedTask);
          updateLinkColumns(targetTaskId, refreshedFields, columnsContainer);

          // Clear message after success
          if (messageDiv) {
            setTimeout(() => {
              messageDiv.textContent = '';
            }, 3000);
          }
        } catch (error) {
          console.error('Error refreshing task:', error);
          // Show error message
          if (messageDiv) {
            messageDiv.textContent = `Error refreshing ${taskName} task. Please try again.`;
            setTimeout(() => {
              messageDiv.textContent = '';
            }, 3000);
          }
        }
      }
    });
  }
}

/**
 * Get task ID for a page element (synchronous version for batching)
 */
function getTaskIdForPageElementSync(element, taskMapping) {
  // Find the Canvas edit link in the Canvas column
  const columnsContainer = element.nextElementSibling;
  if (!columnsContainer || !columnsContainer.classList.contains('page-links-columns')) {
    return null;
  }

  const canvasColumn = columnsContainer.querySelector('.canvas-column');
  if (!canvasColumn) {
    return null;
  }

  const canvasEditLink = canvasColumn.querySelector('a[href*="/edit"]');
  if (!canvasEditLink) {
    return null;
  }

  const canvasUrl = canvasEditLink.getAttribute('href');
  const pageId = extractPageIdFromCanvasUrl(canvasUrl);
  if (!pageId) {
    return null;
  }

  // Look up in task mapping
  return taskMapping[pageId] || null;
}

/**
 * Load and display status for a specific page element
 * @deprecated - Use batch loading instead for better performance
 */
async function loadTaskStatusForElement(element) {
  // Find the columns container (should be the next sibling)
  const columnsContainer = element.nextElementSibling;
  if (!columnsContainer || !columnsContainer.classList.contains('page-links-columns')) {
    return; // No columns container found
  }

  const taskId = await getTaskIdForPageElement(element);
  if (!taskId) {
    // No task ID - hide the entire columns container or just the Asana column
    const asanaColumn = columnsContainer.querySelector('.asana-column');
    if (asanaColumn) {
      asanaColumn.style.display = 'none';
    }
    return;
  }

  try {
    const task = await fetchTask(taskId);
    const fields = await extractCustomFieldValues(task);

    // Debug logging for troubleshooting
    if (taskId === '1212480690742245') {
      console.log('Task data for 1.1:', task);
      console.log('Extracted fields for 1.1:', fields);
    }

    updateLinkColumns(taskId, fields, columnsContainer);
  } catch (error) {
    console.error('Error loading task status:', error);
    const asanaColumn = columnsContainer.querySelector('.asana-column');
    if (asanaColumn) {
      asanaColumn.innerHTML = '<strong>Asana</strong><ul><li class="status-item">Error loading status</li></ul>';
    }
  }
}

/**
 * Batch load and update all task statuses
 * Fetches all tasks in parallel, then updates all DOM elements at once
 */
async function batchLoadTaskStatuses() {
  // Step 1: Load task mapping and custom field definitions
  const taskMapping = await loadTaskMapping();
  await fetchCustomFieldDefinitions();

  // Step 2: Find all headings with columns containers and get their task IDs
  const headings = document.querySelectorAll('h2, h3, h4');
  const taskDataMap = new Map(); // Map of taskId -> { element, columnsContainer }

  for (const heading of headings) {
    const columnsContainer = heading.nextElementSibling;
    if (!columnsContainer || !columnsContainer.classList.contains('page-links-columns')) {
      continue;
    }

    const taskId = getTaskIdForPageElementSync(heading, taskMapping);
    if (taskId) {
      taskDataMap.set(taskId, {
        element: heading,
        columnsContainer: columnsContainer
      });
    } else {
      // No task ID - hide Asana column
      const asanaColumn = columnsContainer.querySelector('.asana-column');
      if (asanaColumn) {
        asanaColumn.style.display = 'none';
      }
    }
  }

  if (taskDataMap.size === 0) {
    return; // No tasks to fetch
  }

  // Step 3: Fetch all tasks in batches to avoid rate limiting
  // Asana rate limit: ~150 requests per minute
  // Batch size: 10 requests per batch with 500ms delay between batches
  const taskIds = Array.from(taskDataMap.keys());
  const BATCH_SIZE = 10;
  const BATCH_DELAY_MS = 500;
  const tasks = [];

  for (let i = 0; i < taskIds.length; i += BATCH_SIZE) {
    const batch = taskIds.slice(i, i + BATCH_SIZE);
    const batchPromises = batch.map(taskId =>
      fetchTask(taskId).catch(error => {
        console.error(`Error fetching task ${taskId}:`, error);
        return null; // Return null on error, we'll handle it below
      })
    );

    const batchResults = await Promise.all(batchPromises);
    tasks.push(...batchResults);

    // Add delay between batches (except for the last batch)
    if (i + BATCH_SIZE < taskIds.length) {
      await new Promise(resolve => setTimeout(resolve, BATCH_DELAY_MS));
    }
  }

  // Step 4: Extract custom field values for all tasks in parallel
  const fieldExtractionPromises = tasks.map((task, i) => {
    const taskId = taskIds[i];
    if (!task) return Promise.resolve(null);

    return extractCustomFieldValues(task).then(fields => {
      // Debug logging for troubleshooting
      if (taskId === '1212480690742245') {
        console.log('Task data for 1.1:', task);
        console.log('Raw custom_fields array:', task.custom_fields);
        console.log('Extracted fields for 1.1:', fields);
        console.log('Field values:', {
          'docx update': fields['docx update'],
          'docx review': fields['docx review'],
          'canvas update': fields['canvas update'],
          'canvas review': fields['canvas review']
        });
      }
      return { taskId, fields };
    }).catch(error => {
      console.error(`Error extracting fields for task ${taskId}:`, error);
      return { taskId, fields: null };
    });
  });

  const fieldExtractionResults = await Promise.all(fieldExtractionPromises);
  const fieldValuesMap = new Map(); // Map of taskId -> fields object
  for (const result of fieldExtractionResults) {
    if (result && result.fields) {
      fieldValuesMap.set(result.taskId, result.fields);
    }
  }

  // Step 5: Update all DOM elements at once
  for (const [taskId, data] of taskDataMap.entries()) {
    const fields = fieldValuesMap.get(taskId);
    if (fields) {
      updateLinkColumns(taskId, fields, data.columnsContainer);
    } else {
      // Error loading task - show error message
      const asanaColumn = data.columnsContainer.querySelector('.asana-column');
      if (asanaColumn) {
        asanaColumn.innerHTML = '<strong>Asana</strong><ul><li class="status-item">Error loading status</li></ul>';
      }
    }
  }

  // All statuses have been updated - message will be cleared by initializeAsanaStatus()
}

/**
 * Initialize Asana status display for all pages on the current page
 * Uses batch loading for better performance - fetches all tasks in parallel,
 * then updates all DOM elements at once
 */
export async function initializeAsanaStatus() {
  // Show loading message when page first loads
  const messageDiv = document.getElementById('asana-refresh-message');
  if (messageDiv) {
    messageDiv.textContent = 'Task data being retrieved from Asana.';
  }

  try {
    // Use batch loading for better performance
    await batchLoadTaskStatuses();

    // Clear message after all statuses are updated
    if (messageDiv) {
      messageDiv.textContent = '';
    }
  } catch (error) {
    console.error('Error initializing Asana status:', error);
    // Clear message even on error
    if (messageDiv) {
      messageDiv.textContent = '';
    }
  }
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeAsanaStatus);
} else {
  initializeAsanaStatus();
}
