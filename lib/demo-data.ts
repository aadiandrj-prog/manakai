export type Standard = {
  id: string;
  number: string;
  title: string;
  version: string;
  status: 'ACTIVE' | 'AMENDED' | 'UPCOMING' | 'SUPERSEDED';
  category: string;
  scope: string;
  sourceLabel: string;
  sourceKind: 'demo' | 'verified';
  lastChecked: string;
};

export type Laboratory = {
  id: string;
  name: string;
  city: string;
  state: string;
  standards: string[];
  capabilities: string[];
  sourceKind: 'demo';
};

export const standards: Standard[] = [
  {
    id: 'is-10322-5-8',
    number: 'IS 10322 (Part 5/Sec 8)',
    title: 'Luminaires — Particular requirements: emergency lighting',
    version: '2013',
    status: 'ACTIVE',
    category: 'Electrical',
    scope:
      'Demo scope record for luminaires used for emergency lighting. Confirm the current edition, amendments and applicability in the official BIS catalogue.',
    sourceLabel: 'Demo fixture · official verification required',
    sourceKind: 'demo',
    lastChecked: 'Not live',
  },
  {
    id: 'is-302-2-15',
    number: 'IS 302 (Part 2/Sec 15)',
    title:
      'Safety of household electrical appliances — Appliances for heating liquids',
    version: '2009',
    status: 'AMENDED',
    category: 'Electrical',
    scope:
      'Demo scope record for household appliances used to heat liquids, including kettle-like products.',
    sourceLabel: 'Demo fixture · official verification required',
    sourceKind: 'demo',
    lastChecked: 'Not live',
  },
  {
    id: 'is-4151',
    number: 'IS 4151',
    title: 'Protective helmets for scooter and motorcycle riders',
    version: '2015',
    status: 'ACTIVE',
    category: 'Consumer safety',
    scope:
      'Demo record representing performance and construction requirements for protective rider helmets.',
    sourceLabel: 'Demo fixture · official verification required',
    sourceKind: 'demo',
    lastChecked: 'Not live',
  },
  {
    id: 'is-1786',
    number: 'IS 1786',
    title:
      'High strength deformed steel bars and wires for concrete reinforcement',
    version: '2008',
    status: 'AMENDED',
    category: 'Construction',
    scope:
      'Demo record for reinforcement steel grades, mechanical properties and testing.',
    sourceLabel: 'Demo fixture · official verification required',
    sourceKind: 'demo',
    lastChecked: 'Not live',
  },
  {
    id: 'is-1417',
    number: 'IS 1417',
    title: 'Gold and gold alloys, jewellery/artefacts — fineness and marking',
    version: '2016',
    status: 'ACTIVE',
    category: 'Hallmarking',
    scope:
      'Demo consumer-support record for fineness and marking concepts used in hallmarking guidance.',
    sourceLabel: 'Demo fixture · official verification required',
    sourceKind: 'demo',
    lastChecked: 'Not live',
  },
];

export const laboratories: Laboratory[] = [
  {
    id: 'lab-delhi',
    name: 'Northstar Electrical Test Lab',
    city: 'New Delhi',
    state: 'Delhi',
    standards: ['IS 10322 (Part 5/Sec 8)', 'IS 302 (Part 2/Sec 15)'],
    capabilities: ['Electrical safety', 'Insulation resistance', 'Endurance'],
    sourceKind: 'demo',
  },
  {
    id: 'lab-noida',
    name: 'Apex Product Assurance Centre',
    city: 'Noida',
    state: 'Uttar Pradesh',
    standards: ['IS 4151', 'IS 10322 (Part 5/Sec 8)'],
    capabilities: ['Impact testing', 'Photometry', 'Thermal testing'],
    sourceKind: 'demo',
  },
  {
    id: 'lab-mumbai',
    name: 'Western Materials Validation Lab',
    city: 'Mumbai',
    state: 'Maharashtra',
    standards: ['IS 1786'],
    capabilities: ['Tensile testing', 'Chemical analysis', 'Bend and rebend'],
    sourceKind: 'demo',
  },
  {
    id: 'lab-jaipur',
    name: 'Aravali Assaying Demo Centre',
    city: 'Jaipur',
    state: 'Rajasthan',
    standards: ['IS 1417'],
    capabilities: ['Fineness testing', 'Assaying demonstration'],
    sourceKind: 'demo',
  },
];

export const emergencyProfile = {
  id: 'demo-emergency-lamp',
  product: 'Portable rechargeable LED emergency lamp',
  role: 'Manufacturer',
  category: 'Electrical lighting equipment',
  standard: standards[0],
  confidence: 91,
  certification: 'Needs authoritative verification',
  qco: 'No live QCO connection in demo mode',
  scheme: 'Demo pathway — confirm with BIS',
  attributes: [
    'Portable',
    'Rechargeable battery',
    'LED light source',
    'Emergency use',
  ],
  tests: [
    'Marking and construction review',
    'Insulation resistance',
    'Electric strength',
    'Battery endurance',
    'Emergency-mode photometry',
  ],
  documents: [
    'Product specification',
    'Critical component list',
    'Circuit diagram',
    'Test request form',
    'Manufacturing process flow',
  ],
  warnings: [
    'This profile uses seeded demonstration data.',
    'Mandatory status and dates have not been verified against a live authoritative BIS source.',
  ],
};

export const journeySteps = [
  {
    title: 'Classify product',
    detail: 'Lighting equipment → self-contained emergency luminaire',
    status: 'complete',
  },
  {
    title: 'Identify candidate standard',
    detail: 'IS 10322 (Part 5/Sec 8):2013',
    status: 'complete',
  },
  {
    title: 'Check mandatory status',
    detail: 'Connect current QCO source before relying on this decision',
    status: 'attention',
  },
  {
    title: 'Review product manual',
    detail: 'Confirm the latest BIS product manual and sampling plan',
    status: 'pending',
  },
  {
    title: 'Arrange recognised testing',
    detail: 'Match the exact standard and test scope to a verified lab',
    status: 'pending',
  },
  {
    title: 'Prepare application',
    detail: 'Compile technical, manufacturing and test documentation',
    status: 'pending',
  },
];
