# ♿ **ISS - ACCESSIBILITY FIRST APPROACH**

> **🎯 ISS è progettato per essere 100% accessibile e inclusivo per tutti i cittadini**

## 🌟 **PRINCIPI FONDAMENTALI**

### **🤝 INCLUSIONE TOTALE**
- **Zero barriere economiche**: Tutto gratuito sempre
- **Zero barriere fisiche**: Accessibilità completa WCAG 2.1 AA
- **Zero barriere linguistiche**: Multilingue e linguaggio semplice
- **Zero barriere tecnologiche**: Compatibile con tecnologie assistive
- **Zero barriere geografiche**: Online + presenza per tutti

### **♿ PRINCIPI WCAG 2.1 AA**

#### **1. PERCEIVABLE (Percepibile)**
```typescript
✅ Contrasto colori 4.5:1 minimo (7:1 per AAA)
✅ Testo ridimensionabile fino 200% senza perdita funzioni
✅ Immagini con alt-text descrittivo
✅ Video con sottotitoli e trascrizioni
✅ Audio con trascrizioni complete
✅ Contenuto non dipende solo dal colore
```

#### **2. OPERABLE (Utilizzabile)**
```typescript
✅ Navigazione completa da tastiera
✅ Nessun contenuto lampeggiante (epilessia-safe)
✅ Tempo sufficiente per leggere contenuti
✅ Collegamenti skip per navigazione rapida
✅ Focus visibile e logico
✅ Shortcut tastiera personalizzabili
```

#### **3. UNDERSTANDABLE (Comprensibile)**
```typescript
✅ Linguaggio semplice e chiaro (B1/B2 max)
✅ Glossario termini tecnici integrato
✅ Istruzioni chiare per ogni azione
✅ Error messages descrittivi e utili
✅ Contenuto prevedibile e consistente
✅ Aiuto contestuale sempre disponibile
```

#### **4. ROBUST (Robusto)**
```typescript
✅ Compatibilità screen reader (NVDA, JAWS, VoiceOver)
✅ HTML semantico e valid W3C
✅ ARIA labels e landmarks corretti
✅ Funziona senza JavaScript (graceful degradation)
✅ Compatible con browser assistivi
✅ Future-proof con standard web
```

---

## 🛠️ **IMPLEMENTAZIONE TECNICA**

### **🎨 Design System Accessibile**

#### **Palette Colori WCAG Compliant**
```css
/* ISS Colors con ratios accessibilità */
--iss-bordeaux-800: #7a2426;    /* Contrasto 7:1 su bianco */
--iss-bordeaux-600: #a4182a;    /* Contrasto 5:1 su bianco */
--iss-gold-500: #f4af00;        /* Contrasto 4.7:1 su bordeaux */
--text-primary: #1a1a1a;        /* Contrasto 16:1 su bianco */
--text-secondary: #4a4a4a;      /* Contrasto 9:1 su bianco */

/* Focus states highly visible */
--focus-ring: 3px solid #2563eb;
--focus-offset: 2px;
```

#### **Typography Accessibile**
```css
/* Font sizes scalabili */
--font-base: clamp(1rem, 2.5vw, 1.125rem);    /* 16-18px */
--font-large: clamp(1.25rem, 3vw, 1.5rem);    /* 20-24px */
--font-xl: clamp(1.5rem, 4vw, 2rem);          /* 24-32px */

/* Line heights per leggibilità */
--line-height-text: 1.6;   /* Testi lunghi */
--line-height-heading: 1.2; /* Titoli */
--letter-spacing: 0.025em;  /* Spaziatura leggibile */
```

### **⌨️ Navigazione da Tastiera**

#### **Focus Management**
```typescript
// Hook per gestione focus accessibile
export const useFocusManagement = () => {
  const focusableElements = [
    'a[href]',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])'
  ].join(',');

  const trapFocus = (container: HTMLElement) => {
    const focusable = container.querySelectorAll(focusableElements);
    const firstFocusable = focusable[0] as HTMLElement;
    const lastFocusable = focusable[focusable.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstFocusable) {
            lastFocusable.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastFocusable) {
            firstFocusable.focus();
            e.preventDefault();
          }
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    return () => container.removeEventListener('keydown', handleTabKey);
  };

  return { trapFocus, focusableElements };
};
```

