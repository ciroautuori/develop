# 👥 **ISS SISTEMA BANDI - USER ACCEPTANCE TESTS**

> **Test per APS Partner**: Validazione esperienza utente reale con stakeholder del territorio

## 🎯 **OBIETTIVI TESTING**

- **Usabilità**: Facilità d'uso per operatori APS non-tech
- **Accessibilità**: Conformità WCAG 2.1 AA per utenti con disabilità  
- **Performance**: Esperienza fluida con dataset reale 500+ bandi
- **Completezza**: Copertura dell'intero workflow bandi

---

## 📋 **TEST SCENARIOS PER APS PARTNER**

### **🔍 SCENARIO 1: Ricerca Base**
**Attore**: Operatore APS senza competenze tecniche avanzate  
**Goal**: Trovare bandi relevanti per la propria associazione

**Test Steps**:
1. ✅ Aprire https://iss.salerno.it/bandi
2. ✅ Utilizzare barra di ricerca con parole chiave "giovani"
3. ✅ Verificare risultati pertinenti mostrati
4. ✅ Cliccare su un bando per vedere dettagli
5. ✅ Salvare bando negli "Interessanti"

**Criteri Successo**:
- [ ] Ricerca restituisce risultati in <2 secondi
- [ ] Risultati sono ordinati per rilevanza
- [ ] Dettagli bando completi e comprensibili
- [ ] Salvataggio funziona correttamente
- [ ] UI intuitiva senza formazione

**Note Tester**: ________________________________
**Rating** (1-5): ⭐⭐⭐⭐⭐

---

### **🎛️ SCENARIO 2: Filtri Avanzati**
**Attore**: Responsabile progetti APS esperto
**Goal**: Utilizzare filtri per ricerca mirata

**Test Steps**:
1. ✅ Aprire pannello filtri avanzati
2. ✅ Impostare filtro "Fonte: Regione Campania"
3. ✅ Impostare range importo "€10.000 - €50.000"
4. ✅ Filtrare per scadenza "Prossimi 30 giorni"
5. ✅ Applicare filtri e verificare risultati

**Criteri Successo**:
- [ ] Filtri facilmente individuabili
- [ ] Combinazione filtri funziona correttamente
- [ ] Risultati filtrati accurati
- [ ] Possibilità reset filtri rapido
- [ ] Filtri attivi chiaramente visibili

**Note Tester**: ________________________________
**Rating** (1-5): ⭐⭐⭐⭐⭐

---

### **📤 SCENARIO 3: Export e Condivisione**
**Attore**: Coordinatore rete APS 
**Goal**: Esportare lista bandi per condivisione team

**Test Steps**:
1. ✅ Selezionare multipli bandi interessanti
2. ✅ Cliccare "Export" 
3. ✅ Scegliere formato PDF
4. ✅ Personalizzare campi da includere
5. ✅ Scaricare e verificare file generato

**Criteri Successo**:
- [ ] Selezione multipla intuitiva
- [ ] Export PDF ben formattato
- [ ] Tutti campi richiesti presenti
- [ ] Download avviene rapidamente
- [ ] File utilizzabile per condivisione

**Note Tester**: ________________________________
**Rating** (1-5): ⭐⭐⭐⭐⭐

---

### **♿ SCENARIO 4: Test Accessibilità**
**Attore**: Utente non vedente con screen reader
**Goal**: Navigare sistema usando solo tecnologie assistive

**Test Steps**:
1. ✅ Navigare con Tab tra elementi
2. ✅ Utilizzare screen reader per leggere contenuti
3. ✅ Eseguire ricerca usando solo tastiera
4. ✅ Aprire filtri con Enter/Spazio
5. ✅ Completare workflow senza mouse

**Criteri Successo**:
- [ ] Tutti elementi raggiungibili via tastiera
- [ ] Screen reader legge contenuti correttamente
- [ ] Skip links funzionanti
- [ ] Focus trap nei modal
- [ ] ARIA labels appropriati

**Note Tester**: ________________________________
**Rating** (1-5): ⭐⭐⭐⭐⭐

---

### **📱 SCENARIO 5: Mobile Experience**
**Attore**: Volontario APS in mobilità
**Goal**: Utilizzare sistema da smartphone

**Test Steps**:  
1. ✅ Aprire bandi da dispositivo mobile
2. ✅ Testare ricerca touchscreen
3. ✅ Verificare filtri responsive
4. ✅ Scrolling e navigazione fluida
5. ✅ Testare link esterni

