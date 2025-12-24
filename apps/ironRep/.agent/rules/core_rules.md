# Core Rules - Protocollo ZERO ERRORI

## 1. Principi Fondamentali (MANDATORY)
- **FULL DELIVERY**: Implementazione completa. Mai lasciare "TODO" o "Placeholder" nel codice di produzione.
- **ZERO ERRORI**: Precisione massima. Verifica ogni import, ogni dipendenza, ogni nome di variabile.
- **ZERO ALLUCINAZIONI**: Usa solo informazioni verificate. Se non sai, verifica. Se non esiste, crealo esplicitamente.
- **ZERO COMPORTAMENTI IMPULSIVI**: Ogni azione deve essere ragionata. Prima di scrivere codice, analizza l'impatto.

## 2. Standard Tecnici
### Python / Backend
- **Type Safety**: Usa sempre `typing` per definire i tipi.
- **Import Espliciti**: Evita `import *`. Importa sempre le classi/funzioni specifiche.
- **Error Handling**: Mai sopprimere le eccezioni silenziosamente (`pass`). Logga sempre con stack trace completo.
- **LangChain Specifics**:
    - **Introspection Safety**: Quando usi `RunnableWithFallbacks` o wrapper complessi, assicurati che `BaseTool` sia visibile globalmente.
    - **Provider Compatibility**: Verifica sempre che il provider LLM supporti le feature richieste (es. `bind_tools` non supportato nativamente da vecchi client Ollama).

### Infrastructure
- **Centralizzazione**: Tutti i servizi infrastrutturali (DB, Redis, Ollama, Chroma) devono risiedere nel `docker-compose` centralizzato o essere referenziati via variabili d'ambiente uniformi.
- **Docker**: Usa sempre percorsi assoluti nei volumi se necessario, ma preferisci volumi named per i dati persistenti.

## 3. Workflow Operativo
1. **Analisi**: Leggi i file rilevanti prima di toccarli.
2. **Pianificazione**: Definisci la modifica atomica.
3. **Esecuzione**: Applica la modifica.
4. **Verifica**: Esegui SEMPRE un test (unitario o end-to-end via script) prima di dichiarare il successo.

## 4. Vincoli di Dominio (CRITICAL)
### Nutrizione
- **ONLY FatSecret**: La ricerca alimenti e i valori nutrizionali devono provenire ESCLUSIVAMENTE dalle API FatSecret Geolocalizzate (es. `region=IT`).
- **NO Generic DB**: Non usare database locali RAG per cercare calorie o macro di alimenti generici. La precisione di FatSecret è l'unica accettata.

### Wizard & Onboarding
- **Smart Hybrid Model**:
    - **Dati Strutturati** (Infortuni, Preferenze Cibo) -> Raccolti via **UI Visuale** (Form, Pulsanti).
    - **Conversazione** -> Gestita da **Agente AI** che riceve il contesto visuale come "verità".
- **Zero Redundancy**: L'agente non deve MAI chiedere informazioni già fornite nei passaggi visuali.
