/**
 * BRAND DNA - StudioCentOS Complete Brand Identity
 *
 * Sistema centralizzato per identità brand:
 * - Colori, tipografia, stile visivo
 * - Tone of voice, valori, mission
 * - Target audience e positioning
 * - Keywords SEO e hashtag
 * - Prompt templates per AI
 *
 * @module constants/brand-dna
 */

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface BrandColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
  success: string;
  warning: string;
  error: string;
  gradients: {
    premium: string;
    gold: string;
    dark: string;
    subtle: string;
  };
  palette: {
    gold: ColorShades;
    black: ColorShades;
    white: ColorShades;
  };
}

export interface ColorShades {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;
  600: string;
  700: string;
  800: string;
  900: string;
}

export interface BrandTypography {
  fontFamily: {
    heading: string;
    body: string;
    mono: string;
  };
  fontWeight: {
    light: number;
    regular: number;
    medium: number;
    semibold: number;
    bold: number;
    extrabold: number;
  };
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
    '5xl': string;
  };
}

export interface BrandVoice {
  primary: string;
  style: string;
  emotion: string;
  approach: string;
  characteristics: string[];
  doList: string[];
  dontList: string[];
}

export interface TargetAudience {
  primary: AudienceSegment;
  secondary: AudienceSegment[];
  sectors: string[];
  demographics: Demographics;
  psychographics: Psychographics;
}

export interface AudienceSegment {
  name: string;
  description: string;
  painPoints: string[];
  goals: string[];
  channels: string[];
}

export interface Demographics {
  ageRange: string;
  location: string;
  businessSize: string;
  revenue: string;
  decisionMakers: string[];
}

export interface Psychographics {
  values: string[];
  motivations: string[];
  fears: string[];
  buyingTriggers: string[];
}

export interface BrandMessaging {
  tagline: string;
  valueProposition: string;
  missionStatement: string;
  visionStatement: string;
  elevatorPitch: string;
  keyMessages: string[];
  proofPoints: string[];
}

export interface SEOKeywords {
  primary: string[];
  secondary: string[];
  longTail: string[];
  local: string[];
}

export interface SocialHashtags {
  brand: string[];
  industry: string[];
  local: string[];
  trending: string[];
  campaign: string[];
}

export interface ContentPillars {
  pillars: ContentPillar[];
  contentMix: ContentMixItem[];
}

export interface ContentPillar {
  id: string;
  name: string;
  description: string;
  topics: string[];
  percentage: number;
}

export interface ContentMixItem {
  type: string;
  percentage: number;
  frequency: string;
}

// ============================================================================
// BRAND DNA CONFIGURATION
// ============================================================================

/**
 * StudioCentOS Complete Brand DNA
 */
