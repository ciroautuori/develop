# 🌟 **ISS - Innovazione Sociale Salernitana APS-ETS**
## 📖 **Guida Completa per il Team Frontend**

---

## 🚀 **VISION DEL PROGETTO**

**ISS (Innovazione Sociale Salernitana)** è un'**Associazione di Promozione Sociale** attiva nel territorio salernitano che promuove **inclusione e innovazione digitale**, con una piattaforma digitale rivoluzionaria che serve una **doppia mission**:

### **🎯 MISSION 1: APS ATTIVA - Inclusione Digitale Territoriale**
ISS opera direttamente sul territorio con **attività concrete di inclusione digitale**:
- **📚 Corsi di Alfabetizzazione Digitale** per cittadini, anziani e categorie vulnerabili
- **♿ Formazione Professionale Inclusiva** per persone con disabilità e tecnologie assistive
- **💼 Supporto Istruzione e Riorientamento Professionale** nel settore digitale
- **🔬 Laboratori di Formazione Digitale** dall'approccio base all'avanzato
- **💡 Innovazione Sociale tramite Tecnologia** con hackathon e competizioni per soluzioni sociali

### **🌐 MISSION 2: HUB REGIONALE - Sistema Bandi Automatizzato**
ISS diventa il **punto di riferimento regionale per l'accesso ai bandi di finanziamento** per tutte le APS campane, democratizzando l'accesso alle opportunità di finanziamento.

### **🎯 OBIETTIVI UTENTE DOPPI**

**👤 UTENTI TIPO 1 - Cittadini Salernitani (Target ISS diretto)**
- Anziani che vogliono imparare ad usare smartphone/computer
- Persone con disabilità che cercano formazione e tecnologie assistive  
- Disoccupati che vogliono riqualificarsi nel digitale
- Giovani interessati a hackathon e innovazione sociale

**👥 UTENTI TIPO 2 - APS Campane (Target Hub Bandi)**
- Presidenti e segretari di APS che cercano finanziamenti
- Volontari che gestiscono ricerca bandi per l'organizzazione
- Operatori del terzo settore che monitorano opportunità

---

## 🏗️ **ARCHITETTURA DEL SISTEMA**

### **📁 Struttura del Progetto**
```
/iss/
├── 🔧 apps/backend/          # API FastAPI + Sistema Bandi
├── 🎨 apps/frontend/         # Interfaccia React/Next.js (DA SVILUPPARE)
├── 🤖 iss-bot/              # Bot monitoraggio bandi (INTEGRATO)
├── 🎨 logo/                 # Brand assets
└── 📋 docs/                 # Documentazione
```

### **🔧 Stack Tecnologico Backend (GIÀ SVILUPPATO)**
- **FastAPI** + **SQLAlchemy** + **PostgreSQL**
- **Redis** per caching e rate limiting
- **Docker** containerizzato
- **Sistema di monitoring automatico 24/7**
- **API REST complete e testate (61/61 test passano)**

---

## 🎯 **SISTEMA BANDI - IL CUORE DEL PROGETTO**

### **💡 CONCEPT RIVOLUZIONARIO**

Il sistema bandi di ISS rappresenta una **innovazione disruptive** nel settore del terzo settore:

1. **🔍 Ricerca Intelligente**: Algoritmi avanzati per trovare bandi pertinenti
2. **⚡ Monitoraggio Automatico**: Scraping 24/7 di fonti ufficiali
3. **📱 Notifiche Real-time**: Alert via email e Telegram
4. **🎯 Personalizzazione**: Filtri per keywords, enti, tipologie
5. **📊 Analytics**: Statistiche e trends sui bandi disponibili

### **🌐 FONTI MONITORATE**
- **Comune di Salerno** (priorità alta)
- **Regione Campania** (priorità alta)  
- **CSV Salerno** (Centro Servizi Volontariato)
- **Fondazione Comunità Salernitana**
- **Fonti aggiuntive** (espandibili)

