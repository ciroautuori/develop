# 📋 TODOLIST - Debito Tecnico Marketing Hub

> **Data creazione:** 4 Dicembre 2025
> **Priorità:** Alta - Allineamento Design System e UX

---

## 🎨 1. DESIGN SYSTEM - Eliminare il BLU

### Problema
Il blu (`#3B82F6`, `blue-500`, `blue-600`, ecc.) è usato in molte parti del backoffice Marketing ma **NON fa parte del brand StudioCentos**.

### Brand Colors Ufficiali
```
GOLD:     #D4AF37 (primary)
BLACK:    #0A0A0A (dark bg)
WHITE:    #FFFFFF (light bg)
GRAY:     scale neutrale
```

### File da Correggere

#### Marketing Hub Components
- [ ] `EmailCampaignPro.tsx` - Sostituire `blue-500/600` con `gold` o `green-600` per azioni
- [ ] `MarketingAnalyticsPro.tsx` - Tab navigation usa blu, cambiare in gold
- [ ] `SocialPublisherPro.tsx` - Selezione piattaforme e focus rings blu
- [ ] `VideoStoryCreator.tsx` - Platform selection, focus rings
- [ ] `LeadFinderPro.tsx` - Pulsanti e stati hover
- [ ] `ContentSchedulerPro.tsx` - Calendario e stati

#### UI Components Globali
- [ ] `button.tsx` - Verificare varianti default
- [ ] `input.tsx` - Focus rings
- [ ] `select.tsx` - Focus rings
- [ ] `tabs.tsx` - Stati attivi

### Sostituzione Colori
| Vecchio | Nuovo | Uso |
|---------|-------|-----|
| `blue-500` | `gold` | Primary actions, tabs attivi |
| `blue-600` | `gold-dark` o `amber-600` | Hover states |
| `focus:ring-blue-500` | `focus:ring-gold` | Focus rings |
| `border-blue-500` | `border-gold` | Bordi attivi |
| `bg-blue-500/20` | `bg-gold/20` | Background states |

---

## 📱 2. PULSANTI NON RESPONSIVE

### Problema
I pulsanti non rispettano:
- Minimum touch target 44x44px (WCAG)
- Scaling responsive mobile-first
- Design System spacing

### Fix Richiesti

- [ ] Aggiungere `min-h-11 min-w-11` (44px) a tutti i Button
- [ ] Verificare `py-3 px-4` minimum su mobile
- [ ] Testare su viewport 320px-768px
- [ ] Gap tra pulsanti: `gap-3` mobile, `gap-4` desktop

### File da Verificare
- [ ] `button.tsx` - Dimensioni base
- [ ] Tutti i form nel Marketing Hub
- [ ] Modal e dialog actions

---

## 💾 3. DNA BRAND - Persistenza Dati ✅ COMPLETATO

### Problema
Il Brand DNA dovrebbe salvare e persistere:
- Logo aziendale
- Colori brand
- Tone of voice
- Valori aziendali
- Target audience
- Keywords preferite

### Implementazione Completata (4 Dicembre 2025)

- [x] Creare tabella `brand_settings` nel database
- [x] API endpoint `POST/GET /api/v1/marketing/brand-dna`
- [x] Salvare su localStorage come cache
- [x] Caricare automaticamente negli agenti AI (`/brand-dna/ai-context`)
- [x] UI per upload logo (già esisteva, ora salva in DB)

### Files Creati/Modificati

**Backend:**
- `app/domain/marketing/models.py` - Modello `BrandSettings` + enum `ToneOfVoice`
- `app/domain/marketing/schemas.py` - Schemi Pydantic per validazione
- `app/domain/marketing/brand_dna_router.py` - Router API completo
- `alembic/versions/015_brand_settings.py` - Migration

**Frontend:**
- `types/business-dna.types.ts` - Types TypeScript per BrandSettings
- `hooks/marketing/useBrandSettings.ts` - Hook per persistenza con cache localStorage
- `components/BusinessDNAGenerator.tsx` - UI aggiornata con save/load

