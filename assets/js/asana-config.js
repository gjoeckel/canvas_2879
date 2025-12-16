// Asana Configuration (MVP)
// TODO: Replace with OAuth after MVP validation

// Personal Access Token - REPLACE WITH YOUR TOKEN
// Get token from: https://app.asana.com/0/my-apps
export const ASANA_ACCESS_TOKEN = '2/1210006544495609/1212398888020207:d221a1678dff1a0bd619636b49b7df93';

// Project configuration
export const ASANA_PROJECT_ID = '1212479530389064';
export const ASANA_WORKSPACE_ID = '970807752514981';

// Custom field GIDs (from custom-fields-mapping.json)
export const ASANA_CUSTOM_FIELD_GIDS = {
  'update ?': '1212480212876970',
  'edit docx': '1212455818928369',
  'docx update': '1212480212876972',
  'docx review': '1212480212876976',
  'edit canvas': '1212480215429505',
  'canvas update': '1212480215429507',
  'canvas review': '1212480215429511',
};

// Enum option GIDs (from enum-options-mapping.json)
export const ASANA_ENUM_OPTIONS = {
  '1212480212876970': { // update ?
    '1212480212876971': 'review',
    '1212480212876973': 'yes',
    '1212480212876974': 'no',
  },
  '1212480212876972': { // docx update
    '1212480212876975': 'not started',
    '1212480212876977': 'started',
    '1212480212876978': 'completed',
    '1212480212876979': 'NA',
  },
  '1212480212876976': { // docx review
    '1212480212876980': 'not started',
    '1212480212876981': 'started',
    '1212480212876982': 'completed',
    '1212480212876983': 'NA',
  },
  '1212480215429507': { // canvas update
    '1212480215429508': 'not started',
    '1212480215429509': 'started',
    '1212480215429510': 'completed',
    '1212480215429512': 'NA',
  },
  '1212480215429511': { // canvas review
    '1212480215429513': 'not started',
    '1212480215429514': 'started',
    '1212480215429515': 'completed',
    '1212480215429516': 'NA',
  },
};