### **📈 IMPATTO SOCIALE ATTESO**
- **500+ APS** potenzialmente servite nella provincia
- **Aumento del 300%** nell'accesso ai finanziamenti
- **Riduzione del 80%** del tempo di ricerca bandi
- **Democratizzazione** dell'accesso alle opportunità

---

## 🔌 **API ENDPOINTS - SISTEMA BANDI**

### **📡 API PUBBLICHE (Per Frontend)**

#### **1. 📊 Statistiche Bandi**
```http
GET /api/v1/bandi/stats
```
**Response:**
```json
{
  "total_bandi": 245,
  "attivi": 89,
  "scaduti": 156,
  "per_fonte": {
    "comune_salerno": 45,
    "regione_campania": 123,
    "csv_salerno": 67,
    "fondazione_comunita": 10
  },
  "keywords_top": ["inclusione sociale", "giovani", "digitale"]
}
```

#### **2. 🔍 Ricerca Bandi**
```http
GET /api/v1/bandi/?query=giovani&fonte=comune_salerno&status=attivo&skip=0&limit=20
```
**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Bando Giovani Protagonisti 2025",
      "ente": "Comune di Salerno",
      "descrizione": "Supporto progetti giovanili...",
      "link": "https://comune.salerno.it/bando-123",
      "fonte": "comune_salerno",
      "status": "attivo",
      "scadenza": "2025-12-31T23:59:59Z",
      "importo_max": 50000,
      "keywords": ["giovani", "inclusione", "digitale"],
      "created_at": "2025-09-23T08:30:00Z"
    }
  ],
  "total": 89,
  "page": 1,
  "pages": 5
}
```

#### **3. 📝 Dettagli Bando**
```http
GET /api/v1/bandi/{id}
```

#### **4. 🕒 Bandi Recenti**
```http
GET /api/v1/bandi/recent?limit=10
```

#### **5. 🏷️ Filtri Disponibili**
```http
GET /api/v1/bandi/filters
```
**Response:**
```json
{
  "fonti": ["comune_salerno", "regione_campania", "csv_salerno"],
  "status": ["attivo", "scaduto", "archiviato"],
  "keywords_popolari": ["giovani", "inclusione sociale", "digitale", "cultura"]
}
```

---

## 🎓 **API ENDPOINTS - ATTIVITÀ ISS APS**

### **📚 API Corsi e Formazione**

#### **1. 📊 Corsi Disponibili**
```http
GET /api/v1/corsi/?categoria=alfabetizzazione&status=attivo&skip=0&limit=20
```
**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "titolo": "Alfabetizzazione Digitale per Anziani",
      "categoria": "alfabetizzazione",
      "descrizione": "Corso base per imparare ad usare smartphone e tablet",
      "data_inizio": "2025-10-15T09:00:00Z",
      "data_fine": "2025-11-15T11:00:00Z",
      "durata_ore": 20,
      "posti_disponibili": 12,
      "posti_totali": 15,
      "prezzo": 0,
      "docente": "Mario Rossi",
      "sede": "Centro ISS - Via Roma 123, Salerno",
      "requisiti": ["Nessun prerequisito"],
      "materiali_inclusi": true,
      "certificazione": true
    }
  ],
  "total": 8,
  "categorie": ["alfabetizzazione", "professionale", "assistive", "avanzato"]
}
```