### Schema Database Proposto
```sql
CREATE TABLE brand_settings (
  id SERIAL PRIMARY KEY,
  admin_id INTEGER REFERENCES admin_users(id),
  logo_url TEXT,
  primary_color VARCHAR(7) DEFAULT '#D4AF37',
  secondary_color VARCHAR(7) DEFAULT '#0A0A0A',
  company_name VARCHAR(255),
  tagline TEXT,
  tone_of_voice VARCHAR(50), -- professional, casual, enthusiastic
  target_audience TEXT,
  keywords JSONB,
  values JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔄 4. SEZIONI MARKETING - Consolidamento ✅ COMPLETATO

### Problema
Troppe sezioni separate che potrebbero essere unificate in modo intelligente.

### Analisi Sezioni Attuali

| Sezione | Funzione | Stato |
|---------|----------|-------|
| Email Campaign Pro | Email marketing | ✅ KEEP |
| Social Publisher Pro | Multi-platform posting | ✅ KEEP |
| Video Story Creator | Video/Stories AI | ✅ KEEP |
| Lead Finder Pro | Ricerca lead | ✅ KEEP |
| Content Scheduler Pro | Calendario editoriale | ✅ KEEP |
| Marketing Analytics Pro | Dashboard metriche | ✅ KEEP |
| AI Chat | Assistente AI | ✅ MOVED → Widget floating |
| Brand DNA | Impostazioni brand | ✅ KEEP (con persistenza DB) |

### Azioni Completate (4 Dicembre 2025)

- [x] **AI Chat** → Rimosso tab da Marketing Hub, ora usa ChatWidget floating
- [x] **Brand DNA** → Persistenza database implementata
- [x] Tab "Chat" eliminato da AIMarketing/index.tsx

### Struttura Attuale

```
Marketing Hub (8 tabs)
├── 📄 Contenuti
├── 🧬 DNA
├── 🎬 Video
├── 📧 Email
├── 📱 Social
├── 📊 Stats
├── 👥 Lead
└── 📅 Cal

+ 💬 AI Chat Widget (floating bottom-right, sempre visibile)
```

---

## 💬 5. AI CHAT - Widget Floating ✅ COMPLETATO

### Soluzione Implementata
Utilizzato il `ChatWidget` esistente in `src/shared/components/ui/chat-widget.tsx` (stesso della landing page).

### Modifiche Effettuate

- [x] Rimosso import `ChatInterface` da AIMarketing/index.tsx
- [x] Rimosso tab 'chat' dall'array tabs
- [x] Rimosso `{activeTab === 'chat' && <ChatInterface />}`
- [x] ChatWidget già presente in AdminShell.tsx

### Posizione Widget
- Desktop: `bottom-8 right-8`
- Mobile: `bottom-6 right-6`
- Z-index: 50 (sempre sopra)
- Button: 64x64px mobile, 56x56px desktop

### UI/UX
```
┌─────────────────────────────┐
│     Marketing Hub           │
│                             │
│     [Content Area]          │
│                             │
│                             │
│                       ┌───┐ │
│                       │💬 │ │  ← Floating button
│                       └───┘ │
└─────────────────────────────┘

Click → Opens drawer:
┌─────────────────────────────┐
│     Marketing Hub           │
├─────────────────────────────┤
│ 💬 AI Assistant        [X]  │
├─────────────────────────────┤
│ User: Come posso...         │
│ AI: Ecco come fare...       │
│                             │
│ [________________] [Send]   │
└─────────────────────────────┘
```

---

## 📋 PRIORITÀ ESECUZIONE

### 🔴 P0 - Critici (Fare Subito)
1. [ ] Eliminare BLU da tutto il backoffice
2. [ ] Fix pulsanti responsive (touch targets)
3. [ ] AI Chat → Widget floating

### 🟡 P1 - Importanti (Questa Settimana)
4. [ ] Brand DNA persistenza database
5. [ ] Consolidare sezioni Marketing

### 🟢 P2 - Miglioramenti (Prossima Settimana)
6. [ ] Review completo Design System
7. [ ] Testing mobile viewport
8. [ ] Performance audit

---

## 🛠️ COMANDI UTILI

```bash
# Trova tutti i blu nel frontend
grep -rn "blue-500\|blue-600\|#3B82F6" apps/frontend/src/

