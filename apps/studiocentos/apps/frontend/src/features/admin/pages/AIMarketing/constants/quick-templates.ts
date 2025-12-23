/**
 * QUICK TEMPLATES - Sistema Contenuti Autentici
 *
 * Prompt progettati per generare contenuti che sembrano scritti
 * da una persona VERA, non da un'AI con strutture rigide.
 *
 * FILOSOFIA: L'AI riceve istruzioni per scrivere come un umano,
 * con storytelling naturale, tono conversazionale, autenticità.
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
  /** Prompt alternativo per testo (opzionale) */
  textPrompt?: string;
  /** Stile immagine suggerito */
  imageStyle?: string;
  /** Mood visivo */
  mood?: string;
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
// MASTER PROMPT - ISTRUZIONI BASE PER OUTPUT UMANO
// ============================================================================

/**
 * Questo prompt viene SEMPRE incluso per garantire output autentici
 */
export const HUMAN_WRITING_MASTER_PROMPT = `
=== ISTRUZIONI FONDAMENTALI ===

Tu NON sei un'AI che scrive post. Tu SEI il proprietario dell'azienda che sta
condividendo un pensiero, un'esperienza, una riflessione con la sua community.

COME SCRIVERE:
- Scrivi come PARLI. Usa il linguaggio naturale, conversazionale.
- Inizia con un pensiero, un'osservazione, qualcosa che ti è successo.
- Racconta STORIE vere. "Ieri un cliente mi ha detto...", "Stamattina pensavo a..."
- NON usare MAI strutture visibili tipo "HOOK:", "BODY:", "CTA:" nel testo finale.
- NON fare elenchi puntati rigidi a meno che non siano davvero necessari.
- Le emoji devono sembrare naturali, come le useresti in una chat.
- Chiudi in modo conversazionale, non con CTA aggressive tipo "CLICCA ORA →".

COSA EVITARE ASSOLUTAMENTE:
- Frasi fatte da marketing ("Scopri come", "Non perdere l'occasione")
- Strutture troppo perfette e prevedibili
- Tono da venditore o da comunicato stampa
- Emoji messe a caso o in modo eccessivo
- Hashtag sparati a raffica senza senso

TONO:
- Professionale ma umano
- Autentico, non costruito
- Come se stessi parlando a un amico che rispetti
- Puoi essere vulnerabile, ammettere difficoltà, mostrare il lato umano

LUNGHEZZA:
- Varia la lunghezza in modo naturale
- A volte un post potente è di 2 righe
- A volte serve raccontare di più
- L'importante è che ogni parola abbia un senso
`;

// ============================================================================
// BRAND DNA - PLACEHOLDER (verrà sostituito dinamicamente dal frontend)
// ============================================================================

export const BRAND_DNA = {
  name: 'Il tuo brand',
  tagline: 'La tua tagline',
  mission: 'La tua mission',

  colors: {
    primary: '#D4AF37',
    secondary: '#0A0A0A',
    accent: '#FAFAFA',
    gradient: 'linear-gradient(135deg, #D4AF37 0%, #0A0A0A 100%)',
  },

  toneOfVoice: {
    primary: 'professionale ma accessibile',
    style: 'diretto e concreto',
    emotion: 'positivo ma realistico',
    approach: 'empatico',
  },

  values: ['Qualità', 'Affidabilità', 'Innovazione'],

  targetAudience: {
    primary: 'Il tuo target principale',
    secondary: ['Target secondari'],
    sectors: ['I tuoi settori'],
  },

  hashtags: {
    brand: ['#IlTuoBrand'],
    local: ['#LaTuaCittà'],
    industry: ['#IlTuoSettore'],
  },

  wordsToAvoid: ['Gergo', 'Buzzword'],

  contentPillars: ['I tuoi pillar di contenuto'],
} as const;

// ============================================================================
// SOCIAL QUICK TEMPLATES - Prompt per Output Autentici e Umani
// ============================================================================

