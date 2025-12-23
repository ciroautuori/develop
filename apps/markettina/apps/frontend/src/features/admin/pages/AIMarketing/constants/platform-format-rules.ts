/**
 * PLATFORM FORMAT RULES - Regole di formattazione per ogni social
 *
 * Definisce lo STILE di scrittura specifico per ogni piattaforma,
 * non solo i limiti caratteri ma anche struttura, tono, emoji usage.
 */

export interface PlatformFormatRule {
  id: string;
  label: string;
  maxChars: number;
  maxHashtags: number;
  maxMentions: number;
  emojiDensity: 'none' | 'low' | 'medium' | 'high';
  lineBreakStyle: 'minimal' | 'paragraphs' | 'spaced';
  structure: {
    hook: boolean;
    body: boolean;
    cta: boolean;
    signature: boolean;
  };
  toneOverride: string | null;
  formatting: {
    bulletPoints: boolean;
    numberedLists: boolean;
    bold: boolean;
    lineBreaksForEmphasis: boolean;
  };
  promptInstructions: string;
  postProcessRules: string[];
}

export const PLATFORM_FORMAT_RULES: Record<string, PlatformFormatRule> = {
  linkedin: {
    id: 'linkedin',
    label: 'LinkedIn',
    maxChars: 3000,
    maxHashtags: 5,
    maxMentions: 3,
    emojiDensity: 'low',
    lineBreakStyle: 'paragraphs',
    structure: {
      hook: true,
      body: true,
      cta: true,
      signature: true,
    },
    toneOverride: null,
    formatting: {
      bulletPoints: true,
      numberedLists: true,
      bold: false,
      lineBreaksForEmphasis: true,
    },
    promptInstructions: `
Scrivi per LinkedIn con tono PROFESSIONALE e autorevole.
STRUTTURA OBBLIGATORIA:
1. HOOK: Prima riga che cattura attenzione (senza emoji iniziale)
2. CORPO: 2-3 paragrafi con insights di valore
3. LISTA: Usa bullet points (✅ o •) per punti chiave
4. CTA: Domanda engaging o call-to-action professionale
5. HASHTAG: Massimo 3-5, rilevanti al settore

STILE:
- Paragrafi brevi (2-3 righe)
- Una riga vuota tra paragrafi
- Emoji moderati (max 3-4 nel post)
- Tono esperto ma accessibile
- Evita slang e abbreviazioni`,
    postProcessRules: [
      'Limita emoji a max 4',
      'Aggiungi riga vuota dopo ogni paragrafo',
      'Hashtag in fondo separati da spazio',
      'Prima lettera maiuscola dopo ogni punto',
    ],
  },

  instagram: {
    id: 'instagram',
    label: 'Instagram',
    maxChars: 2200,
    maxHashtags: 30,
    maxMentions: 10,
    emojiDensity: 'high',
    lineBreakStyle: 'spaced',
    structure: {
      hook: true,
      body: true,
      cta: true,
      signature: false,
    },
    toneOverride: 'casual',
    formatting: {
      bulletPoints: false,
      numberedLists: false,
      bold: false,
      lineBreaksForEmphasis: true,
    },
    promptInstructions: `
Scrivi per Instagram con tono CASUAL e coinvolgente.
STRUTTURA OBBLIGATORIA:
1. HOOK: Emoji + frase catchy che ferma lo scroll
2. CORPO: Storytelling personale o valore immediato
3. CTA: Invita all'interazione (commenta, salva, condividi)
4. HASHTAG: 15-20 rilevanti, mix popolari e di nicchia

STILE:
- Usa MOLTI emoji (ogni 1-2 frasi)
- Line breaks frequenti per leggibilità
- Tono amichevole, come parlassi a un amico
- Domande dirette al pubblico
- Evita formalità eccessive`,
    postProcessRules: [
      'Aggiungi emoji ogni 2-3 frasi',
      'Line break dopo ogni frase',
      'Hashtag separati in blocco finale',
      'Prima emoji nel hook',
    ],
  },

  facebook: {
    id: 'facebook',
    label: 'Facebook',
    maxChars: 63206,
    maxHashtags: 3,
    maxMentions: 5,
    emojiDensity: 'medium',
    lineBreakStyle: 'paragraphs',
    structure: {
      hook: true,
      body: true,
      cta: true,
      signature: false,
    },
    toneOverride: null,
    formatting: {
      bulletPoints: true,
      numberedLists: true,
      bold: false,
      lineBreaksForEmphasis: false,
    },
    promptInstructions: `
Scrivi per Facebook con tono CONVERSAZIONALE e storytelling.
STRUTTURA OBBLIGATORIA:
1. HOOK: Domanda o affermazione che invita alla lettura
2. STORIA: Racconta un'esperienza, un caso, un insight
3. VALORE: Cosa può imparare chi legge
4. CTA: Invita alla discussione nei commenti

STILE:
- Storytelling naturale
- Emoji moderati ma presenti
- Paragrafi di 3-4 righe
- Domande retoriche per engagement
- Tono come se parlassi a una community`,
    postProcessRules: [
      'Max 2-3 hashtag',
      'Domanda finale per engagement',
      'Emoji a inizio e metà post',
    ],
  },

  twitter: {
    id: 'twitter',
    label: 'X (Twitter)',
    maxChars: 280,
    maxHashtags: 2,
    maxMentions: 2,
    emojiDensity: 'low',
    lineBreakStyle: 'minimal',
    structure: {
      hook: true,
      body: false,
      cta: false,
      signature: false,
    },
    toneOverride: null,
    formatting: {
      bulletPoints: false,
      numberedLists: false,
      bold: false,
      lineBreaksForEmphasis: false,
    },
    promptInstructions: `
Scrivi per X (Twitter) con MASSIMA CONCISIONE.
REGOLE FONDAMENTALI:
1. MAX 280 caratteri TOTALI (inclusi hashtag e spazi)
2. Un solo concetto chiaro e memorabile
3. Max 1-2 hashtag (contano nei caratteri!)
4. Emoji solo se aggiunge valore

STILE:
- Diretto e impattante
- No filler words
- Punchline immediata
- Evita "Scopri", "Leggi", preferisci azione diretta`,
    postProcessRules: [
      'Taglia a 280 chars se necessario',
      'Max 2 hashtag',
      'Rimuovi parole superflue',
      'Una frase principale',
    ],
  },

  tiktok: {
    id: 'tiktok',
    label: 'TikTok',
    maxChars: 2200,
    maxHashtags: 5,
    maxMentions: 5,
    emojiDensity: 'high',
    lineBreakStyle: 'minimal',
    structure: {
      hook: true,
      body: false,
      cta: true,
      signature: false,
    },
    toneOverride: 'casual',
    formatting: {
      bulletPoints: false,
      numberedLists: false,
      bold: false,
      lineBreaksForEmphasis: false,
    },
    promptInstructions: `
Scrivi per TikTok caption con tono GIOVANILE e trending.
REGOLE:
1. HOOK: Cattura in 1 secondo (frase shock o curiosità)
2. BREVITÀ: Max 150 caratteri per caption efficace
3. HASHTAG: Mix trending + nicchia
4. CTA: "Salva per dopo" / "Commenta se..."

STILE:
- Ultra-casual, slang accettato
- Emoji trendy
- Reference a trend attuali
- Call-to-action virali`,
    postProcessRules: [
      'Max 150 chars per caption',
      'Hashtag trending first',
      'Emoji trendy (🔥💀✨)',
    ],
  },
};