#### **Skip Links**
```tsx
// Componente Skip Navigation
export const SkipLinks: React.FC = () => {
  return (
    <div className="skip-links">
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 z-50 bg-iss-bordeaux-800 text-white p-2 rounded"
      >
        Salta al contenuto principale
      </a>
      <a 
        href="#navigation" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-24 z-50 bg-iss-bordeaux-800 text-white p-2 rounded"
      >
        Salta alla navigazione
      </a>
      <a 
        href="#search" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-48 z-50 bg-iss-bordeaux-800 text-white p-2 rounded"
      >
        Salta alla ricerca
      </a>
    </div>
  );
};
```

### **🔊 Screen Reader Support**

#### **ARIA Labels e Landmarks**
```tsx
// Componente Header accessibile
export const AccessibleHeader: React.FC = () => {
  return (
    <header role="banner" aria-label="Intestazione principale ISS">
      <div className="container">
        <nav role="navigation" aria-label="Menu principale">
          <h1 className="sr-only">Innovazione Sociale Salernitana</h1>
          <Link 
            to="/" 
            aria-label="Vai alla homepage ISS"
            aria-describedby="site-description"
          >
            <img 
              src="/iss-logo.svg" 
              alt="Logo Innovazione Sociale Salernitana" 
              role="img"
            />
          </Link>
          <span id="site-description" className="sr-only">
            Hub per bandi di finanziamento e formazione digitale gratuita
          </span>
          
          <ul role="list" aria-label="Menu di navigazione">
            <li role="listitem">
              <Link 
                to="/bandi" 
                aria-current={isActive ? 'page' : undefined}
                aria-describedby="bandi-desc"
              >
                Bandi
                <span id="bandi-desc" className="sr-only">
                  Cerca bandi di finanziamento per APS
                </span>
              </Link>
            </li>
            {/* Altri menu items... */}
          </ul>
        </nav>
      </div>
    </header>
  );
};
```

#### **Live Regions per Updates**
```tsx
// Componente per annunci screen reader
export const LiveAnnouncements: React.FC = () => {
  const [announcement, setAnnouncement] = useState('');
  const [politeness, setPoliteness] = useState<'polite' | 'assertive'>('polite');

  const announce = (message: string, urgent = false) => {
    setPoliteness(urgent ? 'assertive' : 'polite');
    setAnnouncement(''); // Reset per trigger update
    setTimeout(() => setAnnouncement(message), 100);
  };

  return (
    <>
      <div 
        aria-live={politeness}
        aria-atomic="true"
        className="sr-only"
      >
        {announcement}
      </div>
      
      {/* Status updates per form submissions */}
      <div 
        role="status" 
        aria-live="polite" 
        aria-atomic="true"
        className="sr-only"
      >
        {/* Dynamic status messages */}
      </div>
    </>
  );
};
```

### **📱 Mobile Accessibility**

#### **Touch Targets**
```css
/* Target touch di almeno 44px x 44px */
.touch-target {
  min-height: 44px;
  min-width: 44px;
  padding: 12px;
  position: relative;
}

/* Espansione area touch se elemento più piccolo */
.touch-target::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  min-width: 44px;
  min-height: 44px;
}
```

#### **Responsive Text Scaling**
```css
/* Supporto iOS text scaling */
@supports (font: -apple-system-body) {
  .responsive-text {
    font: -apple-system-body;
  }
}

/* Supporto Android text scaling */
.responsive-text {
  font-size: clamp(1rem, 4vw, 1.25rem);
  line-height: 1.5;
}
```

---

## 🎯 **FEATURES ACCESSIBILITY SPECIFICHE**

### **🔍 Sistema Bandi Accessibile**

