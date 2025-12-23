/**
 * QUICK TEMPLATES - Sistema Completo Marketing Hub
 *
 * Struttura professionale: HOOK → BODY → CTA → HASHTAG
 * Integrazione Brand DNA StudioCentOS
 *
 * @module constants/quick-templates
 */

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export type PostType =
  | 'lancio_prodotto'
  | 'tip_giorno'
  | 'caso_successo'
  | 'trend_settore'
  | 'offerta_speciale'
  | 'ai_business'
  | 'behind_scenes'
  | 'educational'
  | 'engagement'
  | 'testimonial'
  | 'tutorial'
  | 'annuncio'
  | 'promo'
  | 'quote';

export type ContentCategory = 'social' | 'video' | 'email' | 'story' | 'carousel';

export interface QuickTemplate {
  id: string;
  label: string;
  value: string;
  category: ContentCategory;
  postType: PostType;
  icon: string;
  structure: PostStructure;
  aiPrompt: string;
  platforms: SocialPlatform[];
  hashtags: string[];
  ctaOptions: string[];
}

export interface PostStructure {
  hook: string;
  bodyPoints: number;
  ctaRequired: boolean;
  hashtagCount: number;
  emojiLevel: 'none' | 'low' | 'medium' | 'high';
}

export type SocialPlatform =
  | 'instagram'
  | 'facebook'
  | 'linkedin'
  | 'twitter'
  | 'tiktok'
  | 'threads'
  | 'youtube'
  | 'pinterest';

// ============================================================================
// BRAND DNA - STUDIOCENTOS CORE VALUES
// ============================================================================

export const BRAND_DNA = {
  name: 'StudioCentOS',
  tagline: 'Tecnologia enterprise per la tua PMI, senza la complessità enterprise',
  mission: 'Rendere accessibili le tecnologie più avanzate (AI, automazione, cloud) alle piccole e medie imprese italiane',

  colors: {
    primary: '#D4AF37',    // Oro - Eccellenza
    secondary: '#0A0A0A',  // Nero - Professionalità
    accent: '#FAFAFA',     // Bianco - Pulizia
    gradient: 'linear-gradient(135deg, #D4AF37 0%, #0A0A0A 100%)',
  },

  toneOfVoice: {
    primary: 'professionale ma accessibile',
    style: 'diretto e concreto',
    emotion: 'positivo ma realistico',
    approach: 'empatico con le sfide PMI',
  },

  values: [
    'Innovazione Accessibile',
    'Affidabilità',
    'Trasparenza',
    'Risultati Misurabili',
    'Italianità',
  ],

  targetAudience: {
    primary: 'PMI Campania (1-50 dipendenti)',
    secondary: ['Professionisti', 'Attività commerciali'],
    sectors: ['Ristorazione', 'Studi professionali', 'Commercio', 'Manifatturiero'],
  },

  hashtags: {
    brand: ['#StudioCentOS', '#AIperPMI', '#DigitalizzazionePMI'],
    local: ['#TechSalerno', '#InnovazioneItalia', '#PMIdigitale'],
    industry: ['#SviluppoSoftware', '#Automazione', '#CloudItalia'],
  },

  wordsToAvoid: ['Disruptive', 'Cutting-edge', 'Best-in-class', 'Sinergia'],

  contentPillars: ['Tech Tips', 'Case Studies', 'AI Explained', 'Local Business'],
} as const;

// ============================================================================
// SOCIAL QUICK TEMPLATES - Struttura HOOK → BODY → CTA → HASHTAG
// ============================================================================