export const SOCIAL_QUICK_TEMPLATES: QuickTemplate[] = [
  // LANCIO PRODOTTO
  {
    id: 'lancio_prodotto',
    label: '🚀 Lancio Prodotto',
    value: 'Lancio di un nuovo prodotto/servizio',
    category: 'social',
    postType: 'lancio_prodotto',
    icon: '🚀',
    structure: {
      hook: 'Storia personale dietro il lancio',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 4,
      emojiLevel: 'low',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: LANCIO PRODOTTO/SERVIZIO ===

Immagina di essere l'imprenditore che ha appena finito di costruire qualcosa
di cui è genuinamente orgoglioso. Non stai "vendendo", stai CONDIVIDENDO.

COME SCRIVERE QUESTO POST:

1. INIZIA con il PERCHÉ personale:
   - Racconta brevemente cosa ti ha portato a creare questo
   - "Da mesi vedevo clienti lottare con..."
   - "C'era un problema che mi toglieva il sonno..."

2. PRESENTA la soluzione in modo naturale:
   - Non elencare feature, racconta cosa CAMBIA per le persone
   - Parla di trasformazione, non di specifiche tecniche

3. CHIUDI con genuinità:
   - Non "PRENOTA ORA!!!" ma qualcosa tipo:
   - "Se ti ritrovi in questa situazione, scrivimi. Ne parliamo."
   - "Sono curioso di sapere cosa ne pensi."

ESEMPI DI TONO GIUSTO:
✅ "Ci ho lavorato 6 mesi. Oggi finalmente posso mostrarvelo."
✅ "Non è perfetto, ma risolve un problema reale."
❌ "🚀🔥 LANCIO ESCLUSIVO! OFFERTA LIMITATA!"

Scrivi in italiano, massimo 3-4 hashtag naturali alla fine.
`,
    textPrompt: `Scrivi come se stessi raccontando a un amico il lancio di qualcosa che hai costruito con passione. Niente vendita aggressiva, solo condivisione genuina.`,
    imageStyle: 'clean product photography, natural lighting, authentic workspace background',
    mood: 'proud but humble, genuine excitement',
    platforms: ['instagram', 'facebook', 'linkedin', 'threads'],
    hashtags: ['#NuovoProgetto', '#FattoInItalia', '#Innovazione'],
    ctaOptions: [
      'Scrivimi se vuoi saperne di più',
      'Cosa ne pensi? Mi interessa il tuo parere',
      'Link in bio per i dettagli',
    ],
  },

  // TIP DEL GIORNO
  {
    id: 'tip_giorno',
    label: '💡 Tip del Giorno',
    value: 'Consiglio pratico e utile',
    category: 'social',
    postType: 'tip_giorno',
    icon: '💡',
    structure: {
      hook: 'Esperienza personale che porta al tip',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 5,
      emojiLevel: 'medium',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: TIP/CONSIGLIO ===

Non stai scrivendo un "tip del giorno" da manuale. Stai condividendo qualcosa
che HAI IMPARATO, magari sbagliando, e che vuoi passare agli altri.

COME SCRIVERE QUESTO POST:

1. PARTI da un'esperienza REALE:
   - "La settimana scorsa ho fatto un errore stupido..."
   - "Un cliente mi ha fatto notare una cosa che non avevo considerato..."
   - "Ci ho messo anni a capire che..."

2. CONDIVIDI il consiglio in modo NATURALE:
   - Non "Step 1, Step 2, Step 3"
   - Ma "Quello che ho capito è che..." o "La cosa che funziona è..."
   - Spiega il PERCHÉ, non solo il COSA

3. RENDI PERSONALE:
   - Ammetti se anche tu a volte sbagli
   - Mostra che sei umano, non un guru

ESEMPI DI TONO GIUSTO:
✅ "Ho perso 3 ore ieri per una cosa che si risolveva in 5 minuti. Ecco cosa ho imparato."
✅ "Questo consiglio sembra banale, ma mi ha cambiato il modo di lavorare."
❌ "💡 TIP #47: COME AUMENTARE LA PRODUTTIVITÀ DEL 300%!!!"

Scrivi in italiano, tono conversazionale.
`,
    textPrompt: `Condividi un consiglio come se lo stessi dando a un collega durante un caffè. Inizia con come l'hai scoperto tu.`,
    imageStyle: 'workspace lifestyle, coffee and laptop, natural casual setting',
    mood: 'helpful and relatable, friendly mentor',
    platforms: ['instagram', 'linkedin', 'twitter', 'threads'],
    hashtags: ['#ConsigliUtili', '#ImparoOgniGiorno', '#Crescita'],
    ctaOptions: [
      'Tu come la gestisci questa cosa?',
      'Salva se ti è utile',
      'Quale tip vorresti la prossima volta?',
    ],
  },

  // CASO DI SUCCESSO
  {
    id: 'caso_successo',
    label: '🌟 Caso di Successo',
    value: 'Storia di un cliente soddisfatto',
    category: 'social',
    postType: 'caso_successo',
    icon: '🌟',
    structure: {
      hook: 'Il momento di svolta del cliente',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 4,
      emojiLevel: 'low',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: CASO DI SUCCESSO ===

Non stai scrivendo un "case study" aziendale. Stai raccontando la STORIA
di una persona reale che aveva un problema e l'ha risolto.

COME SCRIVERE QUESTO POST:

1. INIZIA con la PERSONA, non con i numeri:
   - "Marco gestisce un ristorante a Salerno..."
   - "Quando Laura mi ha chiamato la prima volta, era frustrata..."
   - Non "Il cliente X ha ottenuto +50%..."

2. RACCONTA il VIAGGIO:
   - Com'era la situazione prima (con empatia, non per sminuire)
   - Il momento di svolta
   - Come sta ora (con dettagli concreti ma non freddi)

3. LASCIA che i RISULTATI emergano dalla storia:
   - Non "ROI del 200%" ma "Ora Marco chiude alle 23 invece che a mezzanotte"
   - Risultati UMANI, non solo metriche

4. CHIUDI con gratitudine:
   - "Grazie Marco per la fiducia"
   - "Storie così mi ricordano perché faccio questo lavoro"

ESEMPI DI TONO GIUSTO:
✅ "Quando l'ho incontrato, passava 4 ore al giorno a rispondere alle stesse email. Oggi? 20 minuti."
✅ "Non dimenticherò mai la sua faccia quando ha visto i primi risultati."
❌ "CASO STUDIO: +500% DI CONVERSIONI IN 30 GIORNI!"

Scrivi in italiano, storytelling autentico.
`,
    textPrompt: `Racconta la storia di un cliente come la racconteresti a un amico. Inizia dalla persona, non dai numeri.`,
    imageStyle: 'real business environment, authentic workplace, genuine people',
    mood: 'proud of client success, warm and grateful',
    platforms: ['linkedin', 'facebook', 'instagram'],
    hashtags: ['#StorieDiSuccesso', '#ClientiSoddisfatti', '#Risultati'],
    ctaOptions: [
      'Se ti ritrovi nella situazione di Marco, parliamone',
      'Grazie per la fiducia',
      'La prossima storia potrebbe essere la tua',
    ],
  },

  // TREND DEL SETTORE
  {
    id: 'trend_settore',
    label: '📈 Trend del Settore',
    value: 'Riflessione su cosa sta cambiando',
    category: 'social',
    postType: 'trend_settore',
    icon: '📈',
    structure: {
      hook: 'Osservazione personale su un cambiamento',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 5,
      emojiLevel: 'low',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: TREND/RIFLESSIONE ===

Non stai scrivendo un report di settore. Stai condividendo una RIFLESSIONE
personale su qualcosa che stai osservando nel tuo lavoro.

COME SCRIVERE QUESTO POST:

1. PARTI da un'OSSERVAZIONE personale:
   - "Nelle ultime settimane ho notato una cosa..."
   - "Parlando con diversi clienti, sta emergendo un pattern..."
   - "C'è qualcosa che sta cambiando e non tutti se ne accorgono..."

2. CONDIVIDI la tua INTERPRETAZIONE:
   - Non "Il mercato crescerà del X%" ma "Secondo me, questo significa che..."
   - Opinione personale, non comunicato stampa
   - Puoi anche ammettere incertezza: "Non so se ho ragione, ma..."

3. APRI una DISCUSSIONE:
   - "Voi cosa ne pensate?"
   - "State notando la stessa cosa?"
   - "Mi piacerebbe sapere come la vedete"

ESEMPI DI TONO GIUSTO:
✅ "C'è una cosa che mi sta facendo riflettere ultimamente..."
✅ "Non so voi, ma io sto vedendo un cambiamento interessante."
❌ "📊 BREAKING: IL MERCATO AI CRESCERÀ DEL 300%! ECCO COSA DEVI FARE!"

Scrivi in italiano, tono riflessivo e aperto al dialogo.
`,
    textPrompt: `Condividi una riflessione su qualcosa che stai osservando nel tuo settore. Non un report, ma un pensiero personale.`,
    imageStyle: 'thoughtful, clean graphics, minimal data visualization',
    mood: 'thoughtful and curious, open to discussion',
    platforms: ['linkedin', 'twitter', 'threads'],
    hashtags: ['#Riflessioni', '#FuturoDelLavoro', '#Cambiamento'],
    ctaOptions: [
      'Voi cosa ne pensate?',
      'State notando la stessa cosa?',
      'Mi interessa la vostra opinione',
    ],
  },

  // OFFERTA SPECIALE
  {
    id: 'offerta_speciale',
    label: '🎯 Offerta Speciale',
    value: 'Promozione o offerta limitata',
    category: 'social',
    postType: 'offerta_speciale',
    icon: '🎯',
    structure: {
      hook: 'Motivo genuino dietro l\'offerta',
      bodyPoints: 0,
      ctaRequired: true,
      hashtagCount: 3,
      emojiLevel: 'medium',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: OFFERTA/PROMOZIONE ===

Anche quando vendi, puoi farlo con autenticità. Non urlare sconti,
SPIEGA perché stai facendo questa offerta.

COME SCRIVERE QUESTO POST:

1. SPIEGA il PERCHÉ dell'offerta:
   - "È quasi fine anno e voglio ringraziare chi mi ha seguito..."
   - "Ho qualche slot libero questo mese e preferisco riempirli..."
   - "Festeggio un traguardo e voglio condividere..."
   - Un motivo VERO, non "OFFERTA IMPERDIBILE!!!"

2. DESCRIVI cosa offri in modo CHIARO:
   - Niente giri di parole
   - Prezzo chiaro, cosa include, fino a quando
   - Onestà totale

3. CHIUDI senza pressione:
   - Non "ULTIMI POSTI!!!" se non è vero
   - "Se ti interessa, scrivimi" è sufficiente
   - Rispetta l'intelligenza di chi legge

ESEMPI DI TONO GIUSTO:
✅ "Ho 3 slot liberi a dicembre. Se stavi pensando di iniziare un progetto, questo è un buon momento."
✅ "Per ringraziare chi mi segue da un po', questo mese offro una consulenza iniziale gratuita."
❌ "🔥🔥🔥 MEGA SCONTO -70%!!! SOLO PER OGGI!!! CLICCA ORA!!!"

Scrivi in italiano, onestà e trasparenza.
`,
    textPrompt: `Presenta un'offerta spiegando onestamente perché la fai. Niente urgenza finta o pressione.`,
    imageStyle: 'clean promotional, elegant, not salesy',
    mood: 'generous and transparent, no pressure',
    platforms: ['instagram', 'facebook', 'threads'],
    hashtags: ['#Offerta', '#Opportunità'],
    ctaOptions: [
      'Se ti interessa, scrivimi',
      'I dettagli sono nel link in bio',
      'Hai domande? Sono qui',
    ],
  },

  // AI PER BUSINESS
  {
    id: 'ai_business',
    label: '🤖 AI per Business',
    value: 'Come l\'AI può aiutare concretamente',
    category: 'social',
    postType: 'ai_business',
    icon: '🤖',
    structure: {
      hook: 'Esempio concreto e demistificante',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 4,
      emojiLevel: 'low',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: AI/TECNOLOGIA SPIEGATA ===

L'AI spaventa o confonde molte persone. Il tuo lavoro è DEMISTIFICARE,
non impressionare con termini tecnici.

COME SCRIVERE QUESTO POST:

1. PARTI da un PROBLEMA QUOTIDIANO:
   - "Quanto tempo perdi a rispondere alle stesse domande?"
   - "Ti è mai capitato di dimenticare di seguire un cliente?"
   - Problemi REALI che le persone riconoscono

2. SPIEGA come la tecnologia AIUTA (non come funziona):
   - Non "Il machine learning processa..." ma "In pratica, questo significa che..."
   - Benefici concreti: tempo risparmiato, errori evitati, clienti più contenti
   - Esempi che anche tua nonna capirebbe

3. AMMETTI i LIMITI:
   - "Non è magia, ha i suoi limiti..."
   - "Funziona bene per X, meno per Y..."
   - Onestà > Hype

4. INVITA a CHIEDERE:
   - "Se vuoi capire se fa al caso tuo, parliamone"
   - "Sono qui per rispondere a dubbi, non per vendere"

ESEMPI DI TONO GIUSTO:
✅ "L'AI non ti ruberà il lavoro. Ma può liberarti dalle parti noiose per fare quelle che ami."
✅ "Mio padre mi ha chiesto: ma questa AI, in pratica, cosa fa? Ecco cosa gli ho risposto."
❌ "🤖 L'AI RIVOLUZIONERÀ IL TUO BUSINESS! ADOTTA ORA O RESTERAI INDIETRO!"

Scrivi in italiano, tono accessibile e onesto.
`,
    textPrompt: `Spiega un concetto tecnologico come lo spiegheresti a un amico non tecnico che è curioso ma un po' scettico.`,
    imageStyle: 'friendly tech visualization, human-centered, not cold',
    mood: 'helpful educator, demystifying, honest',
    platforms: ['linkedin', 'instagram', 'facebook', 'threads'],
    hashtags: ['#AI', '#TecnologiaAccessibile', '#Innovazione'],
    ctaOptions: [
      'Hai dubbi? Chiedimi pure',
      'Cosa vorresti automatizzare nel tuo lavoro?',
      'Ti spaventa o ti incuriosisce?',
    ],
  },

  // BEHIND THE SCENES
  {
    id: 'behind_scenes',
    label: '🎬 Behind the Scenes',
    value: 'Dietro le quinte del lavoro',
    category: 'social',
    postType: 'behind_scenes',
    icon: '🎬',
    structure: {
      hook: 'Momento autentico catturato',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 4,
      emojiLevel: 'medium',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: BEHIND THE SCENES ===

Questo è il contenuto più UMANO possibile. Mostra chi sei davvero,
non la versione perfetta e curata.

COME SCRIVERE QUESTO POST:

1. CATTURA un MOMENTO VERO:
   - La scrivania incasinata mentre lavori a un progetto
   - La pausa caffè dopo una riunione intensa
   - L'errore che hai fatto e come l'hai risolto
   - La soddisfazione di finire qualcosa

2. SCRIVI come pensi in quel momento:
   - "Sono le 22 e sono ancora qui. Ma questo progetto..."
   - "Il caffè di oggi: necessario per sopravvivere a questa deadline."
   - "Ho sbagliato. Ecco cosa è successo..."

3. MOSTRA VULNERABILITÀ (quando appropriato):
   - Non devi sembrare perfetto
   - Le persone si connettono con l'autenticità
   - "Non è stata una settimana facile, ma..."

4. INVITA alla connessione:
   - "Anche voi avete giornate così?"
   - "Chi mi capisce?"

ESEMPI DI TONO GIUSTO:
✅ "Questo è il caos creativo da cui nascono i progetti. Non giudicatemi 😅"
✅ "Dovevo finire per ieri. Sono ancora qui. Ma sta venendo bene."
❌ "📸 ECCO IL NOSTRO FANTASTICO TEAM AL LAVORO! #TEAMWORK #SUCCESS"

Scrivi in italiano, massima autenticità.
`,
    textPrompt: `Mostra un momento reale del tuo lavoro. Niente di costruito, solo verità.`,
    imageStyle: 'candid, unpolished, real workspace, natural lighting',
    mood: 'authentic and relatable, human',
    platforms: ['instagram', 'threads', 'tiktok'],
    hashtags: ['#VitaDaFreelance', '#DietroLeQuinte', '#LavoroVero'],
    ctaOptions: [
      'Anche voi così?',
      'Chi mi capisce alzi la mano',
      'La vostra scrivania com\'è messa?',
    ],
  },

  // EDUCATIONAL
  {
    id: 'educational',
    label: '📚 Educational',
    value: 'Contenuto formativo che insegna qualcosa',
    category: 'social',
    postType: 'educational',
    icon: '📚',
    structure: {
      hook: 'Problema comune che risolvi',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 5,
      emojiLevel: 'medium',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: EDUCATIONAL ===

Stai insegnando qualcosa, ma non come un professore noioso.
Come un amico che sa una cosa utile e vuole condividerla.

COME SCRIVERE QUESTO POST:

1. PARTI dal PROBLEMA che risolvi:
   - Non "Oggi parliamo di..." (noioso)
   - Ma "Ti è mai capitato di..." o "Sai quella sensazione quando..."

2. INSEGNA in modo CONVERSAZIONALE:
   - Non lezioni accademiche
   - Immagina di spiegarlo a qualcuno davanti a un caffè
   - Usa esempi concreti, non astratti

3. STRUTTURA solo se serve:
   - A volte un elenco aiuta (es. 3 step chiari)
   - Ma non forzare la struttura se non serve
   - Il contenuto guida la forma, non viceversa

4. DAI VALORE VERO:
   - Chi legge deve imparare qualcosa di UTILE
   - Qualcosa che può applicare SUBITO
   - Non teaser che rimandano a link

ESEMPI DI TONO GIUSTO:
✅ "C'è un errore che vedo fare continuamente. Ecco come evitarlo."
✅ "Questa cosa l'ho capita dopo anni. Te la spiego in 2 minuti."
❌ "📚 GUIDA COMPLETA IN 47 STEP PER DIVENTARE UN ESPERTO!"

Scrivi in italiano, valore reale e immediato.
`,
    textPrompt: `Insegna qualcosa di utile come lo spiegheresti a un amico curioso. Valore vero, non teaser.`,
    imageStyle: 'clean infographic style, readable, educational',
    mood: 'helpful teacher, generous with knowledge',
    platforms: ['instagram', 'linkedin', 'threads', 'pinterest'],
    hashtags: ['#Impara', '#Crescita', '#Formazione'],
    ctaOptions: [
      'Salva per dopo',
      'Quale argomento vuoi approfondire?',
      'Ti è stato utile?',
    ],
  },

  // ENGAGEMENT
  {
    id: 'engagement',
    label: '💬 Engagement',
    value: 'Post per stimolare conversazione',
    category: 'social',
    postType: 'engagement',
    icon: '💬',
    structure: {
      hook: 'Domanda genuina e interessante',
      bodyPoints: 0,
      ctaRequired: true,
      hashtagCount: 3,
      emojiLevel: 'medium',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: ENGAGEMENT/CONVERSAZIONE ===

Vuoi creare una conversazione VERA, non raccogliere like a caso.
La domanda deve essere genuina, qualcosa che ti interessa davvero sapere.

COME SCRIVERE QUESTO POST:

1. FAI una DOMANDA che ti interessa DAVVERO:
   - Non domande retoriche
   - Qualcosa su cui sei genuinamente curioso
   - "Mi chiedo spesso..." o "Sono curioso di sapere..."

2. CONDIVIDI la TUA risposta (opzionale ma potente):
   - "Per me è..."
   - "Io la penso così, ma..."
   - Questo invita gli altri a condividere

3. CREA uno spazio SICURO per rispondere:
   - Nessuna risposta giusta o sbagliata
   - "Non c'è risposta giusta, sono curioso"
   - Rispetta tutte le opinioni

4. POI RISPONDI AI COMMENTI:
   - L'engagement vero viene dalla conversazione
   - Rispondi a tutti, crea dialogo

ESEMPI DI TONO GIUSTO:
✅ "Una cosa su cui rifletto spesso: [domanda]. Voi come la vedete?"
✅ "Sono curioso: nella vostra esperienza, [domanda]?"
❌ "🗳️ A o B??? VOTA NEI COMMENTI!!! 👇👇👇"

Scrivi in italiano, curiosità genuina.
`,
    textPrompt: `Fai una domanda che ti interessa davvero. Qualcosa su cui vuoi sentire cosa pensano gli altri.`,
    imageStyle: 'conversation starter, question mark, thought bubble',
    mood: 'curious and open, inviting discussion',
    platforms: ['instagram', 'linkedin', 'twitter', 'threads'],
    hashtags: ['#Discussione', '#VostraOpinione'],
    ctaOptions: [
      'Raccontami nei commenti',
      'Tu come la vedi?',
      'Mi interessa la tua esperienza',
    ],
  },

  // TESTIMONIAL
  {
    id: 'testimonial',
    label: '⭐ Testimonial',
    value: 'Condivisione di un feedback ricevuto',
    category: 'social',
    postType: 'testimonial',
    icon: '⭐',
    structure: {
      hook: 'La parola al cliente',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 3,
      emojiLevel: 'low',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== TIPO DI CONTENUTO: TESTIMONIAL ===

Stai condividendo un feedback che ti ha fatto piacere.
Non per vantarti, ma per ringraziare e mostrare che il lavoro ha senso.

COME SCRIVERE QUESTO POST:

1. LASCIA PARLARE IL CLIENTE:
   - La citazione è il cuore del post
   - Non modificarla per farla sembrare "marketing"
   - L'autenticità si sente

2. AGGIUNGI il TUO commento con GRATITUDINE:
   - "Ricevere messaggi così mi ricorda perché faccio questo lavoro"
   - "Grazie [nome] per la fiducia"
   - Non "Ecco l'ennesimo cliente soddisfatto!"

3. CONTESTUALIZZA (brevemente):
   - Chi è questa persona (con permesso)
   - Quale problema aveva
   - Ma senza trasformarlo in un case study

4. NON CHIEDERE nulla:
   - Questo post è per ringraziare, non per vendere
   - La CTA implicita è sufficiente

ESEMPI DI TONO GIUSTO:
✅ "Stamattina ho ricevuto questo messaggio. Non ho parole, solo gratitudine."
✅ "Quando un cliente ti scrive così, capisci che ne è valsa la pena."
❌ "⭐⭐⭐⭐⭐ ECCO COSA DICONO I NOSTRI CLIENTI! ANCHE TU PUOI OTTENERE QUESTI RISULTATI!"

Scrivi in italiano, gratitudine sincera.
`,
    textPrompt: `Condividi un feedback ricevuto con gratitudine sincera. Lascia che parli da solo.`,
    imageStyle: 'screenshot of real message, authentic testimonial card',
    mood: 'grateful and humbled, not boastful',
    platforms: ['linkedin', 'instagram', 'facebook', 'threads'],
    hashtags: ['#Grazie', '#Feedback'],
    ctaOptions: [
      'Grazie per la fiducia',
      'Momenti così danno senso al lavoro',
    ],
  },
];

// ============================================================================
// VIDEO SCRIPT TEMPLATES - Script per Video Autentici
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
      hook: 'Inizio conversazionale',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 3,
      emojiLevel: 'low',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== SCRIPT VIDEO: LANCIO PRODOTTO (30-60 sec) ===

Stai registrando un video dove presenti qualcosa di nuovo.
NON è uno spot pubblicitario. È come se stessi parlando a un amico.

COME SCRIVERE LO SCRIPT:

APERTURA (5-10 sec):
- Inizia come inizieresti una conversazione
- "Devo mostrarvi una cosa su cui ho lavorato..."
- "Ok, finalmente posso parlarne..."
- NON "Ciao a tutti! Oggi vi presento..."

CORPO (20-40 sec):
- Racconta PERCHÉ l'hai creato, non COSA fa
- Parla del problema che risolveva per te o per i clienti
- Mostra, non elencare feature
- Usa pause naturali, non tutto d'un fiato

CHIUSURA (5-10 sec):
- Conversazionale, non venditore
- "Se vi interessa, trovate il link in bio"
- "Fatemi sapere cosa ne pensate"
- NON "ACQUISTA ORA! OFFERTA LIMITATA!"

TONO:
- Come se stessi registrando un vocale per un amico
- Puoi fare errori, correggiti naturalmente
- Mostra entusiasmo genuino, non forzato
`,
    textPrompt: `Scrivi uno script video come se stessi registrando un messaggio per un amico a cui vuoi mostrare qualcosa di cui sei orgoglioso.`,
    imageStyle: 'authentic video thumbnail, real person, genuine expression',
    mood: 'excited but genuine, conversational',
    platforms: ['instagram', 'tiktok', 'youtube', 'linkedin'],
    hashtags: ['#NuovoProgetto', '#FattoInItalia'],
    ctaOptions: [
      'Link in bio se vuoi saperne di più',
      'Dimmi cosa ne pensi nei commenti',
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
      hook: 'Problema che risolvi',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 4,
      emojiLevel: 'low',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== SCRIPT VIDEO: TUTORIAL (60-120 sec) ===

Stai insegnando qualcosa a qualcuno che è seduto accanto a te.
Non stai facendo un corso, stai aiutando.

COME SCRIVERE LO SCRIPT:

APERTURA (5-10 sec):
- Parti dal problema, non dalla soluzione
- "Sai quando [problema frustrante]? Ho trovato un trucco..."
- "Questa cosa mi faceva impazzire finché..."
- NON "Oggi imparerete 5 step per..."

SPIEGAZIONE (40-90 sec):
- Parla mentre fai, non dopo
- "Ecco, vedete? Faccio così perché..."
- Anticipa gli errori comuni: "Occhio a non fare questo..."
- Se sbagli qualcosa, lascialo: "Ops, visto? Ecco perché dico di..."

CHIUSURA (5-15 sec):
- Verifica che abbiano capito
- "Provate e poi ditemi se funziona anche per voi"
- Offri aiuto: "Se avete dubbi, chiedete pure"
- NON "Iscrivetevi e attivate la campanella!"

TONO:
- Amichevole, paziente, non saccente
- Come spiegheresti a un collega
- Empatia con chi sta imparando
`,
    textPrompt: `Scrivi un tutorial come se stessi mostrando qualcosa a un collega seduto accanto a te. Semplice, diretto, empatico.`,
    imageStyle: 'screen recording with friendly face, natural setting',
    mood: 'helpful mentor, patient teacher',
    platforms: ['instagram', 'tiktok', 'youtube'],
    hashtags: ['#Tutorial', '#ImparaConMe', '#Trucchi'],
    ctaOptions: [
      'Prova e fammi sapere se funziona',
      'Quale tutorial vuoi vedere?',
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
      hook: 'La storia del cliente',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 3,
      emojiLevel: 'none',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== SCRIPT VIDEO: TESTIMONIAL (45-90 sec) ===

Questo NON è un video promozionale. È la storia VERA di una persona.
Il tuo lavoro è farla raccontare nel modo più autentico possibile.

COME SCRIVERE LO SCRIPT (domande per il cliente):

APERTURA:
- Non presentazioni formali
- "Ciao, sono [Nome], ho un [tipo attività]..."
- Lascia che si presenti come vuole

LA STORIA:
- "Com'era la situazione prima?"
- Non chiedere "Qual era il problema?" (troppo leading)
- Lascia emergere le difficoltà naturalmente

LA SVOLTA:
- "Cosa ti ha fatto decidere di provare?"
- "Com'è stato il processo?"
- Cerchiamo i momenti di umanità, non solo risultati

OGGI:
- "Com'è adesso?"
- Non "Quali risultati hai ottenuto?" (troppo marketing)
- I numeri emergono se sono rilevanti per loro

CHIUSURA:
- "Cosa diresti a chi è nella stessa situazione?"
- Lascia spazio a consigli genuini
- NON far dire "Consigliatissimo!" (suona finto)

REGOLE:
- Niente script rigido, lascia parlare
- Mantieni le imperfezioni, le pause, le emozioni
- Se piangono o ridono, è oro
- L'autenticità vale più della perfezione
`,
    textPrompt: `Prepara domande per far emergere una storia vera, non uno spot. L'autenticità è tutto.`,
    imageStyle: 'real person in real environment, natural lighting, genuine',
    mood: 'authentic story, real emotions, no polish',
    platforms: ['linkedin', 'youtube', 'facebook'],
    hashtags: ['#StoriaVera', '#Testimonial'],
    ctaOptions: [
      'Grazie per aver condiviso la tua storia',
    ],
  },
  {
    id: 'video_trend',
    label: '🔥 Trend/Opinione',
    value: 'Riflessione video su un trend o tema',
    category: 'video',
    postType: 'trend_settore',
    icon: '🔥',
    structure: {
      hook: 'Opinione personale',
      bodyPoints: 0,
      ctaRequired: false,
      hashtagCount: 4,
      emojiLevel: 'low',
    },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== SCRIPT VIDEO: TREND/OPINIONE (30-60 sec) ===

Stai condividendo un'opinione o riflessione su qualcosa che sta succedendo.
NON è un report, è il TUO punto di vista.

COME SCRIVERE LO SCRIPT:

APERTURA (5-10 sec):
- Entra subito nell'argomento
- "C'è una cosa che mi sta facendo riflettere..."
- "Ho notato una cosa interessante..."
- NON "Oggi parliamo del trend X che..."

SVILUPPO (20-40 sec):
- Condividi la TUA opinione, non fatti generici
- "Secondo me questo significa che..."
- "Non sono sicuro, ma credo che..."
- Ammetti dubbi, non avere tutte le risposte

CHIUSURA (5-10 sec):
- Apri la discussione
- "Voi come la vedete?"
- "Sto sbagliando qualcosa?"
- NON "Seguitemi per altri insight!"

TONO:
- Pensieroso, riflessivo
- Come un'opinione condivisa a cena
- Okay essere controversi, ma rispettosi
- Autenticità > Viralità
`,
    textPrompt: `Condividi un'opinione su qualcosa che ti sta facendo riflettere. Sii genuino, anche se controverso.`,
    imageStyle: 'talking head, thoughtful expression, simple background',
    mood: 'thoughtful, opinionated but humble',
    platforms: ['instagram', 'tiktok', 'linkedin', 'youtube'],
    hashtags: ['#Riflessioni', '#Opinione', '#Trend'],
    ctaOptions: [
      'Tu come la vedi?',
      'Sono curioso della vostra opinione',
    ],
  },
];

// ============================================================================
// STORY TEMPLATES - Storie Autentiche
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
    id: 'pensiero_giorno',
    name: 'Pensiero del Giorno',
    preview: '💭',
    category: 'quote',
    structure: { slides: 1, hasCTA: false, hasSwipeUp: false },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== STORY: PENSIERO DEL GIORNO ===

Una storia semplice con un pensiero genuino.
Come un post-it mentale che condividi.

COME SCRIVERE:
- Un pensiero breve e autentico
- Qualcosa che ti ha colpito oggi
- Una riflessione personale
- NON citazioni famose banali

ESEMPIO TONO GIUSTO:
✅ "Oggi ho capito una cosa: non devo avere tutte le risposte. Basta fare il passo successivo."
❌ "Chi ha il coraggio di sognare, ha il coraggio di vincere. - Qualcuno"

Breve, personale, vero.
`,
    visualStyle: {
      primaryColor: '#FAFAFA',
      secondaryColor: '#0A0A0A',
      fontStyle: 'minimal',
    },
  },
  {
    id: 'dietro_le_quinte',
    name: 'Dietro le Quinte',
    preview: '📸',
    category: 'engagement',
    structure: { slides: 1, hasCTA: false, hasSwipeUp: false },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== STORY: DIETRO LE QUINTE ===

Mostra qualcosa di reale del tuo lavoro/giornata.
Come mostreresti il telefono a un amico.

COME SCRIVERE:
- Breve descrizione di cosa stai facendo
- Tono casual, come un messaggio
- Emoji naturali, non forzate
- Invita a rispondere: "Anche voi?" o sticker domanda

ESEMPIO TONO GIUSTO:
✅ "Terzo caffè. Questa presentazione non si scrive da sola 😅"
❌ "📸 ECCO IL NOSTRO TEAM AL LAVORO! #WorkHard #Dedication"

Autentico, veloce, relatable.
`,
    visualStyle: {
      primaryColor: '#0A0A0A',
      secondaryColor: '#FAFAFA',
      fontStyle: 'playful',
    },
  },
  {
    id: 'tip_veloce',
    name: 'Tip Veloce',
    preview: '💡',
    category: 'tip',
    structure: { slides: 2, hasCTA: true, hasSwipeUp: false },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== STORY: TIP VELOCE (2 slide) ===

Un consiglio rapido in formato story.
Valore in 15 secondi di lettura.

SLIDE 1:
- Il problema/situazione
- Breve, diretto
- Es: "Quando [problema comune]..."

SLIDE 2:
- La soluzione/tip
- Applicabile subito
- Invito a salvare o condividere

TONO:
- Amichevole, non professorale
- Come un consiglio dato al volo
- Emoji moderate

Utile, veloce, memorabile.
`,
    visualStyle: {
      primaryColor: '#D4AF37',
      secondaryColor: '#0A0A0A',
      fontStyle: 'minimal',
    },
  },
  {
    id: 'annuncio',
    name: 'Annuncio/News',
    preview: '📢',
    category: 'announcement',
    structure: { slides: 2, hasCTA: true, hasSwipeUp: true },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== STORY: ANNUNCIO (2 slide) ===

Hai qualcosa da annunciare.
Fallo con entusiasmo genuino, non da comunicato stampa.

SLIDE 1:
- L'annuncio in modo diretto
- Entusiasmo personale
- Es: "Finalmente posso dirlo..."

SLIDE 2:
- Dettagli essenziali
- Come saperne di più
- Link o CTA naturale

TONO:
- Entusiasta ma non urlato
- Personale, non aziendale
- Come annunciare a un gruppo di amici

Genuino, chiaro, entusiasta.
`,
    visualStyle: {
      primaryColor: '#D4AF37',
      secondaryColor: '#0A0A0A',
      fontStyle: 'bold',
    },
  },
  {
    id: 'domanda_community',
    name: 'Domanda alla Community',
    preview: '🗣️',
    category: 'engagement',
    structure: { slides: 1, hasCTA: true, hasSwipeUp: false },
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== STORY: DOMANDA ALLA COMMUNITY ===

Vuoi sapere cosa pensano i tuoi follower.
Usa sticker sondaggio o domanda.

COME SCRIVERE:
- Domanda genuina, non retorica
- Qualcosa che ti interessa davvero
- Spiega brevemente perché chiedi
- Usa sticker interattivo

ESEMPIO TONO GIUSTO:
✅ "Sto pensando a una cosa. Voi preferite [A] o [B]? Mi serve il vostro parere!"
❌ "SONDAGGIO! VOTATE! A o B??? 🔥🔥🔥"

Curioso, inclusivo, genuino.
`,
    visualStyle: {
      primaryColor: '#FAFAFA',
      secondaryColor: '#D4AF37',
      fontStyle: 'playful',
    },
  },
];

// ============================================================================
// CAROUSEL TEMPLATES - Carousel Autentici
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
    id: 'carousel_storia',
    name: 'Racconta una Storia',
    icon: '📖',
    slides: 5,
    category: 'carousel',
    structure: [
      { type: 'hook', title: 'Inizio', description: 'Apri con un momento/problema' },
      { type: 'content', title: 'Sviluppo 1', description: 'Cosa è successo' },
      { type: 'content', title: 'Sviluppo 2', description: 'La svolta' },
      { type: 'content', title: 'Conclusione', description: 'Come è finita' },
      { type: 'cta', title: 'Riflessione', description: 'Cosa ho imparato' },
    ],
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== CAROUSEL: RACCONTA UNA STORIA ===

Un carousel che racconta una storia vera, come fosse un mini-blog.
Ogni slide è un capitolo, ma leggibile anche da solo.

SLIDE 1 - L'INIZIO:
- Parti dal momento, non dal contesto
- "Era un martedì normale quando..."
- "Non me l'aspettavo, ma..."
- Cattura l'attenzione con onestà

SLIDE 2-3 - LO SVILUPPO:
- Racconta cosa è successo
- Dettagli concreti che fanno vedere la scena
- Emozioni genuine
- Difficoltà affrontate

SLIDE 4 - LA SVOLTA:
- Il momento in cui qualcosa cambia
- Cosa hai capito/fatto di diverso
- Il turning point della storia

SLIDE 5 - LA RIFLESSIONE:
- Cosa hai imparato
- Cosa significa per chi legge
- Invito a condividere esperienze simili
- NO vendita, solo connessione umana

TONO:
- Come racconteresti a un amico
- Vulnerabile quando serve
- Specifico, non generico
`,
  },
  {
    id: 'carousel_lezioni',
    name: 'Lezioni Apprese',
    icon: '💡',
    slides: 6,
    category: 'carousel',
    structure: [
      { type: 'hook', title: 'Titolo', description: 'X cose che ho imparato da...' },
      { type: 'tip', title: 'Lezione 1', description: 'Prima lezione' },
      { type: 'tip', title: 'Lezione 2', description: 'Seconda lezione' },
      { type: 'tip', title: 'Lezione 3', description: 'Terza lezione' },
      { type: 'tip', title: 'Lezione 4', description: 'Quarta lezione' },
      { type: 'cta', title: 'Conclusione', description: 'Invito alla discussione' },
    ],
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== CAROUSEL: LEZIONI APPRESE ===

Condividi lezioni vere dalla tua esperienza.
Non "5 tips per..." ma "5 cose che ho capito dopo..."

SLIDE 1 - COVER:
- Titolo personale, non generico
- "5 cose che ho capito dopo 10 anni di..."
- "Quello che nessuno mi aveva detto su..."
- Sottotitolo che incuriosisce

SLIDE 2-5 - LE LEZIONI:
- Una lezione per slide
- Parti dall'errore o dalla sorpresa
- Spiega COME l'hai imparata
- Rendi applicabile per chi legge
- NON liste generiche da Google

SLIDE 6 - CHIUSURA:
- Riflessione personale finale
- Invito a condividere le loro lezioni
- "Quale aggiungeresti tu?"
- NO CTA commerciali

TONO:
- Riflessivo, maturo
- Umile - ammetti cosa non sapevi
- Generoso - condividi davvero
`,
  },
  {
    id: 'carousel_processo',
    name: 'Il Mio Processo',
    icon: '🔧',
    slides: 5,
    category: 'carousel',
    structure: [
      { type: 'hook', title: 'Intro', description: 'Cosa fai e come' },
      { type: 'content', title: 'Step 1', description: 'Primo passo' },
      { type: 'content', title: 'Step 2', description: 'Secondo passo' },
      { type: 'content', title: 'Step 3', description: 'Terzo passo' },
      { type: 'cta', title: 'Risultato', description: 'Cosa si ottiene' },
    ],
    aiPrompt: `
${HUMAN_WRITING_MASTER_PROMPT}

=== CAROUSEL: IL MIO PROCESSO ===

Mostra come fai qualcosa. Trasparenza sul tuo metodo.
Non per vendere, ma per condividere conoscenza.

SLIDE 1 - INTRO:
- Cosa stai per mostrare
- Perché lo condividi
- "Vi faccio vedere come lavoro su..."
- Contestualizza brevemente

SLIDE 2-4 - IL PROCESSO:
- Un passo per slide
- Concreto, specifico
- Mostra anche le difficoltà
- Spiega il PERCHÉ, non solo il COSA
- Tools o metodi che usi (senza essere uno spot)

SLIDE 5 - RISULTATO/RIFLESSIONE:
- Cosa si ottiene seguendo questo processo
- Varianti possibili
- "Tu come lo fai?"
- Apertura alla discussione

TONO:
- Come mostrare a un collega
- Pratico e utile
- Onesto su pro e contro
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
 * Ottiene il MASTER PROMPT per output umani
 */
export function getHumanWritingPrompt(): string {
  return HUMAN_WRITING_MASTER_PROMPT;
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