```typescript
interface AccessibleBandoFilter {
  // Filtri con supporto screen reader
  announcementsEnabled: boolean;
  highContrastMode: boolean;
  simplifiedView: boolean;
  keyboardShortcuts: {
    [key: string]: () => void;
  };
}

// Componente Bando Card accessibile
export const AccessibleBandoCard: React.FC<{bando: Bando}> = ({ bando }) => {
  const cardId = `bando-${bando.id}`;
  const headingId = `${cardId}-title`;
  const statusId = `${cardId}-status`;

  return (
    <article
      aria-labelledby={headingId}
      aria-describedby={`${cardId}-desc ${statusId}`}
      className="bando-card focus-within:ring-2 focus-within:ring-iss-bordeaux-600"
      tabIndex={0}
    >
      <header>
        <h3 id={headingId} className="text-xl font-bold">
          {bando.titolo}
        </h3>
        <div 
          id={statusId}
          role="status"
          aria-live="polite"
          className={`badge ${getStatusClass(bando.status)}`}
        >
          <span className="sr-only">Stato del bando: </span>
          {bando.status}
        </div>
      </header>
      
      <div id={`${cardId}-desc`}>
        <p className="text-sm text-muted-foreground mb-2">
          <span className="sr-only">Ente erogatore: </span>
          {bando.ente_erogatore}
        </p>
        <p className="text-sm mb-4">
          {bando.descrizione}
        </p>
        
        {bando.data_scadenza && (
          <time 
            dateTime={bando.data_scadenza}
            className="text-sm font-medium"
            aria-label={`Scadenza: ${formatDateAccessible(bando.data_scadenza)}`}
          >
            <span className="sr-only">Scadenza: </span>
            {formatDateAccessible(bando.data_scadenza)}
          </time>
        )}
      </div>
      
      <footer className="flex gap-2 mt-4">
        <Button
          variant="iss-primary"
          size="sm"
          aria-describedby={`${cardId}-details-desc`}
          onClick={() => openBandoDetails(bando)}
        >
          Dettagli
          <span id={`${cardId}-details-desc`} className="sr-only">
            del bando {bando.titolo}
          </span>
        </Button>
        
        <Button
          variant="outline"
          size="sm"
          aria-describedby={`${cardId}-save-desc`}
          onClick={() => saveBando(bando)}
          aria-pressed={isSaved}
        >
          {isSaved ? 'Salvato' : 'Salva'}
          <span id={`${cardId}-save-desc`} className="sr-only">
            {isSaved ? 'Rimuovi dai salvati' : 'Salva nei preferiti'} il bando {bando.titolo}
          </span>
        </Button>
      </footer>
    </article>
  );
};
```

### **🎓 Sistema Corsi Accessibile**

```typescript
// Form iscrizione corso con accessibilità completa
export const AccessibleCorsoEnrollment: React.FC<{corso: Corso}> = ({ corso }) => {
  const [accessibilityNeeds, setAccessibilityNeeds] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  return (
    <form 
      onSubmit={handleSubmit}
      aria-labelledby="enrollment-title"
      aria-describedby="enrollment-description"
      noValidate
    >
      <h2 id="enrollment-title">
        Iscrizione al corso: {corso.titolo}
      </h2>
      <p id="enrollment-description">
        Tutti i corsi ISS sono gratuiti e inclusivi. Compila il form per l'iscrizione.
      </p>

      <fieldset>
        <legend>Informazioni personali</legend>
        
        <div className="form-group">
          <label htmlFor="fullName" className="required">
            Nome completo
            <span aria-label="campo obbligatorio">*</span>
          </label>
          <input
            id="fullName"
            type="text"
            required
            aria-invalid={errors.fullName ? 'true' : 'false'}
            aria-describedby={errors.fullName ? 'fullName-error' : undefined}
          />
          {errors.fullName && (
            <div 
              id="fullName-error" 
              role="alert"
              className="error-message"
            >
              {errors.fullName}
            </div>
          )}
        </div>
      </fieldset>

      <fieldset>
        <legend>Esigenze di accessibilità</legend>
        <p className="fieldset-description">
          Indica eventuali esigenze per partecipare al meglio al corso
        </p>
        
        <div className="form-group">
          <label htmlFor="accessibility-needs">
            Supporti necessari (opzionale)
          </label>
          <textarea
            id="accessibility-needs"
            value={accessibilityNeeds}
            onChange={(e) => setAccessibilityNeeds(e.target.value)}
            placeholder="Es: Interprete LIS, materiali in Braille, parcheggio disabili, etc."
            aria-describedby="accessibility-help"
            rows={4}
          />
          <div id="accessibility-help" className="help-text">
            Specifica qualsiasi supporto di cui hai bisogno. Faremo il possibile per garantire la tua partecipazione.
          </div>
        </div>

        <fieldset className="checkbox-group">
          <legend>Servizi aggiuntivi disponibili</legend>
          {accessibilityServices.map((service) => (
            <label key={service.id} className="checkbox-label">
              <input
                type="checkbox"
                value={service.id}
                aria-describedby={`${service.id}-desc`}
              />
              <span>{service.name}</span>
              <span id={`${service.id}-desc`} className="service-description">
                {service.description}
              </span>
            </label>
          ))}
        </fieldset>
      </fieldset>

      <div className="form-actions">
        <Button
          type="submit"
          variant="iss-primary"
          disabled={isSubmitting}
          aria-describedby="submit-help"
        >
          {isSubmitting ? 'Invio in corso...' : 'Iscriviti gratuitamente'}
        </Button>
        <p id="submit-help" className="help-text">
          L'iscrizione è gratuita e riceverai conferma via email entro 24 ore.
        </p>
      </div>
    </form>
  );
};
```