# Trova button senza min-h
grep -rn "Button" apps/frontend/src/ | grep -v "min-h"

# Build e test
cd apps/frontend && npm run type-check && npm run build
```

---

## ✅ COMPLETATI

- [x] Fix 401 Unauthorized su Email/Marketing endpoints (get_current_admin_user)
- [x] Rebuild backend con auth fix
- [x] Rebuild frontend con aggiornamenti

---

> **Nota:** Questo documento viene aggiornato man mano che i task vengono completati.
> Ultimo aggiornamento: 4 Dicembre 2025


# 📋 ANALISI COMPLETA BACKOFFICE - STUDIOCENTOS

**Data**: 2025-01-12
**Versione**: 1.0 - COMPLETA
**Analizzati**: 15 file critici + grep 123 violazioni

---

## 📊 EXECUTIVE SUMMARY

### Problemi Rilevati
| Categoria | Numero Violazioni | Priorità |
|-----------|-------------------|----------|
| 🔵 Colori BLU (VIETATI) | **123+ istanze** | 🔴 CRITICA |
| 📱 Touch Target < 44px | **~40 bottoni** | 🔴 CRITICA |
| 💾 Persistenza DNA | **0% implementato** | 🔴 CRITICA |
| 💬 AI Chat (non floating) | **1 componente** | 🟡 ALTA |
| 🎨 Focus Ring Blue | **15+ componenti** | 🟡 ALTA |
| ♿ Accessibilità WCAG | **~20 problemi** | 🟡 MEDIA |

---

## 🗂️ STRUTTURA ANALIZZATA

\`\`\`
apps/frontend/src/features/admin/
├── layouts/           (2 files) ✅ Analizzati
├── pages/            (19+ files)
│   └── AIMarketing/  (1 index + 17 components) ✅ Analizzati
├── components/       (14 files)
├── hooks/            (4 + 11 marketing) ✅ Parziale
├── services/         (5 files)
└── types/            (vari) ✅
\`\`\`

---

## 📁 ANALISI FILE-BY-FILE

### 1️⃣ LAYOUTS

#### AdminLayout.tsx
**Status**: ⚠️ Possibilmente non usato (vecchio layout)
**Problemi**:
- primary-500, primary-600 - colori ambigui (potrebbero essere blu)
- Struttura più semplice, potrebbe essere stato sostituito da AdminShell

#### AdminShell.tsx ✅
**Status**: ✅ Layout principale - BEN STRUTTURATO
**Punti Positivi**:
- Usa gold per stati attivi (border-gold, bg-gold/10, text-gold)
- Ha min-h-11 per touch targets (44px)
- Mobile drawer responsive con animazioni
- Dark mode support

---

### 2️⃣ AIMarketing Hub

#### AIMarketing/index.tsx
**Status**: ⚠️ Problemi minori
**Violazioni**:
- ❌ focus:ring-blue-500 nel nav tabs
- ✅ Usa correttamente white/10, white/5 per dark mode
- ✅ Responsive con flex-wrap

#### BusinessDNAGenerator.tsx 🔴 CRITICO
**Violazioni Colori**:
- ❌ focus:ring-purple-500 (multiple)
- ❌ from-purple-600 to-indigo-600 gradient
- ❌ bg-blue-900/20, border-blue-800, text-blue-400 (banner info)
- ❌ hover:border-purple-500/50

**PROBLEMA CRITICO - PERSISTENZA**:
- ❌ **NO DATABASE**: Il DNA non viene salvato!
- Solo generazione immagine in-memory
- Hook useBusinessDNA.ts non ha save/load

#### EmailCampaignPro.tsx 🔴
**Violazioni Colori**:
- ❌ focus:ring-blue-500, focus:ring-green-500
- ❌ bg-blue-500/20 border-blue-500/50 (campaign selezionata)
- ❌ text-blue-500 (click rate)
- ❌ animate-spin text-blue-500 (loader)
**Auth**: ✅ Usa admin_token correttamente

#### MarketingAnalyticsPro.tsx 🔴
**Violazioni Colori**:
- ❌ bg-blue-500 tabs e date selector
- ❌ text-blue-500 click rate
- ❌ from-blue-500 to-cyan-500 gradient

#### ChatInterface.tsx 🔴 PROBLEMA ARCHITETTURALE
**Posizione Attuale**: Tab interno a Marketing Hub
**Posizione Richiesta**: Widget floating bottom-right
**Violazioni**:
- ❌ from-blue-500 to-purple-500, from-blue-600 to-purple-600
- ❌ focus:ring-blue-500
**Soluzione**: Usare ChatWidget esistente in src/shared/components/ui/chat-widget.tsx

#### SocialPublisherPro.tsx 🔴
**Violazioni**:
- ❌ border-blue-500 bg-blue-500/10 (platform selected)
- ❌ focus:ring-blue-500 (multiple)
- ❌ bg-blue-500/20 text-blue-300 (hashtag)
- ❌ from-green-600 to-blue-600 (publish button)

#### ContentGenerator.tsx 🔴
**Violazioni**:
- ❌ focus:ring-blue-500 (multiple)
- ❌ border-blue-500 bg-blue-500/10 (content type selected)
- ❌ from-blue-600 to-purple-600 (generate button)

#### LeadFinderPro.tsx ⚠️
**Violazioni**:
- ❌ from-blue-600 to-purple-600 (header, button)
- ❌ focus:ring-blue-500 (selects)
- ❌ border-blue-500 bg-blue-500/10 (result selected)
**Touch Targets**: ✅ Usa min-h-[44px]

#### ImageGenerator.tsx ⚠️
**Violazioni**: ❌ focus:ring-blue-500
**OK**: Usa from-purple-600 to-pink-600 (non blu)

#### VideoStoryCreator.tsx ⚠️
**Violazioni**: ❌ from-blue-500 to-cyan-500
**Note**: Componente ben strutturato con HeyGen integration

---

### 3️⃣ HOOKS CRITICI

#### useBusinessDNA.ts 🔴
**Problema Critico**:
- ❌ NO PERSISTENZA DATABASE
- Solo generazione in-memory
- Manca save(), load()

#### business-dna.types.ts ✅
- Default colori: #D4AF37 (gold), #0A0A0A (black), #FAFAFA (white)

---

## 🎨 SOSTITUZIONI RICHIESTE

### Focus Ring (15+ file)
- focus:ring-blue-500 → focus:ring-gold
- focus:ring-purple-500 → focus:ring-gold
- focus:ring-green-500 → focus:ring-gold

### Selected States (10+ file)
- border-blue-500 bg-blue-500/10 → border-gold bg-gold/10

### Gradients (10+ file)
- from-blue-600 to-purple-600 → from-gold to-amber-500
- from-purple-600 to-indigo-600 → from-gold to-amber-500

### Info Banners
- bg-blue-900/20 border-blue-800 text-blue-400 → bg-gold/10 border-gold/30 text-gold

---

## 📝 PIANO ESECUTIVO

### FASE 1: COLORI (123+ modifiche)
1. Sostituzioni batch regex
2. Verificare ogni file

### FASE 2: TOUCH TARGETS
1. min-h-[44px] su tutti i bottoni

### FASE 3: PERSISTENZA BUSINESS DNA
1. Backend: Creare modello BrandDNA
2. Backend: Endpoint POST/GET /api/v1/marketing/brand-dna
3. Frontend: Aggiornare hook

### FASE 4: AI CHAT FLOATING
1. Rimuovere tab chat da AIMarketing
2. Aggiungere ChatWidget a AdminShell.tsx

---

## ✅ CHECKLIST FINALE

- [ ] Zero blu (blue-500, blue-600, #3B82F6)
- [ ] Zero purple nei focus states
- [ ] Tutti bottoni min-h-11
- [ ] Business DNA persistenza DB
- [ ] AI Chat floating widget
- [ ] Test mobile

---

**Firma**: GitHub Copilot - Analisi Completa
**Status**: PRONTO PER FIX