/**
 * Ottiene le regole di formattazione per una piattaforma
 */
export function getPlatformFormatRule(platformId: string): PlatformFormatRule | null {
  return PLATFORM_FORMAT_RULES[platformId] || null;
}

/**
 * Genera le istruzioni prompt per l'AI in base alla piattaforma
 */
export function getPromptInstructionsForPlatform(platformId: string): string {
  const rule = PLATFORM_FORMAT_RULES[platformId];
  if (!rule) return '';
  return rule.promptInstructions;
}

/**
 * Post-processa il contenuto generato per adattarlo alla piattaforma
 */
export function postProcessContentForPlatform(content: string, platformId: string): string {
  const rule = PLATFORM_FORMAT_RULES[platformId];
  if (!rule) return content;

  let processed = content;

  // Applica limiti caratteri
  if (processed.length > rule.maxChars) {
    processed = processed.slice(0, rule.maxChars - 3) + '...';
  }

  // Gestione emoji density
  if (rule.emojiDensity === 'none') {
    // Rimuovi tutti gli emoji
    processed = processed.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '');
  }

  // Gestione line breaks per piattaforma
  if (rule.lineBreakStyle === 'spaced') {
    // Aggiungi line break dopo ogni punto
    processed = processed.replace(/\. /g, '.\n\n');
  } else if (rule.lineBreakStyle === 'paragraphs') {
    // Assicurati che ci siano paragrafi chiari
    processed = processed.replace(/\n{3,}/g, '\n\n');
  } else if (rule.lineBreakStyle === 'minimal') {
    // Rimuovi line breaks eccessivi
    processed = processed.replace(/\n{2,}/g, '\n');
  }

  return processed.trim();
}

/**
 * Limita gli hashtag secondo le regole della piattaforma
 */
export function limitHashtagsForPlatform(hashtags: string[], platformId: string): string[] {
  const rule = PLATFORM_FORMAT_RULES[platformId];
  if (!rule) return hashtags;
  return hashtags.slice(0, rule.maxHashtags);
}

/**
 * Limita le menzioni secondo le regole della piattaforma
 */
export function limitMentionsForPlatform(mentions: string[], platformId: string): string[] {
  const rule = PLATFORM_FORMAT_RULES[platformId];
  if (!rule) return mentions;
  return mentions.slice(0, rule.maxMentions);
}