#### **2. 🎯 Progetti Attivi**
```http
GET /api/v1/progetti/?tipo=inclusione&status=attivo
```
**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "nome": "Salerno Digitale Inclusiva",
      "tipo": "inclusione",
      "descrizione": "Progetto per l'inclusione digitale di persone con disabilità",
      "obiettivi": ["Formare 100 persone", "Creare 5 laboratori", "Sviluppare app accessibile"],
      "data_inizio": "2025-09-01T00:00:00Z",
      "data_fine": "2026-08-31T23:59:59Z",
      "budget": 85000,
      "partner": ["Comune di Salerno", "ASL Salerno", "Università di Salerno"],
      "beneficiari_target": 100,
      "beneficiari_raggiunti": 23,
      "status": "in_progress",
      "referente": "Anna Bianchi"
    }
  ]
}
```

#### **3. 📅 Eventi e Workshop**
```http
GET /api/v1/eventi/?tipo=hackathon&data_da=2025-10-01
```
**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "titolo": "Hackathon Sociale Salerno 2025",
      "tipo": "hackathon",
      "descrizione": "48 ore per sviluppare soluzioni innovative ai problemi sociali della città",
      "data_evento": "2025-11-15T09:00:00Z",
      "data_fine": "2025-11-17T18:00:00Z",
      "luogo": "Stazione Marittima Salerno",
      "partecipanti_max": 150,
      "iscrizioni_aperte": true,
      "quota_partecipazione": 25,
      "premi": [
        {"posizione": 1, "premio": "€2000 + incubazione"},
        {"posizione": 2, "premio": "€1000"},
        {"posizione": 3, "premio": "€500"}
      ],
      "sponsor": ["Tech Company Salerno", "Banca Campania"],
      "tema": "Inclusione sociale attraverso la tecnologia"
    }
  ]
}
```

### **👥 API Volontariato e Community**

#### **4. 🤝 Opportunità Volontariato**
```http
GET /api/v1/volontariato/?area=formazione&tipo=continuativo
```
**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "titolo": "Tutor Corsi Alfabetizzazione",
      "area": "formazione",
      "tipo": "continuativo",
      "descrizione": "Cerchiamo volontari per supportare anziani nei corsi di alfabetizzazione digitale",
      "competenze_richieste": ["Pazienza", "Conoscenze informatiche base", "Empatia"],
      "tempo_richiesto": "4 ore/settimana",
      "sede": "Centro ISS + Domicilio",
      "formazione_prevista": true,
      "contatto": "volontariato@iss-salerno.it",
      "scadenza_candidatura": "2025-12-31T23:59:59Z"
    }
  ]
}
```

---

## 🎨 **LINEE GUIDA UX/UI PER IL FRONTEND**

### **🎯 OBIETTIVI UTENTE DOPPI**

#### **👤 OBIETTIVI UTENTI ISS (Cittadini Salernitani)**
1. **📚 Learning**: Trovare corsi di formazione digitale adatti
2. **🎯 Participation**: Iscriversi a eventi, hackathon, workshop
3. **🤝 Volunteering**: Candidarsi come volontario per progetti sociali
4. **📊 Progress**: Monitorare il proprio percorso formativo
5. **🌐 Community**: Sentirsi parte della comunità ISS

#### **👥 OBIETTIVI UTENTI HUB BANDI (APS Campane)**  
1. **👀 Discovery**: Trovare rapidamente bandi pertinenti alla propria APS
2. **🔍 Search**: Ricerca avanzata con filtri per tipo, ente, scadenza
3. **📊 Monitor**: Monitorare nuovi bandi e scadenze importanti
4. **📱 Alerts**: Ricevere notifiche personalizzate per keywords
5. **📈 Analytics**: Visualizzare trends e statistiche sui finanziamenti

### **🏗️ COMPONENTI CHIAVE DA SVILUPPARE**

#### **1. 🔍 Dual SearchBar System**
```jsx
// Per Hub Bandi
<BandoSearchBar 
  placeholder="Cerca bandi per parole chiave, ente, categoria..."
  onSearch={handleBandoSearch}
  suggestions={bandoSuggestions}
  filters={bandoFilters}
/>

// Per Attività ISS  
<ISSSearchBar 
  placeholder="Cerca corsi, eventi, progetti..."
  onSearch={handleISSSearch}
  suggestions={issSuggestions}
  categories={["corsi", "eventi", "progetti", "volontariato"]}
