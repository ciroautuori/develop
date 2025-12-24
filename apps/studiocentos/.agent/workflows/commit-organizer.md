---
description: Organizza commit in staging per categoria (feat/fix/docs/chore)
---

# Workflow: Commit Organizzati per Categoria

Quando hai molte modifiche e vuoi creare commit separati per categoria, segui questi step:

## 1. Visualizza File Modificati
```bash
git status --short
```

## 2. Identifica le Categorie

Raggruppa i file per tipo di modifica:

| Categoria | Prefisso | Esempi |
|-----------|----------|--------|
| **feat** | Nuove funzionalità | hooks, nuovi componenti, nuovi endpoint |
| **fix** | Bug fix | correzioni errori, fix React, fix CSS |
| **docs** | Documentazione | roadmap, README, changelog |
| **chore** | Manutenzione | config docker, dependencies, cleanup |
| **refactor** | Refactoring | riorganizzazione codice senza cambi funzionali |
| **style** | Stile/UI | CSS, design, layout changes |
| **test** | Test | nuovi test, fix test |

## 3. Commit per Categoria

### Step A: Feature Commit
```bash
# Aggiungi solo file della feature
git add [path/to/feature/files]
git commit -m "feat(scope): descrizione breve

- dettaglio 1
- dettaglio 2"
```

### Step B: Fix Commit
```bash
git add [path/to/fix/files]
git commit -m "fix(scope): descrizione breve"
```

### Step C: Docs Commit
```bash
git add docs/
git commit -m "docs: descrizione breve"
```

### Step D: Chore Commit
```bash
git add .agent/ config/
git commit -m "chore: descrizione breve"
```

## 4. Verifica Finale
```bash
git status --short  # Deve essere vuoto
git log --oneline -10  # Verifica commit history
```

---

## Esempio Pratico (24 Dic 2024)

Ho organizzato così:

| # | Commit | Files |
|---|--------|-------|
| 1 | `feat(portfolio): uniform all showcase cards` | 7 card TSX |
| 2 | `feat(vetrina): add mandatory Stripe check` | hook + form + docs |
| 3 | `docs: reorganize features folder` | MASTER_ROADMAP + cleanup |
| 4 | `chore(agent): update memories and rules` | .agent/* |
| 5 | `fix(education): standardize degree fields` | locales + components |
| 6 | `fix(languages): fix React hooks error` | LanguageForm |
| 7 | `fix(portfolio): improve PublicPortfolio` | 1 file |
| 8 | `chore(docker): update docker-compose` | config |
| 9 | `chore: remove duplicate file` | cleanup |

---

## Tips

1. **Ordine**: Commit feature prima, poi fix, poi docs, poi chore
2. **Scope**: Usa scope specifico (es. `vetrina`, `portfolio`, `agent`)
3. **Messaggi**: Prima riga max 50 chars, poi lista dettagli
4. **Verifica**: Sempre `git status` dopo ogni commit
