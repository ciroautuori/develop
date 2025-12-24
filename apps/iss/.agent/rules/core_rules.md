---
description: "Regole d'oro non negoziabili per l'operatività dell'agente"
---

# 🏆 Regole d'Oro (Non Negoziabili)

1. **Analisi Prima di Agire**: Mai modificare codice senza aver prima letto e compreso il contesto, i file correlati e le dipendenze.
2. **Niente Hallucinazioni**: Se non sei sicuro, VERIFICA. Non inventare nomi di file, funzioni o percorsi. Usa `ls`, `grep` o `view_file` per confermare.
3. **Testare Sempre**: Dopo ogni modifica significativa, verifica che il codice compili e che le funzionalità principali (es. Login, Build) non siano rotte.
4. **Non Rompere la Produzione**: Le modifiche critiche (auth, db) vanno testate isolatamente o con script di debug prima di dire "è fatto".
5. **Memoria Storica**: Consulta sempre `.agent/memories` e `.agent/workflows` per vedere come sono stati risolti problemi simili in passato.
6. **Docker Pulito**: Quando si ricostruisce, usare `--no-cache` se ci sono modifiche a dipendenze o asset statici, per evitare versioni vecchie.
7. **No Hardcoded Credentials**: Mai lasciare password o chiavi API nel codice.
8. **Infrastruttura Centralizzata**: Tutti i servizi di rete condivisi (Redis, DB esterni, ecc.) devono essere accessibili tramite endpoint centralizzati e NON gestiti localmente nei file compose di progetto.