---

## 🧪 **TESTING ACCESSIBILITY**

### **🔬 Tools di Testing**
```bash
# Automated testing
npm install --save-dev @axe-core/react @testing-library/jest-dom
npm install --save-dev lighthouse lighthouse-ci

# Manual testing tools
npm install --save-dev pa11y pa11y-ci
```

### **🤖 Automated Tests**
```typescript
// Tests accessibilità con Jest + axe
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('BandoCard Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(
      <BandoCard bando={mockBando} />
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should be keyboard navigable', () => {
    render(<BandoCard bando={mockBando} />);
    
    const card = screen.getByRole('article');
    fireEvent.keyDown(card, { key: 'Enter' });
    
    expect(mockOnClick).toHaveBeenCalled();
  });

  it('should announce changes to screen readers', () => {
    render(<BandoCard bando={mockBando} />);
    
    const statusElement = screen.getByRole('status');
    expect(statusElement).toHaveAttribute('aria-live', 'polite');
  });
});
```

### **👥 User Testing**
```typescript
// Piano testing con utenti reali
interface AccessibilityUserTestPlan {
  screenReaderUsers: {
    tools: ['NVDA', 'JAWS', 'VoiceOver'];
    scenarios: string[];
    successCriteria: string[];
  };
  
  motorImpairmentUsers: {
    inputMethods: ['keyboard-only', 'switch-device', 'voice-control'];
    scenarios: string[];
    successCriteria: string[];
  };
  
  cognitiveAccessibilityUsers: {
    needsAssessment: string[];
    simplificationFeatures: string[];
    supportMechanisms: string[];
  };
}
```

---

## 🎯 **IMPACT ACCESSIBILITY**

### **📈 Metrics di Successo**
- **100% WCAG 2.1 AA compliance** in automated tests
- **< 0 critical accessibility issues** in Lighthouse
- **90%+ user satisfaction** tra utenti con disabilità
- **5+ lingue supportate** per inclusione linguistica
- **100% features utilizzabili** solo con tastiera
- **Zero barriere economiche** per qualsiasi servizio

### **🤝 Partnership Accessibility**
- **UICI Salerno** (Unione Italiana Ciechi e Ipovedenti)
- **ENS Campania** (Ente Nazionale Sordi)
- **ANMIC** (Associazione Nazionale Mutilati e Invalidi Civili)
- **Centri Territoriali di Supporto** per tecnologie assistive
- **Università** per ricerca sull'accessibilità

**ISS sarà un modello di accessibilità digitale per il terzo settore italiano!** ♿🌟

---

## 💡 **INNOVAZIONI ACCESSIBILITY ISS**

### **🔊 Voice Interface**
- **Controlli vocali** per navigazione hands-free
- **Lettura automatica** contenuti con sintesi vocale
- **Comandi vocali personalizzabili** per azioni frequenti

### **🤖 AI per Accessibilità**
- **Auto-generazione alt-text** per immagini
- **Semplificazione testi automatica** (livello B1/B2)
- **Traduzione automatica** in tempo reale
- **Predizione esigenze utente** basata su comportamento

### **📱 App Mobile Accessibile**
- **PWA** con funzionalità offline
- **Compatibilità totale** con TalkBack/VoiceOver
- **Gesture personalizzabili** per utenti con disabilità motorie
- **Modalità alto contrasto** e dark mode

**ISS sarà all'avanguardia nell'accessibilità digitale!** 🚀♿
