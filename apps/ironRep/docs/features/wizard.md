# 🧙 Visual Smart Hybrid Wizard

## Panoramica
Il "Visual Smart Hybrid Wizard" è il nuovo sistema di onboarding di IronRep.
Combina l'efficienza dei form visuali per i dati strutturati con la flessibilità di un agente AI per la conversazione e la motivazione.

## Architettura

```mermaid
graph TD
    A[Start Wizard] --> B[Intake Step UI<br/>(Biometrics + Goals + Flags)]
    B -->|Has Injury?| C[Injury UI Step]
    B -->|Want Nutrition?| D[Food Prefs UI Step]
    B -->|No Flags| E[Wizard Chat UI]
    C --> E
    D --> E
    E -->|Initial Context| F{Agent Logic}
    F -->|Has Rich Data?| G[Smart Skip<br/>(Salta fasi ridondanti)]
    F -->|Missing Data?| H[Standard Interview]
    G --> I[Chat Interaction]
    H --> I
    I -->|Complete| J[Generate Plans]
```

## Componenti Chiave

### 1. Frontend: Conditional Forms
Invece di chiedere tutto via chat, usiamo componenti React specializzati:
- `IntakeStep`: Raccoglie biometria base e flag (`hasInjury`, `wantNutrition`).
- `InjuryDetailsStep` (Condizionale): Appare solo se l'utente segnala infortuni. Raccoglie diagnosi precisa, livello dolore (slider) e data.
- `FoodPreferencesStep` (Condizionale): Appare solo se l'utente vuole il piano nutrizionale. Raccoglie cibi sì/no usando FatSecret API.

### 2. Backend: Agent Trust & Smart Skip
Il `WizardAgent` (Python) è configurato per "fidarsi" ciecamante dei dati visivi.
- Se riceve `injuryDetails` dal frontend -> Salta la fase `PAIN_ASSESSMENT`.
- Se riceve `foodPreferences` dal frontend -> Salta la fase `NUTRITION_DETAILS`.

### 3. Integrazione Agente
L'agente saluta l'utente dimostrando di conoscere già il contesto:
> "Vedo che hai un'ernia L5-S1. Procederemo con cautela. Qual è il tuo obiettivo principale?"

## Vantaggi
- **Zero Ripetizioni**: L'utente non deve riscrivere cose già cliccate.
- **Dati Puliti**: Infortuni e Cibi sono salvati come dati strutturati JSON, non testo libero.
- **UX Premium**: Slider e pulsanti sono più veloci della tastiera su mobile.