export const BRAND_DNA = {
  // ============================================
  // IDENTITY
  // ============================================
  identity: {
    name: 'StudioCentOS',
    legalName: 'StudioCentOS S.r.l.',
    founded: 2020,
    location: 'Salerno, Campania, Italia',
    website: 'https://studiocentos.it',
    email: 'info@studiocentos.it',
    industry: 'Software Development & AI Solutions',
  },

  // ============================================
  // COLORS
  // ============================================
  colors: {
    primary: '#D4AF37',      // Oro - Eccellenza, qualità premium
    secondary: '#0A0A0A',    // Nero - Professionalità, eleganza
    accent: '#FAFAFA',       // Bianco - Pulizia, semplicità
    background: '#FFFFFF',
    text: '#1A1A1A',
    success: '#22C55E',
    warning: '#F59E0B',
    error: '#EF4444',

    gradients: {
      premium: 'linear-gradient(135deg, #D4AF37 0%, #0A0A0A 100%)',
      gold: 'linear-gradient(135deg, #D4AF37 0%, #B8960C 100%)',
      dark: 'linear-gradient(180deg, #0A0A0A 0%, #1A1A1A 100%)',
      subtle: 'linear-gradient(135deg, #FAFAFA 0%, #E5E5E5 100%)',
    },

    palette: {
      gold: {
        50: '#FDF9E9',
        100: '#FCF3D3',
        200: '#F9E7A7',
        300: '#F5DA7B',
        400: '#EACC50',
        500: '#D4AF37',
        600: '#B8960C',
        700: '#8C7209',
        800: '#604E06',
        900: '#342A03',
      },
      black: {
        50: '#F5F5F5',
        100: '#E5E5E5',
        200: '#CCCCCC',
        300: '#999999',
        400: '#666666',
        500: '#333333',
        600: '#1A1A1A',
        700: '#0A0A0A',
        800: '#050505',
        900: '#000000',
      },
      white: {
        50: '#FFFFFF',
        100: '#FAFAFA',
        200: '#F5F5F5',
        300: '#F0F0F0',
        400: '#E5E5E5',
        500: '#D9D9D9',
        600: '#CCCCCC',
        700: '#B3B3B3',
        800: '#999999',
        900: '#808080',
      },
    },
  } as BrandColors,

  // ============================================
  // TYPOGRAPHY
  // ============================================
  typography: {
    fontFamily: {
      heading: '"Montserrat", -apple-system, BlinkMacSystemFont, sans-serif',
      body: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
      mono: '"JetBrains Mono", "Fira Code", monospace',
    },
    fontWeight: {
      light: 300,
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
    fontSize: {
      xs: '0.75rem',     // 12px
      sm: '0.875rem',    // 14px
      base: '1rem',      // 16px
      lg: '1.125rem',    // 18px
      xl: '1.25rem',     // 20px
      '2xl': '1.5rem',   // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem',  // 36px
      '5xl': '3rem',     // 48px
    },
  } as BrandTypography,

  // ============================================
  // VOICE & TONE
  // ============================================
  voice: {
    primary: 'Professionale ma accessibile',
    style: 'Diretto e concreto',
    emotion: 'Positivo ma realistico',
    approach: 'Empatico con le sfide delle PMI italiane',

    characteristics: [
      'Competente senza essere arrogante',
      'Chiaro senza essere semplicistico',
      'Amichevole senza essere informale',
      'Innovativo senza essere intimidatorio',
      'Locale con visione internazionale',
    ],

    doList: [
      'Usare esempi concreti e numeri reali',
      'Parlare dei benefici, non solo delle feature',
      'Rispondere alle obiezioni proattivamente',
      'Usare il "tu" per creare vicinanza',
      'Citare casi di successo locali',
      'Spiegare i tecnicismi quando necessario',
      'Essere trasparenti su tempi e costi',
    ],

    dontList: [
      'Usare gergo tecnico non necessario',
      'Fare promesse vaghe o esagerate',
      'Usare anglicismi quando esiste l\'equivalente italiano',
      'Essere paternalistici o presuntuosi',
      'Ignorare le specificità del mercato italiano',
      'Usare "Disruptive", "Cutting-edge", "Best-in-class", "Sinergia"',
    ],
  } as BrandVoice,

  // ============================================
  // VALUES
  // ============================================
  values: [
    {
      name: 'Innovazione Accessibile',
      description: 'Tecnologie enterprise a portata di PMI',
      icon: '💡',
    },
    {
      name: 'Affidabilità',
      description: 'Soluzioni robuste e supporto continuo',
      icon: '🛡️',
    },
    {
      name: 'Trasparenza',
      description: 'Prezzi chiari, comunicazione diretta',
      icon: '🔍',
    },
    {
      name: 'Risultati',
      description: 'Focus su ROI misurabile per i clienti',
      icon: '📈',
    },
    {
      name: 'Italianità',
      description: 'Comprensione profonda del mercato locale',
      icon: '🇮🇹',
    },
  ],

  // ============================================
  // TARGET AUDIENCE
  // ============================================
  targetAudience: {
    primary: {
      name: 'PMI Campania',
      description: 'Piccole e medie imprese della Campania (1-50 dipendenti)',
      painPoints: [
        'Mancanza di competenze digitali interne',
        'Budget limitato per tecnologia',
        'Difficoltà a trovare fornitori affidabili',
        'Paura di progetti IT fallimentari',
        'Concorrenza di grandi catene/e-commerce',
      ],
      goals: [
        'Aumentare efficienza operativa',
        'Raggiungere nuovi clienti online',
        'Automatizzare processi ripetitivi',
        'Competere con aziende più grandi',
        'Digitalizzare senza stravolgere',
      ],
      channels: ['LinkedIn', 'Facebook', 'Google', 'Passaparola', 'Eventi locali'],
    },

    secondary: [
      {
        name: 'Professionisti',
        description: 'Avvocati, commercialisti, medici, consulenti',
        painPoints: [
          'Gestione clienti inefficiente',
          'Comunicazione frammentata',
          'Tempo perso in attività ripetitive',
        ],
        goals: [
          'Automatizzare la gestione clienti',
          'Migliorare la comunicazione',
          'Liberare tempo per attività di valore',
        ],
        channels: ['LinkedIn', 'Google', 'Ordini professionali'],
      },
      {
        name: 'Attività Commerciali',
        description: 'Ristoranti, hotel, negozi, attività locali',
        painPoints: [
          'Gestione prenotazioni manuale',
          'Poca visibilità online',
          'Difficoltà con social media',
        ],
        goals: [
          'Aumentare prenotazioni',
          'Migliorare recensioni online',
          'Gestire social in modo efficiente',
        ],
        channels: ['Instagram', 'Facebook', 'Google Business', 'TripAdvisor'],
      },
    ],

    sectors: [
      'Ristorazione e ospitalità',
      'Studi professionali (legali, fiscali, medici)',
      'Commercio al dettaglio',
      'Manifatturiero locale',
      'Servizi alle imprese',
      'Turismo e accoglienza',
    ],

    demographics: {
      ageRange: '35-60 anni',
      location: 'Campania, Sud Italia',
      businessSize: '1-50 dipendenti',
      revenue: '€100K - €5M annui',
      decisionMakers: ['Titolari', 'Amministratori', 'Responsabili IT'],
    },

    psychographics: {
      values: ['Tradizione', 'Famiglia', 'Qualità', 'Rapporti personali'],
      motivations: ['Crescita aziendale', 'Competitività', 'Legacy', 'Innovazione graduale'],
      fears: ['Fallimento progetti IT', 'Sprecare budget', 'Dipendenza da fornitori', 'Obsolescenza'],
      buyingTriggers: ['Referral di fiducia', 'Casi di successo locali', 'Demo pratica', 'Prezzo chiaro'],
    },
  } as TargetAudience,

  // ============================================
  // MESSAGING
  // ============================================
  messaging: {
    tagline: 'Tecnologia enterprise per la tua PMI, senza la complessità enterprise',

    valueProposition: 'Aiutiamo le PMI italiane a competere con le grandi aziende grazie a soluzioni AI e software su misura, con supporto in italiano e risultati misurabili in 30 giorni.',

    missionStatement: 'Rendere accessibili le tecnologie più avanzate (AI, automazione, cloud) alle piccole e medie imprese italiane, eliminando la complessità tecnica e offrendo soluzioni pronte all\'uso.',

    visionStatement: 'Diventare il partner tecnologico di riferimento per le PMI del Sud Italia, guidandole nella trasformazione digitale con soluzioni concrete e misurabili.',

    elevatorPitch: 'StudioCentOS è la software house che porta l\'intelligenza artificiale nelle PMI italiane. Sviluppiamo soluzioni su misura che automatizzano il marketing, ottimizzano i processi e aumentano le vendite. I nostri clienti vedono risultati in 30 giorni, con supporto in italiano e prezzi trasparenti.',

    keyMessages: [
      'AI accessibile per ogni PMI italiana',
      'Risultati misurabili in 30 giorni',
      'Supporto in italiano, da persone vere',
      'Prezzi trasparenti, nessuna sorpresa',
      'Soluzioni pronte all\'uso, non progetti infiniti',
    ],

    proofPoints: [
      '100+ PMI italiane digitalizzate',
      '30% risparmio medio sui costi operativi',
      '50% aumento lead generation',
      '4.9/5 valutazione clienti',
      'Team 100% italiano',
    ],
  } as BrandMessaging,

  // ============================================
  // SEO KEYWORDS
  // ============================================
  seoKeywords: {
    primary: [
      'sviluppo software Salerno',
      'software house Campania',
      'soluzioni AI PMI',
      'intelligenza artificiale business',
      'automazione marketing PMI',
    ],

    secondary: [
      'agenzia web Napoli',
      'sviluppo app mobile Campania',
      'consulenza digitale PMI',
      'chatbot aziendale',
      'CRM personalizzato',
    ],

    longTail: [
      'come automatizzare marketing PMI',
      'intelligenza artificiale per ristoranti',
      'software gestionale studi legali Salerno',
      'sviluppo e-commerce Campania',
      'digitalizzazione aziende Sud Italia',
    ],

    local: [
      'sviluppo software Salerno',
      'web agency Napoli',
      'app mobile Campania',
      'consulente IT Avellino',
      'digitalizzazione Benevento',
    ],
  } as SEOKeywords,

  // ============================================
  // SOCIAL HASHTAGS
  // ============================================
  hashtags: {
    brand: [
      '#StudioCentOS',
      '#AIperPMI',
      '#DigitalizzazionePMI',
      '#TechForBusiness',
    ],

    industry: [
      '#SviluppoSoftware',
      '#IntelligenzaArtificiale',
      '#Automazione',
      '#DigitalTransformation',
      '#MarketingAutomation',
      '#CloudComputing',
    ],

    local: [
      '#TechSalerno',
      '#InnovazioneItalia',
      '#PMIdigitale',
      '#SudInnovativo',
      '#CampaniaDigitale',
      '#MadeInItaly',
    ],

    trending: [
      '#AI',
      '#ChatGPT',
      '#Startup',
      '#Business',
      '#Impresa',
      '#Innovazione',
    ],

    campaign: [
      '#TrasformazioneDigitale',
      '#PMI40',
      '#FuturoDigitale',
      '#InnovareOggi',
    ],
  } as SocialHashtags,

  // ============================================
  // CONTENT PILLARS
  // ============================================
  contentPillars: {
    pillars: [
      {
        id: 'tech_tips',
        name: 'Tech Tips',
        description: 'Consigli pratici per la digitalizzazione delle PMI',
        topics: [
          'Automazione processi',
          'Tool e software consigliati',
          'Best practice digitali',
          'Risparmio tempo e costi',
        ],
        percentage: 30,
      },
      {
        id: 'case_studies',
        name: 'Case Studies',
        description: 'Storie di successo dei nostri clienti',
        topics: [
          'Risultati ottenuti',
          'Sfide superate',
          'ROI misurabili',
          'Testimonianze',
        ],
        percentage: 25,
      },
      {
        id: 'ai_explained',
        name: 'AI Explained',
        description: 'Intelligenza artificiale spiegata semplice',
        topics: [
          'Cos\'è l\'AI e come usarla',
          'Casi d\'uso per PMI',
          'Miti da sfatare',
          'Trend e novità',
        ],
        percentage: 25,
      },
      {
        id: 'local_business',
        name: 'Local Business',
        description: 'Focus sull\'economia e business locale',
        topics: [
          'Storie di imprenditori locali',
          'Eventi e networking',
          'Opportunità del territorio',
          'Collaborazioni',
        ],
        percentage: 20,
      },
    ],

    contentMix: [
      { type: 'Educational', percentage: 40, frequency: '3x/settimana' },
      { type: 'Promotional', percentage: 20, frequency: '1x/settimana' },
      { type: 'Engagement', percentage: 25, frequency: '2x/settimana' },
      { type: 'Behind the Scenes', percentage: 15, frequency: '1x/settimana' },
    ],
  } as ContentPillars,

  // ============================================
  // VISUAL STYLE
  // ============================================
  visualStyle: {
    imageStyle: {
      primary: 'professional, clean, modern, minimal',
      secondary: 'warm, approachable, Italian',
      avoid: 'cold, corporate, generic stock',
    },

    photography: {
      subjects: ['Team al lavoro', 'Clienti soddisfatti', 'Uffici moderni', 'Tecnologia'],
      style: 'Natural lighting, authentic moments, local settings',
      mood: 'Confident, innovative, approachable',
    },

    graphics: {
      style: 'Clean lines, minimal, data-driven',
      icons: 'Outlined or filled, consistent weight',
      charts: 'Simple, brand colors, clear labels',
    },

    video: {
      style: 'Professional but not corporate',
      pacing: 'Dynamic, attention-grabbing first 3 seconds',
      captions: 'Always include, brand fonts',
    },
  },

  // ============================================
  // COMPETITORS
  // ============================================
  competitors: {
    direct: [
      {
        name: 'Agenzie web locali',
        weakness: 'Solo siti web, no AI, no automazione',
        ourAdvantage: 'Offriamo soluzioni complete AI-powered',
      },
      {
        name: 'Grandi software house',
        weakness: 'Troppo costose, tempi lunghi, poco flessibili',
        ourAdvantage: 'Prezzi PMI, tempi rapidi, approccio personalizzato',
      },
    ],
    indirect: [
      {
        name: 'Freelancer',
        weakness: 'Meno affidabilità, nessun supporto continuativo',
        ourAdvantage: 'Team strutturato, supporto garantito',
      },
      {
        name: 'SaaS internazionali',
        weakness: 'Non localizzati, supporto in inglese',
        ourAdvantage: 'Soluzioni su misura, supporto in italiano',
      },
    ],
  },
} as const;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Ottiene il prompt AI con il Brand DNA completo
 */
export function getBrandDNAPrompt(): string {
  return `
BRAND DNA - STUDIOCENTOS

IDENTITÀ:
- Nome: ${BRAND_DNA.identity.name}
- Settore: ${BRAND_DNA.identity.industry}
- Location: ${BRAND_DNA.identity.location}

MISSION: ${BRAND_DNA.messaging.missionStatement}

VALUE PROPOSITION: ${BRAND_DNA.messaging.valueProposition}

TONE OF VOICE:
- Stile: ${BRAND_DNA.voice.primary}
- Approccio: ${BRAND_DNA.voice.approach}
- Caratteristiche: ${BRAND_DNA.voice.characteristics.join(', ')}

DA FARE:
${BRAND_DNA.voice.doList.map(item => `• ${item}`).join('\n')}

DA EVITARE:
${BRAND_DNA.voice.dontList.map(item => `• ${item}`).join('\n')}

TARGET:
- Primario: ${BRAND_DNA.targetAudience.primary.name}
- Settori: ${BRAND_DNA.targetAudience.sectors.join(', ')}

VALORI:
${BRAND_DNA.values.map(v => `${v.icon} ${v.name}: ${v.description}`).join('\n')}

HASHTAG BRAND: ${BRAND_DNA.hashtags.brand.join(' ')}
`.trim();
}

/**
 * Ottiene i colori brand per CSS/Tailwind
 */
export function getBrandColors() {
  return BRAND_DNA.colors;
}

/**
 * Ottiene gli hashtag per una categoria
 */
export function getHashtags(category: keyof typeof BRAND_DNA.hashtags, limit: number = 10): string[] {
  return BRAND_DNA.hashtags[category].slice(0, limit);
}

/**
 * Ottiene tutti gli hashtag combinati
 */
export function getAllHashtags(limit: number = 20): string[] {
  const all = [
    ...BRAND_DNA.hashtags.brand,
    ...BRAND_DNA.hashtags.industry,
    ...BRAND_DNA.hashtags.local,
  ];
  return [...new Set(all)].slice(0, limit);
}

/**
 * Ottiene il content pillar per ID
 */
export function getContentPillar(id: string) {
  return BRAND_DNA.contentPillars.pillars.find(p => p.id === id);
}

/**
 * Genera la firma per i post
 */
export function getBrandSignature(platform: 'linkedin' | 'instagram' | 'twitter' | 'facebook'): string {
  const signatures = {
    linkedin: `\n\n---\n${BRAND_DNA.identity.name} | ${BRAND_DNA.messaging.tagline}\n${BRAND_DNA.hashtags.brand.slice(0, 3).join(' ')}`,
    instagram: `\n\n.\n.\n.\n${BRAND_DNA.hashtags.brand.join(' ')} ${BRAND_DNA.hashtags.local.slice(0, 3).join(' ')}`,
    twitter: `\n\n${BRAND_DNA.hashtags.brand.slice(0, 2).join(' ')}`,
    facebook: `\n\n${BRAND_DNA.identity.name} - ${BRAND_DNA.messaging.tagline}`,
  };
  return signatures[platform] || '';
}

/**
 * Valida se un testo rispetta il brand voice
 */
export function validateBrandVoice(text: string): { valid: boolean; issues: string[] } {
  const issues: string[] = [];
  const lowerText = text.toLowerCase();

  // Check parole da evitare
  const wordsToAvoid = ['disruptive', 'cutting-edge', 'best-in-class', 'sinergia', 'synergy'];
  for (const word of wordsToAvoid) {
    if (lowerText.includes(word)) {
      issues.push(`Evita la parola "${word}"`);
    }
  }

  // Check lunghezza frasi (max 25 parole per frase)
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  for (const sentence of sentences) {
    const wordCount = sentence.trim().split(/\s+/).length;
    if (wordCount > 30) {
      issues.push('Alcune frasi sono troppo lunghe (max 25-30 parole)');
      break;
    }
  }

  return {
    valid: issues.length === 0,
    issues,
  };
}

export default BRAND_DNA;
