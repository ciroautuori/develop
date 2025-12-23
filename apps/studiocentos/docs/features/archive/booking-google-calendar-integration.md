# 🎯 Booking System - Google Calendar/Meet Integration

## 📋 Overview

Il sistema di prenotazioni è stato **potenziato** (non duplicato) per integrarsi completamente con Google Calendar API e Google Meet, sfruttando l'infrastruttura esistente.

## ✅ Architettura Esistente Utilizzata

### Backend (GIÀ PRESENTE)
- ✅ **GoogleCalendarService** (`app/domain/google/calendar_service.py`)
  - Metodo `create_event_with_meet()` per creare eventi con conferenceData
  - Metodo `update_event()` per aggiornare eventi
  - Metodo `delete_event()` per cancellare eventi
  - OAuth token management automatico

- ✅ **BookingAdminService** (`app/domain/booking/admin_service.py`)
  - `create_booking()` - Crea booking + evento Google Calendar
  - `update_booking()` - Aggiorna booking + sincronizza Calendar
  - `delete_booking()` - Elimina booking + rimuove evento Calendar

- ✅ **Models** (`app/domain/booking/models.py`)
  - Campo `meeting_provider` (google_meet, zoom, phone, in_person)
  - Campo `meeting_url` (link Google Meet auto-generato)
  - Campo `meeting_id` (Calendar event ID per sync)

- ✅ **Router** (`app/domain/booking/admin_router.py`)
  - `POST /api/v1/admin/bookings` - Crea con Calendar sync
  - `PUT /api/v1/admin/bookings/{id}` - Aggiorna con sync
  - `DELETE /api/v1/admin/bookings/{id}` - Elimina con sync

### Flow Automatico Backend

```
Admin crea booking (meeting_provider='google_meet')
    ↓
BookingAdminService.create_booking()
    ↓
create_google_meet_link() [services.py]
    ↓
GoogleCalendarService.create_event_with_meet()
    ↓
Google Calendar API crea evento + conferenceData
    ↓
Backend riceve event_id + meet_link
    ↓
Salva meeting_url e meeting_id nel booking
    ↓
Invia invito email automatico al cliente
```

## 🚀 Migliorie Frontend (NUOVE)

### 1. Smart Pre-Selection Dropdowns

**File**: `apps/frontend/src/features/admin/components/BookingModal.tsx`

```tsx
const SERVICE_DEFAULTS = {
  consultation: { duration: 60, requiresMeet: true },
  meeting: { duration: 30, requiresMeet: true },
  demo: { duration: 45, requiresMeet: true },
  support: { duration: 30, requiresMeet: false },
  training: { duration: 120, requiresMeet: true },
  interview: { duration: 60, requiresMeet: true }
};
```

**Comportamento**:
- Cambiando "Tipo Servizio", la durata si adatta automaticamente
- `meeting_provider` viene pre-selezionato in base al tipo servizio
- Consulenze/Demo → Google Meet automatico
- Supporto → Chiamata telefonica

**Esempio**:
```
User seleziona: "🎯 Demo"
  ↓
Durata auto-cambia: 45 minuti
Meeting provider: Google Meet
```

### 2. Visualizzazione Google Meet Link

**Quando disponibile** (dopo creazione booking):
```tsx
{isEdit && booking?.meeting_url && (
  <div>
    <label>Link Google Meet</label>
    <input value={booking.meeting_url} readOnly />
    <Button onClick={() => copy(booking.meeting_url)}>📋 Copia</Button>
    <Button onClick={() => open(booking.meeting_url)}>🚀 Apri</Button>
  </div>
)}
```

**Features**:
- 📋 Bottone "Copia" → copia link negli appunti
- 🚀 Bottone "Apri" → apre Meet in nuova tab
- ✅ Badge "Google Meet creato via Calendar API"

### 3. Toast Notifications Migliorati

```tsx
// Dopo creazione booking
if (result?.meeting_url) {
  toast.success(`🎥 Meet creato: ${result.meeting_url}`, { duration: 8000 });
}
```

**Feedback all'utente**:
- ✅ "Prenotazione creata!"
- 🎥 "Meet creato: https://meet.google.com/abc-defg-hij"
- Toast rimane visibile 8 secondi per copiare link

