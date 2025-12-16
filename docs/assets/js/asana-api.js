/**
 * Asana API Client (MVP)
 * Direct API calls using Personal Access Token
 */

import { ASANA_ACCESS_TOKEN, ASANA_PROJECT_ID, ASANA_WORKSPACE_ID } from './asana-config.js';

const ASANA_API_BASE_URL = 'https://app.asana.com/api/1.0';

/**
 * Makes an authenticated request to the Asana API.
 * @param {string} endpoint - The API endpoint (e.g., '/tasks/123', '/projects/456/custom_fields').
 * @param {string} method - HTTP method (GET, POST, PUT).
 * @param {object} data - Request body data.
 * @returns {Promise<object>} - The JSON response from the Asana API.
 */
async function asanaApiRequest(endpoint, method = 'GET', data = null) {
  const headers = {
    'Authorization': `Bearer ${ASANA_ACCESS_TOKEN}`,
    'Content-Type': 'application/json',
  };

  const config = {
    method: method,
    headers: headers,
  };

  if (data) {
    config.body = JSON.stringify({ data });
  }

  const response = await fetch(`${ASANA_API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const errorBody = await response.json();
    throw new Error(`Asana API Error ${response.status}: ${errorBody.errors.map(e => e.message).join(', ')}`);
  }

  return (await response.json()).data;
}

// Custom field definitions cache (includes enum options with colors)
let customFieldDefinitions = null; // Maps field name -> field GID
let fieldGidToName = {}; // Reverse mapping: field GID -> field name
let enumOptionsCache = {}; // Maps field GID -> { optionGID: { name, color } }

/**
 * Fetch custom field definitions for the project
 * Includes enum options with their colors
 * @returns {Promise<object>} - Object with fieldGids and enumOptions mappings
 */
export async function fetchCustomFieldDefinitions() {
  // Check sessionStorage cache first
  const cacheKey = 'asana_field_definitions';
  const cached = sessionStorage.getItem(cacheKey);
  if (cached) {
      try {
        const parsed = JSON.parse(cached);
        customFieldDefinitions = parsed.fieldGids;
        enumOptionsCache = parsed.enumOptions;
        // Rebuild reverse mapping from cached data
        fieldGidToName = {};
        for (const [name, gid] of Object.entries(parsed.fieldGids)) {
          fieldGidToName[gid] = name;
        }
        return parsed;
      } catch (e) {
        // Invalid cache, continue to fetch
      }
  }

  // Fetch from API
  try {
    const endpoint = `/projects/${ASANA_PROJECT_ID}/custom_field_settings?opt_fields=custom_field.name,custom_field.resource_subtype,custom_field.enum_options.name,custom_field.enum_options.color,custom_field.enum_options.gid`;
    const settings = await asanaApiRequest(endpoint);

    const fieldDefs = {
      fieldGids: {},
      enumOptions: {}
    };

    settings.forEach(setting => {
      const field = setting.custom_field;
      const fieldName = field.name;
      const fieldGid = field.gid;

      fieldDefs.fieldGids[fieldName] = fieldGid;
      // Build reverse mapping: GID -> name (for lookup from task.custom_fields)
      fieldGidToName[fieldGid] = fieldName;

      // Store enum options with colors
      if (field.enum_options && field.enum_options.length > 0) {
        fieldDefs.enumOptions[fieldGid] = {};
        field.enum_options.forEach(opt => {
          fieldDefs.enumOptions[fieldGid][opt.gid] = {
            name: opt.name,
            color: opt.color // Color values: blue, green, red, yellow, purple, orange, etc.
          };
        });
        enumOptionsCache[fieldGid] = fieldDefs.enumOptions[fieldGid];
      }
    });

    customFieldDefinitions = fieldDefs.fieldGids;

    // Cache in sessionStorage
    sessionStorage.setItem(cacheKey, JSON.stringify(fieldDefs));

    return fieldDefs;
  } catch (error) {
    console.error('Error fetching custom field definitions:', error);
    throw error;
  }
}

/**
 * Get the color for an enum option value
 * @param {string} fieldGid - The custom field GID
 * @param {string} optionGid - The enum option GID
 * @returns {string|null} - The color name (e.g., 'blue', 'green', 'red') or null
 */
export function getEnumOptionColor(fieldGid, optionGid) {
  if (!enumOptionsCache[fieldGid] || !optionGid) {
    return null;
  }
  const option = enumOptionsCache[fieldGid][optionGid];
  if (option && option.color) {
    return option.color;
  }
  return null;
}

/**
 * Get the color for an enum option by field name and option name
 * @param {string} fieldName - The custom field name (e.g., 'update ?')
 * @param {string} optionName - The enum option name (e.g., 'review', 'yes', 'no')
 * @returns {string|null} - The color name or null
 */
export function getEnumOptionColorByName(fieldName, optionName) {
  if (!customFieldDefinitions || !customFieldDefinitions[fieldName]) {
    return null;
  }

  const fieldGid = customFieldDefinitions[fieldName];
  if (!enumOptionsCache[fieldGid]) {
    return null;
  }

  // Find option by name
  for (const [optionGid, option] of Object.entries(enumOptionsCache[fieldGid])) {
    if (option.name === optionName) {
      return option.color;
    }
  }

  return null;
}

/**
 * Fetches a single task's details, including custom fields.
 * @param {string} taskId - The GID of the task.
 * @returns {Promise<object>} - The task object with custom fields.
 */
export async function fetchTask(taskId) {
  // Fetch task with all custom fields (including enum values with GIDs for color lookup)
  // Also include resource_subtype to identify field types
  return asanaApiRequest(`/tasks/${taskId}?opt_fields=name,custom_fields,custom_fields.enum_value.gid,custom_fields.enum_value.name,custom_fields.resource_subtype,custom_fields.text_value`);
}

/**
 * Extracts custom field values from a task object, including enum option colors.
 * @param {object} task - The task object from Asana API.
 * @returns {Promise<object>} - An object with custom field values and colors.
 */
export async function extractCustomFieldValues(task) {
  // Ensure definitions are loaded
  await fetchCustomFieldDefinitions();

  const result = {
    'update ?': { value: 'review', color: null },  // Default for update ? is 'review', not placeholder
    'edit docx': { value: '', color: null },
    'docx update': { value: '  -', color: null },  // Placeholder for update/review fields
    'docx review': { value: '  -', color: null },
    'edit canvas': { value: '', color: null },
    'canvas update': { value: '  -', color: null },
    'canvas review': { value: '  -', color: null },
  };

  if (!task || !task.custom_fields) {
    return result;
  }

  // Process each custom field
  task.custom_fields.forEach(field => {
    const fieldGid = field.gid;

    // Find field name by GID using dynamically fetched definitions
    const fieldName = fieldGidToName[fieldGid];

    // Debug logging for task 1212480690742245
    if (task.gid === '1212480690742245') {
      console.log('Processing field:', {
        fieldGid,
        fieldName,
        hasEnumValue: !!field.enum_value,
        enumValue: field.enum_value,
        resourceSubtype: field.resource_subtype,
        textValue: field.text_value,
        fieldGidToName: fieldGidToName
      });
    }

    // Skip if field name not found or not in our result set
    if (!fieldName || !result.hasOwnProperty(fieldName)) {
      return; // Field not in our mapping
    }

    // Extract value and color based on field type
    if (field.enum_value) {
      // Enum field with a selected value - get name and color
      const optionName = field.enum_value?.name || '-';
      const optionGid = field.enum_value?.gid;

      // Try to get color by GID first, then fall back to name lookup
      let color = optionGid ? getEnumOptionColor(fieldGid, optionGid) : null;
      if (!color) {
        // Fallback: try to find color by option name
        color = getEnumOptionColorByName(fieldName, optionName);
      }

      result[fieldName] = {
        value: optionName,
        color: color
      };
    } else if (field.resource_subtype === 'enum' || enumOptionsCache[fieldGid]) {
      // Enum field but no value selected - show placeholder "  -"
      result[fieldName] = {
        value: '  -',
        color: null
      };
    } else if (field.text_value !== undefined && field.text_value !== null) {
      // Text field - no color
      result[fieldName] = {
        value: field.text_value,
        color: null
      };
    }
  });

  return result;
}

/**
 * Convert Asana color name to background and text color values
 * Returns colors that match Asana's badge styling with sufficient contrast
 * @param {string} asanaColor - Asana color name (e.g., 'blue', 'green', 'red')
 * @returns {object} - Object with backgroundColor and color (text color) properties
 */
export function asanaColorToCSS(asanaColor) {
  const colorMap = {
    'blue': {
      backgroundColor: '#1976D2',  // Darker blue for better contrast (was #4A90E2)
      color: '#FFFFFF'              // White text for contrast
    },
    'green': {
      backgroundColor: '#2E7D32',   // Even darker green for better contrast (was #388E3C)
      color: '#FFFFFF'              // White text for contrast
    },
    'red': {
      backgroundColor: '#D32F2F',   // Darker red for better contrast (was #F44336)
      color: '#FFFFFF'              // White text for contrast
    },
    'yellow': {
      backgroundColor: '#F9A825',   // Medium yellow/orange - use black text for contrast
      color: '#000000'              // Black text for better contrast on yellow
    },
    'orange': {
      backgroundColor: '#BF360C',   // Very dark orange/red to meet contrast (was #D84315)
      color: '#FFFFFF'              // White text for contrast
    },
    'purple': {
      backgroundColor: '#7B1FA2',   // Darker purple for better contrast (was #9C27B0)
      color: '#FFFFFF'              // White text for contrast
    },
    'pink': {
      backgroundColor: '#C2185B',   // Darker pink for better contrast (was #E91E63)
      color: '#FFFFFF'              // White text for contrast
    },
    'black': {
      backgroundColor: '#212121',   // Very dark gray/black background
      color: '#FFFFFF'              // White text for contrast
    },
    'grey': {
      backgroundColor: '#616161',   // Darker gray for better contrast (was #9E9E9E)
      color: '#FFFFFF'              // White text for contrast
    },
  };

  return colorMap[asanaColor] || { backgroundColor: '#212121', color: '#FFFFFF' };
}