**Criteri Successo**:
- [ ] Layout responsive perfetto
- [ ] Touch targets dimensioni adeguate
- [ ] Scroll performance fluida
- [ ] Testo leggibile senza zoom
- [ ] Funzionalità complete su mobile

**Note Tester**: ________________________________
**Rating** (1-5): ⭐⭐⭐⭐⭐

---

## 📊 **METRICHE QUALITATIVE**

### **Net Promoter Score (NPS)**
"Quanto consiglieresti il Sistema Bandi ISS ad altre APS?"
- 0-6: Detrattori
- 7-8: Neutrali  
- 9-10: Promotori

**Score Partner**: ___/10

### **System Usability Scale (SUS)**
Questionario standard usabilità (10 domande, scala 1-5)

1. **Uso frequente**: Vorrei usare questo sistema spesso
2. **Complessità**: Il sistema è inutilmente complesso
3. **Facilità**: Il sistema è facile da usare  
4. **Supporto**: Ho bisogno di supporto tecnico per usarlo
5. **Integrazione**: Le funzioni sono ben integrate
6. **Incoerenza**: C'è troppa incoerenza nel sistema
7. **Apprendimento**: Penso che si impari rapidamente
8. **Difficoltà**: Il sistema è difficile/pesante da usare
9. **Sicurezza**: Mi sento sicuro usando il sistema
10. **Formazione**: Ho bisogno di formazione prima di usarlo

**SUS Score Totale**: ___/100

---

## 🎯 **SCENARIO WORKFLOW COMPLETO**

### **"Giornata Tipo Operatore APS"**
**Durata**: 30 minuti  
**Attore**: Maria, Responsabile Progetti APS "Nuove Rotte"

**Background**: Maria deve cercare finanziamenti per un progetto sull'inclusione digitale degli anziani. Ha 30 minuti prima di una riunione.

**Workflow Completo**:
1. **Login** (se necessario)
2. **Ricerca** → "inclusione digitale anziani"
3. **Filtraggio** → Importo min €15.000, Scadenza prossimi 60 giorni
4. **Valutazione** → Leggere 5-7 bandi più promettenti
5. **Selezione** → Salvare 3 bandi di interesse
6. **Export** → Creare PDF per condivisione team
7. **Follow-up** → Aggiungere note personali sui bandi

**Criteri Successo Globali**:
- [ ] Workflow completato in <30 minuti
- [ ] Zero supporto tecnico richiesto
- [ ] Risultati utili e actionable
- [ ] Esperienza positiva generale
- [ ] Valore aggiunto rispetto a metodi attuali

**Note Finali**: ________________________________
**Raccomandazioni**: ________________________________

---

## 📈 **PERFORMANCE BENCHMARKS**

### **Tempi Target**:
- **Ricerca base**: <2 secondi
- **Filtri applicati**: <3 secondi  
- **Caricamento pagina**: <1 secondo
- **Export PDF**: <5 secondi
- **Mobile loading**: <2 secondi

### **Stress Test**:
- **50 utenti concorrenti**: Performance accettabile
- **500+ bandi**: Navigazione fluida
- **Filtri multipli**: Risposta immediata
- **Mobile 3G**: Usabilità mantenuta

---

## ✅ **CHECKLIST FINALE APS PARTNER**

### **Usabilità** ✅❌
- [ ] Sistema immediatamente comprensibile
- [ ] Workflow logico e naturale
- [ ] Errori facilmente correggibili
- [ ] Feedback chiari per ogni azione
- [ ] Terminologia appropriata settore APS

### **Utilità** ✅❌  
- [ ] Bandi mostrati sono rilevanti
- [ ] Informazioni sufficienti per decisioni
- [ ] Export utilizzabili internamente
- [ ] Notifiche utili senza spam
- [ ] Integrazione workflow esistente

### **Performance** ✅❌
- [ ] Velocità accettabile sempre
- [ ] Nessun crash o blocco sistema
- [ ] Mobile performance adeguata
- [ ] Compatibilità browser garantita
- [ ] Accessibilità piena garantita

---

## 🏆 **VERDETTO FINALE APS PARTNER**

**Valutazione Complessiva**: ___/5 ⭐
**Pronti per Production**: ✅ YES / ❌ NO
**Blocker Issues**: ________________________________
**Nice-to-Have**: ________________________________

**Firma Partner Tester**: ________________________________
**Data**: ________________________________

---
*Test eseguiti secondo standard ISO 9241-11 (Usabilità) e WCAG 2.1 AA (Accessibilità)*