### 4. UI Consistency

**Styling uniforme** con AIMarketing.tsx:
```tsx
const selectBg = isDark
  ? 'bg-white/5 border-white/10 text-white'
  : 'bg-white border-gray-300 text-gray-900';
```

- Dropdown con sfondo bianco in light mode
- Border grigio per consistenza design system
- Focus ring oro `#D4AF37`

## 🔧 Mapping Frontend ↔ Backend

| Frontend Field      | Backend Field       | Descrizione                     |
|---------------------|---------------------|---------------------------------|
| `service_type`      | `service_type`      | consultation, meeting, demo...  |
| `duration_minutes`  | `duration_minutes`  | Auto-set da SERVICE_DEFAULTS    |
| `meeting_provider`  | `meeting_provider`  | google_meet, phone, zoom...     |
| `meeting_url`       | `meeting_url`       | Link Meet (read-only frontend)  |
| -                   | `meeting_id`        | Calendar event ID (backend only)|

## 📊 Test Flow Completo

### Script di Test
```bash
./scripts/tests/test_booking_google_meet.sh
```

**Cosa testa**:
1. ✅ Creazione booking con `meeting_provider='google_meet'`
2. ✅ Backend genera Google Meet link automaticamente
3. ✅ Link salvato in `booking.meeting_url`
4. ✅ Smart pre-selection (demo = 45 min)
5. ✅ Cleanup automatico

### Test Manuale UI

1. **Apri BookingModal** → "Nuova Prenotazione"
2. **Seleziona servizio**: "🎯 Demo"
   - ✅ Durata cambia automaticamente a 45 min
   - ✅ Meeting provider = Google Meet
3. **Compila campi**: Nome, Email, Data/Ora
4. **Salva**
   - ✅ Toast: "Prenotazione creata!"
   - ✅ Toast: "🎥 Meet creato: https://meet.google.com/..."
5. **Riapri booking**
   - ✅ Campo "Link Google Meet" visibile
   - ✅ Bottoni 📋 Copia e 🚀 Apri funzionanti

## 🎯 Service Type Presets

| Servizio       | Emoji | Durata | Meeting Provider | Note                     |
|----------------|-------|--------|------------------|--------------------------|
| Consultation   | 💼    | 60 min | Google Meet      | Consulenza standard      |
| Meeting        | 🤝    | 30 min | Google Meet      | Meeting veloce           |
| Demo           | 🎯    | 45 min | Google Meet      | Demo prodotto            |
| Support        | 🛠️    | 30 min | Phone            | Supporto telefonico      |
| Training       | 📚    | 120min | Google Meet      | Formazione (2h)          |
| Interview      | 🎤    | 60 min | Google Meet      | Colloquio                |

## 🔐 Sicurezza & OAuth

- ✅ Solo admin autenticato via Google OAuth può creare bookings
- ✅ Token OAuth recuperato da `localStorage.getItem('admin_token')`
- ✅ Backend valida token e usa scope `calendar.events` per API
- ✅ Ogni booking creato usa l'account Google dell'admin loggato

## 📅 Google Calendar Sync Features

### Creazione Evento
```python
event = {
  "summary": booking.title,
  "description": f"Cliente: {name}\nEmail: {email}",
  "start": {"dateTime": scheduled_at.isoformat()},
  "end": {"dateTime": end_time.isoformat()},
  "attendees": [{"email": client_email}],
  "conferenceData": {
    "createRequest": {
      "requestId": uuid4(),
      "conferenceSolutionKey": {"type": "hangoutsMeet"}
    }
  }
}
```

### Auto-Invito Email
- ✅ Google Calendar invia automaticamente invito al `client_email`
- ✅ Cliente riceve email con:
  - Dettagli appuntamento
  - Link Google Meet
  - Bottone "Aggiungi al calendario"

### Reminder Automatici
```python
"reminders": {
  "overrides": [
    {"method": "email", "minutes": 1440},  # 24h prima
    {"method": "popup", "minutes": 30}     # 30min prima
  ]
}
```

## 🎨 UI/UX Improvements

