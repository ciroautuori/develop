# Design System Audit & UI Report (Frontend)
Data: 07 Dicembre 2025
Stato: ✅ COMPLETED

Questo documento analizza lo stato attuale del Design System, evidenziando le discrepanze tra Landing Page e Backoffice, e fornisce una roadmap per il refactoring.

---

## 1. Architettura Attuale

Il progetto utilizza **TailwindCSS** come motore principale, integrato con **Shadcn/UI** per i componenti riutilizzabili.

| Componente | Stack Tecnologico | Stato Design System |
|------------|-------------------|---------------------|
| **Core** | TailwindCSS + CSS Variables | ✅ Definito (Globals.css) |
| **Backoffice** | React + Shadcn/UI + Lucide Icons | ✅ Aderente (High Consistency) |
| **Landing Page** | React + CSS Animations + Shadcn/UI | ✅ Aderente (Refactored) |

---

## 2. Incongruenze Rilevate (Bugs & Style Mismatches)

### ✅ A. Conflitto Animazioni (Landing Page)
**Bug:** Il file `landing.css` dichiara esplicitamente: *"ANIMATIONS - Sostituiscono Framer Motion"*.
**Soluzione Applicata:** Rimossa Framer Motion. Introdotto `RevealOnScroll` component che usa animazioni CSS native (`animate-fade-in-up`, etc.).

### ✅ B. Colori Hardcoded vs Design Tokens
**Bug:** La Landing Page utilizza valori HEX manuali invece dei token definiti in `tailwind.config.js`.
**Soluzione Applicata:** Tutti i colori hardcoded (`#0a0a0a`, `#D4AF37`) sostituiti con classi Tailwind semantiche (`bg-background`, `text-primary`, `text-muted-foreground`).

### ✅ C. Componenti UI non riutilizzati
**Bug:** La Landing Page ricrea pulsanti e card da zero con HTML/CSS invece di importare `components/ui/button`.
**Soluzione Applicata:** Implementati `<Button>` di Shadcn/UI ovunque, inclusi header, hero e contact form.

### ✅ D. Duplicazione CSS in Globals
**Issue:** `globals.css` contiene classi specifiche per la landing (`.landing-hero`, `.bento-grid`).
**Stato:** Monitoraggio. Non critico dopo il refactoring dei componenti.

---

## 3. Style Guide & Design Tokens (Riferimento)

### Colori Brand
- **Gold Primary:** `#D4AF37` (`bg-primary`, `text-primary`)
- **Background Dark:** `#0A0A0A` (Landing) vs `#0a0a0a` (Admin) -> *Unificare*

### Typography
- **Font:** Inter
- **Headings:** Mobile-first, `font-semibold tracking-tight`

---

## 4. Roadmap di Refactoring (Action Plan)

### Fase 1: Pulizia (Priority: High)
- [ ] **Rimozione Framer Motion dalla Landing:** Se l'obiettivo è usare CSS, sostituire tutti i `<motion.div>` con le classi `animate-*` definite in `landing.css`.
- [ ] **Standardizzazione Colori:** Sostituire tutti i codici HEX `#...` nella Landing con le classi Tailwind `bg-background`, `text-gold`, etc.

### Fase 2: Unificazione Componenti (Priority: Medium)
- [ ] Sostituire i tag `<button>` della Landing con `<Button>` di Shadcn.
- [ ] Sostituire gli input manuali con `<Input>` di Shadcn nel form contatti.

### Fase 3: Performance (Priority: Low)
- [ ] Spostare le classi `.landing-*` da `globals.css` a un file CSS modulare o convertire in Tailwind.
- [ ] Verificare che `landing.css` venga caricato solo nella rotta home.

---

**Nota per il Team:**
L'Admin Dashboard (`AdminShell.tsx`) è attualmente l'implementazione di riferimento ("Gold Standard") per come il codice dovrebbe essere strutturato. La Landing Page necessita di un refactoring per allinearsi a questo standard.