/>
```

#### **2. 🃏 Dual Card Components**
```jsx
// Per Bandi (APS esterne)
<BandoCard 
  bando={bandoData}
  showStatus={true}
  showScadenza={true}
  onSave={handleSave}
  onShare={handleShare}
/>

// Per Corsi ISS
<CorsoCard 
  corso={corsoData}
  showPosti={true}
  showPrezzo={true}
  onIscrizione={handleIscrizione}
  onInfo={handleInfo}
/>

// Per Eventi ISS
<EventoCard 
  evento={eventoData}
  showData={true}
  showPosti={true}
  onPartecipa={handlePartecipa}
  onCondividi={handleCondividi}
/>

// Per Progetti ISS
<ProgettoCard 
  progetto={progettoData}
  showProgress={true}
  showPartner={true}
  onDettagli={handleDettagli}
  onVolontariato={handleVolontariato}
/>
```

#### **3. 📊 Dual Dashboard System**
```jsx
// Dashboard Bandi (per APS esterne)
<BandoStats 
  data={bandoStatsData}
  charts={["pie", "timeline", "bars"]}
  period="last_30_days"
  kpis={["total_bandi", "attivi", "scadenti"]}
/>

// Dashboard ISS (attività interne)
<ISSStats 
  data={issStatsData}
  charts={["corsi_completati", "eventi_partecipazione", "progetti_progress"]}
  kpis={["studenti_formati", "eventi_organizzati", "volontari_attivi"]}
  period="current_year"
/>
```

#### **4. 🔔 Notification System**
```jsx
<NotificationSettings 
  keywords={userKeywords}
  sources={selectedSources}
  frequency="daily"
  methods={["email", "telegram"]}