export const SOCIAL_QUICK_TEMPLATES: QuickTemplate[] = [
  // LANCIO PRODOTTO
  {
    id: 'lancio_prodotto',
    label: '🚀 Lancio Prodotto',
    value: 'Lancio di un nuovo prodotto/servizio digitale',
    category: 'social',
    postType: 'lancio_prodotto',
    icon: '🚀',
    structure: {
      hook: 'Domanda provocatoria o annuncio impattante',
      bodyPoints: 3,
      ctaRequired: true,
      hashtagCount: 8,
      emojiLevel: 'medium',
    },
    aiPrompt: `
RUOLO: Sei il content creator di StudioCentOS, software house italiana specializzata in AI per PMI.

BRAND DNA:
- Tono: ${BRAND_DNA.toneOfVoice.primary}
- Stile: ${BRAND_DNA.toneOfVoice.style}
- Target: PMI italiane, professionisti, attività commerciali

STRUTTURA POST LANCIO PRODOTTO:

🔥 HOOK (Prima riga - FERMA LO SCROLL):
[Domanda provocatoria o statistica shock che evidenzia il problema risolto]

📝 BODY (3-4 punti chiave):
• Problema che risolve
• Beneficio principale per la PMI
• Differenziatore vs soluzioni esistenti
• Risultato atteso (numero o percentuale)

✨ CTA (Call-to-Action):
[Invito all'azione chiaro: prenota demo, richiedi info, scopri di più]

🏷️ HASHTAG:
${BRAND_DNA.hashtags.brand.join(' ')} + hashtag specifici del prodotto

REGOLE:
- Parla dei benefici, non delle feature
- Usa numeri e dati concreti
- Evita tecnicismi eccessivi
- Mantieni il tono ${BRAND_DNA.toneOfVoice.primary}
`,
    platforms: ['instagram', 'facebook', 'linkedin', 'threads'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#NuovoServizio', '#InnovazionePMI', '#TechItalia'],
    ctaOptions: [
      'Prenota una demo gratuita →',
      'Scopri come può aiutarti →',
      'Richiedi info in DM 📩',
      'Link in bio per saperne di più',
    ],
  },

  // TIP DEL GIORNO
  {
    id: 'tip_giorno',
    label: '💡 Tip del Giorno',
    value: 'Consiglio pratico per PMI sulla digitalizzazione',
    category: 'social',
    postType: 'tip_giorno',
    icon: '💡',
    structure: {
      hook: 'Problema comune + soluzione immediata',
      bodyPoints: 3,
      ctaRequired: true,
      hashtagCount: 10,
      emojiLevel: 'high',
    },
    aiPrompt: `
RUOLO: Sei l'esperto tech di StudioCentOS che aiuta le PMI italiane.

BRAND DNA:
- Tono: ${BRAND_DNA.toneOfVoice.primary}
- Mission: ${BRAND_DNA.mission}

STRUTTURA TIP DEL GIORNO:

💡 HOOK:
"Sapevi che [problema comune]? Ecco come risolverlo in [tempo]:"

📝 BODY (Passi pratici):
1️⃣ [Primo step semplice]
2️⃣ [Secondo step]
3️⃣ [Terzo step con risultato]

💰 BONUS/RISULTATO:
[Beneficio concreto: tempo risparmiato, costi ridotti, efficienza aumentata]

💬 CTA:
"Quale tip vorresti vedere la prossima volta? 👇"

🏷️ HASHTAG:
${BRAND_DNA.hashtags.brand.join(' ')} #TechTips #ConsigliPMI

REGOLE:
- Consigli PRATICI e IMMEDIATI
- Nessun gergo tecnico inutile
- Focus su risparmio tempo/costi
- Incoraggia il salvataggio del post
`,
    platforms: ['instagram', 'linkedin', 'twitter', 'threads'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#TechTips', '#ConsigliPMI', '#Produttività', '#BusinessTips'],
    ctaOptions: [
      'Salva questo post per dopo 📌',
      'Quale tip vuoi vedere? 👇',
      'Condividi con chi ne ha bisogno',
      'Seguici per altri tip quotidiani',
    ],
  },

  // CASO DI SUCCESSO
  {
    id: 'caso_successo',
    label: '🌟 Caso di Successo',
    value: 'Storia di successo di un cliente soddisfatto',
    category: 'social',
    postType: 'caso_successo',
    icon: '🌟',
    structure: {
      hook: 'Risultato numerico impressionante',
      bodyPoints: 4,
      ctaRequired: true,
      hashtagCount: 8,
      emojiLevel: 'medium',
    },
    aiPrompt: `
RUOLO: Sei lo storyteller di StudioCentOS che racconta successi reali.

BRAND DNA:
- Valori: ${BRAND_DNA.values.join(', ')}
- Target: ${BRAND_DNA.targetAudience.primary}

STRUTTURA CASO DI SUCCESSO:

🏆 HOOK:
"[Nome cliente o settore] ha ottenuto [risultato numerico] in [tempo]"

📊 SITUAZIONE PRIMA:
• Problema principale
• Impatto sul business
• Tentativi falliti precedenti

🚀 SOLUZIONE:
• Cosa abbiamo implementato
• Come lo abbiamo fatto
• Tempistiche

📈 RISULTATI:
• +X% [metrica principale]
• €X risparmiati
• [Ore/tempo] recuperato

💬 TESTIMONIANZA:
"[Citazione diretta del cliente]"

🎯 CTA:
"Vuoi risultati simili? Parliamone →"

REGOLE:
- Dati REALI e verificabili
- Nomi o settori specifici (con permesso)
- Storytelling emotivo ma professionale
- Focus su ROI misurabile
`,
    platforms: ['linkedin', 'facebook', 'instagram'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#CaseStudy', '#Successo', '#ROI', '#Testimonianza'],
    ctaOptions: [
      'Vuoi risultati simili? Scrivici →',
      'Prenota una consulenza gratuita',
      'Scopri come possiamo aiutarti',
      'La tua storia potrebbe essere la prossima',
    ],
  },

  // TREND DEL SETTORE
  {
    id: 'trend_settore',
    label: '📈 Trend del Settore',
    value: 'Analisi trend tecnologici per il business',
    category: 'social',
    postType: 'trend_settore',
    icon: '📈',
    structure: {
      hook: 'Statistica o previsione impattante',
      bodyPoints: 4,
      ctaRequired: true,
      hashtagCount: 10,
      emojiLevel: 'low',
    },
    aiPrompt: `
RUOLO: Sei l'analista tech di StudioCentOS, esperto di trend digitali.

BRAND DNA:
- Tono: autorevole ma accessibile
- Pillars: ${BRAND_DNA.contentPillars.join(', ')}

STRUTTURA TREND ANALYSIS:

📊 HOOK:
"Il [X]% delle PMI italiane [statistica rilevante]. Ecco cosa sta cambiando:"

🔍 IL TREND:
• Cosa sta accadendo nel settore
• Perché ora è importante
• Chi sta già adottando

💡 IMPATTO SULLE PMI:
• Opportunità immediate
• Rischi del non adottare
• Timeline consigliata

🛠️ COME PREPARARSI:
1. [Azione pratica 1]
2. [Azione pratica 2]
3. [Azione pratica 3]

🎯 CTA:
"La tua azienda è pronta? Confrontati con noi →"

REGOLE:
- Dati da fonti autorevoli
- Focus su applicabilità per PMI
- Evita allarmismi, proponi soluzioni
- Tono thought leadership
`,
    platforms: ['linkedin', 'twitter', 'threads'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#Trend2025', '#DigitalTransformation', '#FutureOfWork', '#TechTrends'],
    ctaOptions: [
      'Sei pronto per questo trend?',
      'Condividi la tua opinione 👇',
      'Scopri come prepararti →',
      'Seguici per restare aggiornato',
    ],
  },

  // OFFERTA SPECIALE
  {
    id: 'offerta_speciale',
    label: '🎯 Offerta Speciale',
    value: 'Promozione limitata sui servizi digitali',
    category: 'social',
    postType: 'offerta_speciale',
    icon: '🎯',
    structure: {
      hook: 'Urgenza + valore dell\'offerta',
      bodyPoints: 3,
      ctaRequired: true,
      hashtagCount: 6,
      emojiLevel: 'high',
    },
    aiPrompt: `
RUOLO: Sei il marketing manager di StudioCentOS.

BRAND DNA:
- Valori: Trasparenza nei prezzi
- Stile: ${BRAND_DNA.toneOfVoice.style}

STRUTTURA OFFERTA SPECIALE:

🔥 HOOK:
"[SCADENZA] Solo X giorni per [beneficio] a [condizione speciale]"

💰 L'OFFERTA:
• Cosa include
• Valore normale vs prezzo promo
• Risparmio in € o %

✅ PERFETTO PER:
• [Target 1]
• [Target 2]
• [Target 3]

⏰ URGENZA:
• Scadenza precisa
• Posti limitati / Quantità limitata
• Motivo della promozione

🎯 CTA:
"Blocca il prezzo ORA → [link/azione]"

REGOLE:
- Offerta VERA con scadenza REALE
- Nessun inganno o false scarsità
- Valore chiaro e trasparente
- CTA diretto e urgente
`,
    platforms: ['instagram', 'facebook', 'threads'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#Offerta', '#Promo', '#LimitedTime', '#Risparmio'],
    ctaOptions: [
      'Blocca il prezzo ORA →',
      'Scrivi "INFO" in DM 📩',
      'Link in bio per prenotare',
      'Solo X posti disponibili',
    ],
  },

  // AI PER BUSINESS
  {
    id: 'ai_business',
    label: '🤖 AI per Business',
    value: 'Come l\'intelligenza artificiale trasforma il business',
    category: 'social',
    postType: 'ai_business',
    icon: '🤖',
    structure: {
      hook: 'Caso d\'uso AI sorprendente',
      bodyPoints: 4,
      ctaRequired: true,
      hashtagCount: 10,
      emojiLevel: 'medium',
    },
    aiPrompt: `
RUOLO: Sei l'esperto AI di StudioCentOS che demistifica l'intelligenza artificiale.

BRAND DNA:
- Mission: ${BRAND_DNA.mission}
- Pillar: AI Explained

STRUTTURA AI PER BUSINESS:

🤖 HOOK:
"L'AI può [azione sorprendente] per la tua PMI. Ecco come:"

❌ MITO DA SFATARE:
"Molti pensano che l'AI sia [pregiudizio comune]. In realtà..."

✅ LA REALTÀ:
• Cosa può fare OGGI l'AI per le PMI
• Costi reali (accessibili)
• Tempistiche di implementazione

💡 ESEMPI PRATICI:
1. [Caso d'uso 1 - settore specifico]
2. [Caso d'uso 2 - settore specifico]
3. [Caso d'uso 3 - settore specifico]

📊 RISULTATI TIPICI:
• [Metrica 1]
• [Metrica 2]

🎯 CTA:
"Vuoi scoprire cosa può fare l'AI per te? →"

REGOLE:
- Linguaggio semplice, zero tecnicismi
- Esempi concreti per PMI italiane
- Onestà su limiti e potenzialità
- Focus su ROI misurabile
`,
    platforms: ['linkedin', 'instagram', 'facebook', 'threads'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#AI', '#IntelligenzaArtificiale', '#AIforBusiness', '#Automazione'],
    ctaOptions: [
      'Scopri cosa può fare l\'AI per te →',
      'Prenota una demo gratuita',
      'Quale attività vorresti automatizzare? 👇',
      'Seguici per altri contenuti AI',
    ],
  },

  // BEHIND THE SCENES
  {
    id: 'behind_scenes',
    label: '🎬 Behind the Scenes',
    value: 'Dietro le quinte del nostro lavoro',
    category: 'social',
    postType: 'behind_scenes',
    icon: '🎬',
    structure: {
      hook: 'Curiosità o momento autentico',
      bodyPoints: 2,
      ctaRequired: true,
      hashtagCount: 8,
      emojiLevel: 'high',
    },
    aiPrompt: `
RUOLO: Sei il community manager di StudioCentOS che mostra il lato umano.

BRAND DNA:
- Valori: ${BRAND_DNA.values.join(', ')}
- Tono: autentico e relatable

STRUTTURA BEHIND THE SCENES:

📸 HOOK:
"Cosa succede quando [momento autentico del lavoro]?"

💼 IL CONTESTO:
• Cosa stavamo facendo
• La sfida/il momento
• Il team coinvolto

😊 IL LATO UMANO:
• Emozione del momento
• Cosa abbiamo imparato
• Perché lo condividiamo

🎯 CTA:
"Raccontaci il tuo behind the scenes! 👇"

REGOLE:
- Autenticità sopra tutto
- Mostra le persone, non solo il prodotto
- Storytelling personale
- Invita alla conversazione
`,
    platforms: ['instagram', 'threads', 'tiktok'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#BehindTheScenes', '#TeamWork', '#AgencyLife', '#DietroLeQuinte'],
    ctaOptions: [
      'Cosa vorresti vedere del nostro lavoro?',
      'Anche tu hai momenti così? 👇',
      'Seguici per altri backstage',
      'Tag un collega che capisce 😄',
    ],
  },

  // EDUCATIONAL
  {
    id: 'educational',
    label: '📚 Educational',
    value: 'Contenuto formativo e informativo',
    category: 'social',
    postType: 'educational',
    icon: '📚',
    structure: {
      hook: 'Domanda comune o problema diffuso',
      bodyPoints: 5,
      ctaRequired: true,
      hashtagCount: 12,
      emojiLevel: 'medium',
    },
    aiPrompt: `
RUOLO: Sei l'educator di StudioCentOS che semplifica la tecnologia.

BRAND DNA:
- Mission: ${BRAND_DNA.mission}
- Tono: ${BRAND_DNA.toneOfVoice.primary}

STRUTTURA EDUCATIONAL:

❓ HOOK:
"[Domanda comune] Ecco la risposta completa:"

📖 SPIEGAZIONE:
• Cos'è [concetto]
• Perché è importante
• A chi serve

📝 GUIDA PRATICA:
1️⃣ [Step 1]
2️⃣ [Step 2]
3️⃣ [Step 3]
4️⃣ [Step 4]
5️⃣ [Step 5]

⚠️ ERRORI COMUNI:
• [Errore 1 da evitare]
• [Errore 2 da evitare]

💡 PRO TIP:
[Consiglio avanzato per chi vuole di più]

🎯 CTA:
"Salva questo post e condividilo con chi ne ha bisogno 📌"

REGOLE:
- Spiegazioni semplici e chiare
- Esempi concreti
- Struttura scannerizzabile
- Valore educativo genuino
`,
    platforms: ['instagram', 'linkedin', 'threads', 'pinterest'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#Educational', '#Formazione', '#Guide', '#HowTo', '#Impara'],
    ctaOptions: [
      'Salva per dopo 📌',
      'Quale argomento vuoi approfondire?',
      'Condividi con chi può trovarlo utile',
      'Seguici per imparare qualcosa ogni giorno',
    ],
  },

  // ENGAGEMENT
  {
    id: 'engagement',
    label: '💬 Engagement',
    value: 'Post per stimolare interazione',
    category: 'social',
    postType: 'engagement',
    icon: '💬',
    structure: {
      hook: 'Domanda diretta o sondaggio',
      bodyPoints: 1,
      ctaRequired: true,
      hashtagCount: 5,
      emojiLevel: 'high',
    },
    aiPrompt: `
RUOLO: Sei il community builder di StudioCentOS.

BRAND DNA:
- Tono: conversazionale e inclusivo
- Target: ${BRAND_DNA.targetAudience.primary}

STRUTTURA ENGAGEMENT:

🎤 HOOK:
"[Domanda provocatoria o sondaggio]"

💭 CONTESTO (breve):
[1-2 frasi che spiegano perché chiediamo]

🗳️ OPZIONI (se sondaggio):
A) [Opzione 1]
B) [Opzione 2]
C) [Altra risposta nei commenti]

🎯 CTA:
"Commenta con la tua risposta! 👇"

REGOLE:
- Domanda genuina, non retorica
- Rispondere a TUTTI i commenti
- Creare discussione, non polemica
- Valorizzare le risposte ricevute
`,
    platforms: ['instagram', 'linkedin', 'twitter', 'threads'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#Community', '#VostraOpinione', '#Discussione'],
    ctaOptions: [
      'Rispondi nei commenti! 👇',
      'A o B? Dicci la tua!',
      'Tag chi la pensa come te',
      'Condividi la tua esperienza',
    ],
  },

  // TESTIMONIAL
  {
    id: 'testimonial',
    label: '⭐ Testimonial',
    value: 'Recensione o feedback cliente',
    category: 'social',
    postType: 'testimonial',
    icon: '⭐',
    structure: {
      hook: 'Citazione impattante del cliente',
      bodyPoints: 2,
      ctaRequired: true,
      hashtagCount: 6,
      emojiLevel: 'low',
    },
    aiPrompt: `
RUOLO: Sei il PR manager di StudioCentOS che condivide successi.

BRAND DNA:
- Valori: Affidabilità, Risultati
- Stile: professionale ed empatico

STRUTTURA TESTIMONIAL:

⭐ HOOK:
"[Citazione diretta più impattante del cliente]"

👤 CHI È:
• Nome/Ruolo/Azienda
• Settore
• Sfida affrontata

📈 RISULTATI:
• [Metrica principale]
• [Beneficio tangibile]

💬 CITAZIONE COMPLETA:
"[Testimonianza estesa]"

🎯 CTA:
"La prossima recensione potrebbe essere la tua →"

REGOLE:
- Testimonianza REALE e verificabile
- Permesso del cliente ottenuto
- Numeri e risultati concreti
- Gratitudine genuina
`,
    platforms: ['linkedin', 'instagram', 'facebook', 'threads'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#Testimonial', '#Recensioni', '#ClientiSoddisfatti', '#Successo'],
    ctaOptions: [
      'Vuoi risultati simili? Contattaci →',
      'Grazie [Nome] per la fiducia! ❤️',
      'La tua storia potrebbe essere la prossima',
      'Scopri cosa dicono i nostri clienti',
    ],
  },
];

// ============================================================================
// VIDEO SCRIPT TEMPLATES
// ============================================================================

export const VIDEO_SCRIPT_TEMPLATES: QuickTemplate[] = [
  {
    id: 'video_lancio',
    label: '🚀 Lancio Prodotto Video',
    value: 'Presentazione video di un nuovo prodotto/servizio',
    category: 'video',
    postType: 'lancio_prodotto',
    icon: '🚀',
    structure: {
      hook: 'Apertura shock nei primi 3 secondi',
      bodyPoints: 4,
      ctaRequired: true,
      hashtagCount: 5,
      emojiLevel: 'medium',
    },
    aiPrompt: `
STRUTTURA VIDEO LANCIO (30-60 sec):

⏱️ 0-3 sec - HOOK:
"[Domanda provocatoria o statement shock]"

⏱️ 3-15 sec - PROBLEMA:
"Sappiamo che [problema comune]..."

⏱️ 15-30 sec - SOLUZIONE:
"Ecco perché abbiamo creato [prodotto]..."

⏱️ 30-45 sec - BENEFICI:
• [Beneficio 1]
• [Beneficio 2]
• [Beneficio 3]

⏱️ 45-60 sec - CTA:
"Vuoi saperne di più? [azione]"

STILE VISIVO:
- Colori brand: Oro #D4AF37, Nero #0A0A0A
- Sottotitoli sempre visibili
- Transizioni fluide
- Logo in chiusura
`,
    platforms: ['instagram', 'tiktok', 'youtube', 'linkedin'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#VideoMarketing', '#NuovoLancio'],
    ctaOptions: [
      'Link in bio per saperne di più',
      'Commenta "INFO" per ricevere dettagli',
      'Seguici per non perderti nulla',
    ],
  },
  {
    id: 'video_tutorial',
    label: '💡 Tutorial Video',
    value: 'Tutorial passo-passo',
    category: 'video',
    postType: 'tutorial',
    icon: '💡',
    structure: {
      hook: 'Promessa di risultato immediato',
      bodyPoints: 5,
      ctaRequired: true,
      hashtagCount: 8,
      emojiLevel: 'medium',
    },
    aiPrompt: `
STRUTTURA VIDEO TUTORIAL (60-120 sec):

⏱️ 0-5 sec - HOOK:
"In [X] secondi impari a [risultato]"

⏱️ 5-15 sec - CONTESTO:
"Questo ti serve se [situazione]..."

⏱️ 15-90 sec - STEP BY STEP:
Step 1: [Azione + visual]
Step 2: [Azione + visual]
Step 3: [Azione + visual]

⏱️ 90-110 sec - RISULTATO:
"Ed ecco il risultato finale!"

⏱️ 110-120 sec - CTA:
"Salva questo video e seguici per altri tutorial!"

STILE VISIVO:
- Screen recording + facecam piccola
- Evidenziazione delle azioni
- Testo on-screen per i punti chiave
- Musica di sottofondo soft
`,
    platforms: ['instagram', 'tiktok', 'youtube'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#Tutorial', '#HowTo', '#ImparaConNoi', '#TechTips'],
    ctaOptions: [
      'Salva per dopo! 📌',
      'Quale tutorial vuoi vedere?',
      'Seguici per tutorial quotidiani',
    ],
  },
  {
    id: 'video_testimonial',
    label: '🌟 Testimonial Video',
    value: 'Video testimonianza cliente',
    category: 'video',
    postType: 'testimonial',
    icon: '🌟',
    structure: {
      hook: 'Risultato numerico impattante',
      bodyPoints: 3,
      ctaRequired: true,
      hashtagCount: 5,
      emojiLevel: 'low',
    },
    aiPrompt: `
STRUTTURA VIDEO TESTIMONIAL (45-90 sec):

⏱️ 0-5 sec - HOOK:
"[Risultato numerico o citazione impattante]"

⏱️ 5-20 sec - PRESENTAZIONE:
"Sono [Nome] di [Azienda]..."

⏱️ 20-40 sec - PRIMA:
"Prima di StudioCentOS, [problema]..."

⏱️ 40-60 sec - DOPO:
"Ora invece [soluzione e risultati]..."

⏱️ 60-80 sec - CONSIGLIO:
"A chi ha lo stesso problema, dico [consiglio]..."

⏱️ 80-90 sec - CHIUSURA:
"Grazie StudioCentOS!"

STILE VISIVO:
- Intervista professionale
- B-roll dell'azienda cliente
- Grafiche con numeri/risultati
- Sottotitoli obbligatori
`,
    platforms: ['linkedin', 'youtube', 'facebook'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#Testimonial', '#ClientiSoddisfatti', '#Successo'],
    ctaOptions: [
      'Vuoi raccontare la tua storia?',
      'Contattaci per una consulenza',
      'Link in bio per iniziare',
    ],
  },
  {
    id: 'video_chi_siamo',
    label: '💼 Chi Siamo',
    value: 'Presentazione aziendale StudioCentOS',
    category: 'video',
    postType: 'educational',
    icon: '💼',
    structure: {
      hook: 'Mission statement potente',
      bodyPoints: 4,
      ctaRequired: true,
      hashtagCount: 6,
      emojiLevel: 'low',
    },
    aiPrompt: `
STRUTTURA VIDEO CHI SIAMO (60-90 sec):

⏱️ 0-5 sec - HOOK:
"${BRAND_DNA.tagline}"

⏱️ 5-20 sec - CHI SIAMO:
"Siamo StudioCentOS, software house italiana..."

⏱️ 20-40 sec - MISSION:
"${BRAND_DNA.mission}"

⏱️ 40-60 sec - COSA FACCIAMO:
• Sviluppo software
• Soluzioni AI
• Automazione marketing
• Consulenza digitale

⏱️ 60-80 sec - PERCHÉ SCEGLIERCI:
• Team italiano
• Supporto dedicato
• Risultati misurabili

⏱️ 80-90 sec - CTA:
"Pronto a digitalizzare la tua azienda?"

STILE VISIVO:
- Colori brand: Oro #D4AF37, Nero #0A0A0A
- Team al lavoro
- Showcase progetti
- Professionale ma accessibile
`,
    platforms: ['linkedin', 'youtube', 'facebook', 'instagram'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#ChiSiamo', '#SoftwareHouse', '#TeamItalia'],
    ctaOptions: [
      'Scopri cosa possiamo fare per te',
      'Visita il nostro sito →',
      'Contattaci per una consulenza',
    ],
  },
  {
    id: 'video_trend',
    label: '🔥 Trend Tech',
    value: 'Analisi trend tecnologici',
    category: 'video',
    postType: 'trend_settore',
    icon: '🔥',
    structure: {
      hook: 'Previsione o dato shock',
      bodyPoints: 3,
      ctaRequired: true,
      hashtagCount: 8,
      emojiLevel: 'medium',
    },
    aiPrompt: `
STRUTTURA VIDEO TREND (45-60 sec):

⏱️ 0-5 sec - HOOK:
"[Statistica shock o previsione]"

⏱️ 5-20 sec - IL TREND:
"Ecco cosa sta cambiando..."

⏱️ 20-35 sec - IMPATTO PMI:
"Per le PMI questo significa..."

⏱️ 35-50 sec - COSA FARE:
"Ecco come prepararsi:
1. [Azione 1]
2. [Azione 2]
3. [Azione 3]"

⏱️ 50-60 sec - CTA:
"Sei pronto? Seguici per restare aggiornato"

STILE VISIVO:
- Grafiche animate con dati
- News style / Reportage
- Fonti visualizzate
- Ritmo dinamico
`,
    platforms: ['instagram', 'tiktok', 'linkedin', 'youtube'],
    hashtags: [...BRAND_DNA.hashtags.brand, '#Trend', '#Tech', '#Futuro', '#Innovazione'],
    ctaOptions: [
      'Seguici per restare aggiornato',
      'Cosa ne pensi? Commenta 👇',
      'Condividi con chi deve saperlo',
    ],
  },
];

// ============================================================================
// STORY TEMPLATES
// ============================================================================

export interface StoryTemplate {
  id: string;
  name: string;
  preview: string;
  category: StoryTemplateCategory;
  structure: {
    slides: number;
    hasCTA: boolean;
    hasSwipeUp: boolean;
  };
  aiPrompt: string;
  visualStyle: {
    primaryColor: string;
    secondaryColor: string;
    fontStyle: 'bold' | 'elegant' | 'minimal' | 'playful';
  };
}

export type StoryTemplateCategory = 'promo' | 'quote' | 'announcement' | 'product' | 'testimonial' | 'tip' | 'engagement';

export const STORY_TEMPLATES: StoryTemplate[] = [
  {
    id: 'promo_sconto',
    name: 'Promo Sconto',
    preview: '🏷️',
    category: 'promo',
    structure: { slides: 3, hasCTA: true, hasSwipeUp: true },
    aiPrompt: `
STRUTTURA STORY PROMO (3 slide):

SLIDE 1 - HOOK:
🔥 [SCONTO X%]
[Titolo breve accattivante]

SLIDE 2 - DETTAGLI:
✅ Cosa include
✅ Valore reale
✅ Scadenza

SLIDE 3 - CTA:
⬆️ SWIPE UP per info
oppure
📩 Scrivi "PROMO" in DM

STILE: Bold, urgente, colori brand
`,
    visualStyle: {
      primaryColor: '#D4AF37',
      secondaryColor: '#0A0A0A',
      fontStyle: 'bold',
    },
  },
  {
    id: 'lancio_prodotto',
    name: 'Lancio Prodotto',
    preview: '🚀',
    category: 'product',
    structure: { slides: 4, hasCTA: true, hasSwipeUp: true },
    aiPrompt: `
STRUTTURA STORY LANCIO (4 slide):

SLIDE 1 - TEASER:
🚀 NOVITÀ IN ARRIVO
[Anticipazione misteriosa]

SLIDE 2 - REVEAL:
Presentazione prodotto/servizio
[Immagine o mockup]

SLIDE 3 - BENEFICI:
✨ [Beneficio 1]
✨ [Beneficio 2]
✨ [Beneficio 3]

SLIDE 4 - CTA:
⬆️ Scopri di più
[Link o azione]

STILE: Elegante, premium, colori brand
`,
    visualStyle: {
      primaryColor: '#D4AF37',
      secondaryColor: '#0A0A0A',
      fontStyle: 'elegant',
    },
  },
  {
    id: 'citazione_minimal',
    name: 'Citazione Minimal',
    preview: '💬',
    category: 'quote',
    structure: { slides: 1, hasCTA: false, hasSwipeUp: false },
    aiPrompt: `
STRUTTURA STORY QUOTE (1 slide):

"[Citazione ispirazionale o di valore]"

— Nome Autore

STILE: Minimal, elegante, sfondo neutro
Tipografia: grande e leggibile
Logo brand in basso
`,
    visualStyle: {
      primaryColor: '#FAFAFA',
      secondaryColor: '#0A0A0A',
      fontStyle: 'minimal',
    },
  },
  {
    id: 'citazione_bold',
    name: 'Citazione Bold',
    preview: '📢',
    category: 'quote',
    structure: { slides: 1, hasCTA: false, hasSwipeUp: false },
    aiPrompt: `
STRUTTURA STORY QUOTE BOLD (1 slide):

[PAROLA CHIAVE]
"[Citazione potente e diretta]"

@studiocentos

STILE: Bold, impattante, colori forti
Tipografia: extra bold, grande
Effetto grafico dinamico
`,
    visualStyle: {
      primaryColor: '#D4AF37',
      secondaryColor: '#0A0A0A',
      fontStyle: 'bold',
    },
  },
  {
    id: 'annuncio_news',
    name: 'Annuncio News',
    preview: '📰',
    category: 'announcement',
    structure: { slides: 2, hasCTA: true, hasSwipeUp: false },
    aiPrompt: `
STRUTTURA STORY NEWS (2 slide):

SLIDE 1:
📢 ANNUNCIO
[Titolo della news]

SLIDE 2:
[Dettagli essenziali]
💬 Commenta cosa ne pensi!

STILE: News style, professionale
Tipografia: pulita e leggibile
`,
    visualStyle: {
      primaryColor: '#0A0A0A',
      secondaryColor: '#D4AF37',
      fontStyle: 'minimal',
    },
  },
  {
    id: 'coming_soon',
    name: 'Coming Soon',
    preview: '⏰',
    category: 'announcement',
    structure: { slides: 2, hasCTA: true, hasSwipeUp: false },
    aiPrompt: `
STRUTTURA STORY COMING SOON (2 slide):

SLIDE 1:
⏰ COMING SOON
[Countdown o data]

SLIDE 2:
[Teaser misterioso]
🔔 Attiva le notifiche per non perderlo!

STILE: Suspense, anticipazione
Effetti: blur, countdown
`,
    visualStyle: {
      primaryColor: '#D4AF37',
      secondaryColor: '#0A0A0A',
      fontStyle: 'bold',
    },
  },
  {
    id: 'showcase_prodotto',
    name: 'Showcase Prodotto',
    preview: '📦',
    category: 'product',
    structure: { slides: 3, hasCTA: true, hasSwipeUp: true },
    aiPrompt: `
STRUTTURA STORY SHOWCASE (3 slide):

SLIDE 1:
[Immagine prodotto full screen]

SLIDE 2:
✨ Caratteristiche principali
• [Feature 1]
• [Feature 2]
• [Feature 3]

SLIDE 3:
💰 [Prezzo o CTA]
⬆️ Scopri di più

STILE: Product photography, clean
Focus sul prodotto
`,
    visualStyle: {
      primaryColor: '#FAFAFA',
      secondaryColor: '#D4AF37',
      fontStyle: 'elegant',
    },
  },
  {
    id: 'testimonial_story',
    name: 'Testimonianza',
    preview: '⭐',
    category: 'testimonial',
    structure: { slides: 2, hasCTA: true, hasSwipeUp: false },
    aiPrompt: `
STRUTTURA STORY TESTIMONIAL (2 slide):

SLIDE 1:
⭐⭐⭐⭐⭐
"[Citazione cliente]"

SLIDE 2:
— [Nome Cliente]
[Ruolo/Azienda]
📈 [Risultato ottenuto]

STILE: Social proof, credibile
Foto cliente (se autorizzato)
`,
    visualStyle: {
      primaryColor: '#D4AF37',
      secondaryColor: '#0A0A0A',
      fontStyle: 'elegant',
    },
  },
  {
    id: 'tip_rapido',
    name: 'Tip Rapido',
    preview: '💡',
    category: 'tip',
    structure: { slides: 2, hasCTA: true, hasSwipeUp: false },
    aiPrompt: `
STRUTTURA STORY TIP (2 slide):

SLIDE 1:
💡 TIP DEL GIORNO
[Titolo tip]

SLIDE 2:
[Spiegazione breve]
✅ [Azione pratica]

📌 Salva questa storia!

STILE: Educational, chiaro
Tipografia leggibile
`,
    visualStyle: {
      primaryColor: '#D4AF37',
      secondaryColor: '#0A0A0A',
      fontStyle: 'minimal',
    },
  },
  {
    id: 'sondaggio',
    name: 'Sondaggio',
    preview: '📊',
    category: 'engagement',
    structure: { slides: 1, hasCTA: true, hasSwipeUp: false },
    aiPrompt: `
STRUTTURA STORY SONDAGGIO (1 slide):

[Domanda engaging]

[Sticker sondaggio Instagram]
A) [Opzione 1]
B) [Opzione 2]

Oppure:
[Sticker slider emoji]
[Sticker domanda aperta]

STILE: Interattivo, colorato
Usa sticker nativi Instagram
`,
    visualStyle: {
      primaryColor: '#D4AF37',
      secondaryColor: '#FAFAFA',
      fontStyle: 'playful',
    },
  },
];

// ============================================================================
// CAROUSEL TEMPLATES
// ============================================================================

export interface CarouselTemplate {
  id: string;
  name: string;
  icon: string;
  slides: number;
  category: ContentCategory;
  structure: CarouselSlide[];
  aiPrompt: string;
}

export interface CarouselSlide {
  type: 'hook' | 'content' | 'tip' | 'cta';
  title: string;
  description: string;
}

export const CAROUSEL_TEMPLATES: CarouselTemplate[] = [
  {
    id: 'carousel_tips',
    name: '5 Tips Carousel',
    icon: '💡',
    slides: 7,
    category: 'carousel',
    structure: [
      { type: 'hook', title: 'Cover', description: 'Titolo accattivante + problema' },
      { type: 'tip', title: 'Tip 1', description: 'Primo consiglio pratico' },
      { type: 'tip', title: 'Tip 2', description: 'Secondo consiglio pratico' },
      { type: 'tip', title: 'Tip 3', description: 'Terzo consiglio pratico' },
      { type: 'tip', title: 'Tip 4', description: 'Quarto consiglio pratico' },
      { type: 'tip', title: 'Tip 5', description: 'Quinto consiglio pratico' },
      { type: 'cta', title: 'CTA', description: 'Call to action finale' },
    ],
    aiPrompt: `
STRUTTURA CAROUSEL 5 TIPS:

SLIDE 1 (COVER):
[Titolo: 5 [cosa] per [risultato]]
[Sottotitolo: Hook che invita a scorrere]

SLIDE 2-6 (TIPS):
[Numero] [Emoji]
[Titolo Tip]
[Spiegazione 2-3 righe]
[Visual/icona illustrativa]

SLIDE 7 (CTA):
[Riassunto]
📌 Salva questo carousel
💬 Quale tip userai?
👉 Seguici @studiocentos

STILE VISIVO:
- Colori coerenti brand
- Tipografia leggibile
- Ogni slide auto-conclusiva
- Swipe indicator visibile
`,
  },
  {
    id: 'carousel_before_after',
    name: 'Before/After',
    icon: '🔄',
    slides: 5,
    category: 'carousel',
    structure: [
      { type: 'hook', title: 'Cover', description: 'Prima vs Dopo teaser' },
      { type: 'content', title: 'Before', description: 'Situazione problematica' },
      { type: 'content', title: 'Soluzione', description: 'Cosa abbiamo fatto' },
      { type: 'content', title: 'After', description: 'Risultato ottenuto' },
      { type: 'cta', title: 'CTA', description: 'Vuoi lo stesso risultato?' },
    ],
    aiPrompt: `
STRUTTURA CAROUSEL BEFORE/AFTER:

SLIDE 1 (COVER):
PRIMA 👉 DOPO
[Titolo trasformazione]

SLIDE 2 (BEFORE):
❌ PRIMA
[Screenshot/immagine problematica]
[Punti critici]

SLIDE 3 (SOLUZIONE):
🛠️ COSA ABBIAMO FATTO
[Elenco azioni]

SLIDE 4 (AFTER):
✅ DOPO
[Screenshot/immagine risultato]
[Metriche migliorate]

SLIDE 5 (CTA):
📈 I NUMERI
[Metriche confronto]
Vuoi lo stesso risultato? →
`,
  },
  {
    id: 'carousel_guide',
    name: 'Mini Guida',
    icon: '📚',
    slides: 8,
    category: 'carousel',
    structure: [
      { type: 'hook', title: 'Cover', description: 'Titolo guida + target' },
      { type: 'content', title: 'Introduzione', description: 'Perché questa guida' },
      { type: 'content', title: 'Step 1', description: 'Primo passo' },
      { type: 'content', title: 'Step 2', description: 'Secondo passo' },
      { type: 'content', title: 'Step 3', description: 'Terzo passo' },
      { type: 'content', title: 'Step 4', description: 'Quarto passo' },
      { type: 'content', title: 'Bonus', description: 'Consiglio extra' },
      { type: 'cta', title: 'CTA', description: 'Conclusione e azione' },
    ],
    aiPrompt: `
STRUTTURA CAROUSEL MINI GUIDA:

SLIDE 1 (COVER):
📚 GUIDA COMPLETA
[Titolo: Come fare X in Y step]
[Target: Per chi è]

SLIDE 2 (INTRO):
❓ Perché [problema]?
[Contesto e importanza]

SLIDE 3-6 (STEPS):
STEP [N]
[Titolo azione]
[Istruzioni dettagliate]
[Visual esplicativo]

SLIDE 7 (BONUS):
💎 BONUS
[Consiglio avanzato]
[Tool/risorsa consigliata]

SLIDE 8 (CTA):
✅ RIASSUNTO
[Checklist rapida]
📌 Salva | 💬 Commenta | ➡️ Condividi
`,
  },
];

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Ottiene template per categoria
 */
export function getTemplatesByCategory(category: ContentCategory): QuickTemplate[] {
  return SOCIAL_QUICK_TEMPLATES.filter(t => t.category === category);
}

/**
 * Ottiene template per tipo di post
 */
export function getTemplatesByPostType(postType: PostType): QuickTemplate[] {
  return SOCIAL_QUICK_TEMPLATES.filter(t => t.postType === postType);
}

/**
 * Ottiene template per piattaforma
 */
export function getTemplatesForPlatform(platform: SocialPlatform): QuickTemplate[] {
  return SOCIAL_QUICK_TEMPLATES.filter(t => t.platforms.includes(platform));
}

/**
 * Ottiene il prompt AI per un template
 */
export function getAIPromptForTemplate(templateId: string): string | null {
  const template = SOCIAL_QUICK_TEMPLATES.find(t => t.id === templateId);
  return template?.aiPrompt || null;
}

/**
 * Genera hashtag per un template
 */
export function getHashtagsForTemplate(templateId: string, limit: number = 10): string[] {
  const template = SOCIAL_QUICK_TEMPLATES.find(t => t.id === templateId);
  return template?.hashtags.slice(0, limit) || [...BRAND_DNA.hashtags.brand];
}

/**
 * Ottiene tutti i template disponibili
 */
export function getAllTemplates(): {
  social: QuickTemplate[];
  video: QuickTemplate[];
  story: StoryTemplate[];
  carousel: CarouselTemplate[];
} {
  return {
    social: SOCIAL_QUICK_TEMPLATES,
    video: VIDEO_SCRIPT_TEMPLATES,
    story: STORY_TEMPLATES,
    carousel: CAROUSEL_TEMPLATES,
  };
}