### Dropdown Migliorati
- ✅ Emoji per ogni opzione
- ✅ Durata suggerita mostrata nel label
- ✅ Tooltip: "Durata e tipo meeting si adattano automaticamente"
- ✅ Focus ring oro consistente con design system

### Meeting Provider
```tsx
<select value={meeting_provider}>
  <option value="google_meet">🎥 Google Meet (Calendar API)</option>
  <option value="phone">📞 Chiamata Telefonica</option>
  <option value="in_person">🏢 Di Persona</option>
  <option value="zoom">🎬 Zoom (Manuale)</option>
</select>
```

### Info Tooltip
```
meeting_provider === 'google_meet'
  ↓
"✨ Google Calendar creerà automaticamente evento + Meet link + invito email"
```

## 🔄 Update/Delete Sync

### Update Booking
```typescript
// Frontend
await updateBooking.mutateAsync({ id, data });

// Backend sincronizza automaticamente:
if (booking.meeting_id) {
  await update_booking_event(
    event_id=booking.meeting_id,
    new_start_time=...,
    new_duration_minutes=...
  )
}
```

### Delete Booking
```typescript
// Frontend
await deleteBooking.mutateAsync(id);

// Backend cancella da Calendar:
if (booking.meeting_id) {
  await cancel_booking_event(
    event_id=booking.meeting_id,
    send_notifications=True  // Invia email cancellazione
  )
}
```

## 📈 Vantaggi Implementazione

### ✅ Nessun Duplicato
- Sfrutta `GoogleCalendarService` esistente
- Usa `BookingAdminService` già implementato
- Nessun nuovo endpoint API creato
- Nessun nuovo modulo backend

### ✅ Smart Defaults
- Riduce errori umani (durata sbagliata)
- UX più veloce (meno click)
- Pre-selection intelligente service → duration → meeting_provider

### ✅ Automazione Completa
- Admin crea booking → Meet link auto-generato
- Cliente riceve invito email automatico
- Reminder 24h e 30min automatici
- Sync bidirezionale Calendar ↔ Booking

### ✅ User Experience
- Toast con Meet link (copiabile)
- Bottoni Copia/Apri link rapidi
- Badge "Google Meet creato via Calendar API"
- Tooltip informativi

## 🚀 Prossimi Step (Opzionali)

### 1. Calendar Widget Frontend
- Mostrare eventi Google Calendar in BusinessHub
- Drag & drop per reschedule
- Color coding per service_type

### 2. Client Portal
- Cliente può vedere i suoi bookings
- Reschedule self-service
- Join Meeting button

### 3. Analytics
- Booking conversion rate
- No-show tracking
- Service type popularity

### 4. Integrazione Zoom
- Implementare `create_zoom_meeting()` (già stub in services.py)
- Alternative a Google Meet per clienti senza Gmail

## 📝 Note Tecniche

### OAuth Scopes Richiesti
```python
SCOPES = [
  'https://www.googleapis.com/auth/calendar',
  'https://www.googleapis.com/auth/calendar.events',
  'https://www.googleapis.com/auth/gmail.send'
]
```

### Timezone Management
- Default: `Europe/Rome`
- ISO 8601 format per datetime
- Frontend invia UTC, backend converte

### Error Handling
```python
try:
  result = await create_google_meet_link(...)
  booking.meeting_url = result.get("meet_link")
except Exception as e:
  # Non blocca creazione booking
  logger.error(f"Google Calendar error: {e}")
```

### Backward Compatibility
- Bookings esistenti senza `meeting_provider` continuano a funzionare
- Default `meeting_provider='google_meet'` per nuovi bookings
- Campo `meeting_url` nullable per bookings manuali

## 🎯 Conclusione

L'integrazione Google Calendar/Meet è **completa e funzionale**:

✅ Backend: Già implementato con `GoogleCalendarService`
✅ Frontend: Potenziato con smart dropdowns e Meet link display
✅ Automazione: Evento + Meet + Email invito automatici
✅ UX: Toast, bottoni Copia/Apri, tooltip informativi
✅ Testing: Script automatizzato per verifica end-to-end

**Nessun file duplicato**, solo **potenziamento dell'esistente**.