/>
```

### **🎨 DESIGN SYSTEM SUGGERITO**

#### **🎨 Palette Colori**
```css
:root {
  --primary: #2563eb;        /* Blu professionale */
  --secondary: #059669;      /* Verde successo */
  --accent: #dc2626;         /* Rosso urgenza */
  --warning: #f59e0b;        /* Arancione scadenza */
  --neutral: #6b7280;        /* Grigio testi */
  --background: #f9fafb;     /* Sfondo chiaro */
}
```

#### **📱 Breakpoints Responsive**
```css
/* Mobile First Approach */
.container {
  /* Mobile: 320px+ */
  padding: 1rem;
  
  /* Tablet: 768px+ */
  @media (min-width: 768px) {
    padding: 2rem;
    display: grid;
    grid-template-columns: 1fr 3fr;
  }
  
  /* Desktop: 1024px+ */
  @media (min-width: 1024px) {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

---

## 📄 **PAGINE PRINCIPALI DA SVILUPPARE**

### **1. 🏠 Homepage Dual-Purpose**
```
/
├── Hero Section (Doppio messaggio: ISS APS + Hub Bandi)
├── Quick Navigation (Cittadini ISS | APS Partner)
├── Sezione ISS APS:
│   ├── Prossimi Corsi (3 in evidenza)
│   ├── Eventi in Programma (hackathon, workshop)
│   └── Progetti Attivi (con progresso visuale)
├── Sezione Hub Bandi:
│   ├── Statistiche Live (total bandi, nuovi oggi)
│   ├── Bandi in Scadenza (urgenti)
│   └── Bandi in Evidenza (pertinenti)
├── Impact Numbers (studenti formati, bandi trovati)
├── Come Funziona (processo dual per entrambi i target)
└── Testimonianze (cittadini ISS + APS partner)
```

### **2. 🔍 Pagine Ricerca Dual**
```
/bandi (Hub per APS esterne)
├── SearchBar + Filtri Avanzati
├── Risultati con Sorting
├── Paginazione
├── Sidebar con Stats
└── Quick Filters (Attivi, Scadenza Vicina, etc.)

/corsi (Per cittadini ISS)
├── Filtri per Categoria (alfabetizzazione, professionale, etc.)
├── Calendar View disponibilità
├── Filtri per Livello (base, intermedio, avanzato)
├── Posti disponibili real-time
└── Sistema iscrizioni integrato

/eventi (Per cittadini ISS)
├── Calendar View con eventi mensili
├── Filtri per Tipo (hackathon, workshop, conferenze)
├── System RSVP e registrazione
├── Integrazione social sharing
└── Feed aggiornamenti eventi
```

### **3. 📄 Pagine Dettaglio Multiple**
```
/bandi/{id} (Per APS esterne)
├── Header con Status + Scadenza
├── Descrizione Completa
├── Requisiti e Modalità
├── Link Ufficiale + Download
├── Bandi Correlati
└── Azioni (Salva, Condividi, Alert)

/corsi/{id} (Per cittadini ISS)
├── Header con Date + Posti Disponibili
├── Programma Dettagliato
├── Docente e Competenze
├── Prerequisiti e Materiali
├── Sede e Modalità
├── Testimonianze ex-studenti
└── Azioni (Iscriviti, Scarica Programma)

/eventi/{id} (Per cittadini ISS)
├── Header con Data + Location
├── Agenda Dettagliata
├── Speaker e Partner
├── Premi e Riconoscimenti (se hackathon)
├── Come Partecipare
├── Eventi Correlati
└── Azioni (Registrati, Condividi, Aggiungi Calendario)

/progetti/{id} (Per cittadini ISS)
├── Header con Timeline + Budget
├── Obiettivi e Impatto
├── Partner e Collaborazioni
├── Progress Tracker
├── Come Contribuire/Volontariato
├── Updates e News
└── Azioni (Candidati, Dona, Condividi)
```

### **4. 📊 Dashboard Analytics**
```
/analytics
├── Charts Interattivi
├── Trends Temporali
├── Distribuzione per Fonte
├── Keywords più Ricercate
└── Export Dati
```

### **5. ⚙️ Configurazione Alerts**
```
/alerts
├── Form Keywords Personalizzate
├── Selezione Fonti
├── Frequenza Notifiche
├── Canali (Email/Telegram)
└── Preview Notifiche
```

---

## 📊 **ESEMPI DI IMPLEMENTAZIONE**

### **🔍 Ricerca con Filtri**
```jsx
const BandoSearch = () => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({
    fonte: 'all',
    status: 'attivo',
    scadenza: 'prossimi_30_giorni'
  });
  
  const { data, loading, error } = useBandoSearch({
    query,
    ...filters,
    page: currentPage
  });
  
  return (
    <div className="bando-search">
      <SearchFilters 
        filters={filters}
        onChange={setFilters}
      />
      <BandoResults 
        bandi={data?.items || []}
        loading={loading}
        total={data?.total}
        onPageChange={setCurrentPage}
      />
    </div>
  );
};
```

### **📊 Dashboard Stats**
```jsx
const BandoStatsView = () => {
  const { stats } = useBandoStats();
  
  return (
    <div className="stats-grid">
      <StatCard
        title="Bandi Attivi"
        value={stats.attivi}
        trend="+12%"
        color="green"
      />
      <StatCard
        title="Nuovi Oggi"
        value={stats.nuovi_oggi}
        trend="+5"
        color="blue"
      />
      <PieChart
        data={stats.per_fonte}
        title="Distribuzione per Fonte"
      />
      <TimelineChart
        data={stats.timeline}
        title="Bandi nel Tempo"
      />
    </div>
  );
};
```

---

## 🚀 **ROADMAP IMPLEMENTAZIONE DUAL-PURPOSE**

### **🎯 FASE 1 - Foundation + MVP (2-3 settimane)**
**Priority 1: Sistema Hub Bandi (Core Business)**
- [ ] Setup React 19 + TypeScript 5 + Tailwind v4
- [ ] Sistema autenticazione (cittadini ISS vs APS esterne)
- [ ] Homepage dual-purpose con navigation split
- [ ] Pagina ricerca bandi con filtri avanzati
- [ ] Dashboard bandi con statistiche live
- [ ] Integrazione API bandi completa

**Priority 2: Attività ISS APS**
- [ ] Pagina corsi con sistema iscrizioni
- [ ] Pagina eventi con calendar view
- [ ] Cards per progetti attivi
- [ ] Sistema volontariato base

### **🎯 FASE 2 - CORE FEATURES (3-4 settimane)**
**Sistema Bandi Avanzato:**
- [ ] Dashboard analytics con charts interattivi
- [ ] Sistema notifiche personalizzate (email/telegram)
- [ ] Filtri avanzati e ricerca semantica
- [ ] Export dati e report

**Attività ISS Complete:**
- [ ] Sistema completo iscrizioni corsi
- [ ] Piattaforma eventi con RSVP
- [ ] Dashboard progetti con progress tracking
- [ ] Community volontari con matching

### **🎯 FASE 3 - GROWTH & OPTIMIZATION (2-3 settimane)**
- [ ] PWA con offline support
- [ ] A/B testing per conversioni
- [ ] SEO optimization avanzato
- [ ] Social sharing virale
- [ ] Performance optimization < 2s load
- [ ] Offline support
- [ ] Advanced analytics
- [ ] A/B testing
- [ ] Performance optimization

---

## 🔗 **RISORSE E RIFERIMENTI**

### **📚 Documentazione API**
- **Base URL**: `https://api.iss-salerno.it/api/v1/`
- **Authentication**: Public APIs (no auth required)
- **Rate Limit**: 1000 requests/hour per IP
- **Swagger Docs**: `/docs` (disponibile in sviluppo)

### **🎨 Design Resources**
- **Figma**: [Link al design system]
- **Icons**: Heroicons, Lucide React
- **Charts**: Chart.js, Recharts
- **Components**: Tailwind UI, Headless UI

### **🔧 Tech Stack Suggerito**
```json
{
  "framework": "Next.js 14+",
  "styling": "Tailwind CSS",
  "state": "Zustand / Redux Toolkit",
  "data": "TanStack Query",
  "forms": "React Hook Form",
  "charts": "Chart.js + React-Chartjs-2",
  "testing": "Jest + Testing Library",
  "deployment": "Vercel / Netlify"
}
```

---

## 📞 **SUPPORTO E CONTATTI**

### **👥 Team Backend**
- **API Support**: Documentazione swagger disponibile
- **Database**: PostgreSQL con 61 test passanti al 100%
- **Performance**: Redis caching + rate limiting attivo

### **🚨 PRIORITÀ STRATEGICHE**

> **⚠️ CRITICAL**: Il sistema bandi è la **killer feature** che differenzierà ISS da qualsiasi altro portale. L'implementazione deve essere **user-centric**, **performante** e **accessibile**. Ogni APS della Campania deve poter trovare e accedere facilmente ai bandi pertinenti.

### **🎯 KPI DA MONITORARE**
- **Conversioni**: % utenti che trovano bandi utili
- **Engagement**: Tempo medio sulla ricerca
- **Retention**: Utenti che ritornano per nuove ricerche
- **Social Impact**: Numero di bandi applicati tramite ISS

---

## 🌟 **CONCLUSIONE**

Il progetto ISS rappresenta un'opportunità unica per creare un **impatto sociale misurabile** nel territorio campano. Il sistema bandi non è solo una feature, ma **il cuore pulsante** di una piattaforma che può trasformare il modo in cui le APS accedono ai finanziamenti.

**Il vostro lavoro frontend sarà la chiave per democratizzare l'accesso alle opportunità di finanziamento per centinaia di organizzazioni del terzo settore.**

---

> **💡 Remember**: Ogni bando trovato facilmente attraverso ISS può significare un progetto sociale finanziato, una comunità aiutata, un futuro migliore per il territorio. **Il vostro codice ha un impatto sociale diretto!**

---

**🚀 Happy Coding! Rendiamo Salerno la capitale dell'innovazione sociale digitale!**
