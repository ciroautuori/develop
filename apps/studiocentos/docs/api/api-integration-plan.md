# 🚀 StudioCentOS - Piano Integrazione API Strategiche

## Panoramica

Questo documento descrive tutte le API da integrare nel backoffice StudioCentOS e nei suoi agenti AI per massimizzare l'automazione e il valore per i clienti.

---

## 📋 Indice

1. [Lead Intelligence & B2B](#1-lead-intelligence--b2b)
2. [Marketing Automation](#2-marketing-automation)
3. [SEO & Analytics](#3-seo--analytics)
4. [AI Avanzata](#4-ai-avanzata)
5. [Business Operations](#5-business-operations)
6. [Priorità Implementation](#6-priorità-implementation)

---

## 1. Lead Intelligence & B2B

### 1.1 Apollo.io API
**Priorità**: 🔴 CRITICA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Database B2B con 265M+ contatti, info aziendali, email, telefoni |
| **Costo** | Free: 50 credits/mese, Basic: $49/mese (200 credits) |
| **Endpoint Base** | `https://api.apollo.io/v1/` |
| **Auth** | API Key in header |

**Endpoints chiave**:
```
POST /people/match         → Trova persone per ruolo/azienda
POST /organizations/enrich → Arricchisci dati azienda
POST /mixed_people/search  → Ricerca avanzata contatti
```

**Integrazione proposta**:
```python
# app/domain/lead_finder/apollo_service.py
class ApolloService:
    async def find_decision_makers(self, company_domain: str, job_titles: List[str]) -> List[Contact]
    async def enrich_company(self, domain: str) -> CompanyInfo
    async def search_leads(self, industry: str, location: str, size_range: str) -> List[Lead]
```

**File da modificare**:
- `apps/ai_microservice/app/domain/lead_finder/` → Nuovo `apollo_service.py`
- `config/docker/.env.production` → Aggiungere `APOLLO_API_KEY`

---

### 1.2 Hunter.io API
**Priorità**: 🟠 ALTA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Trova email professionali da dominio, verifica email |
| **Costo** | Free: 25 ricerche/mese, Starter: €49/mese |
| **Endpoint Base** | `https://api.hunter.io/v2/` |
| **Auth** | API Key in query param |

**Endpoints chiave**:
```
GET /domain-search?domain=example.com  → Tutte le email di un dominio
GET /email-finder?domain=X&first_name=Y → Trova email specifica
GET /email-verifier?email=X            → Verifica deliverability
```

**Integrazione proposta**:
```python
# app/domain/lead_finder/hunter_service.py
class HunterService:
    async def find_emails_by_domain(self, domain: str) -> List[EmailResult]
    async def find_email(self, domain: str, first_name: str, last_name: str) -> str
    async def verify_email(self, email: str) -> VerificationResult
```

---

### 1.3 Clearbit API
**Priorità**: 🟠 ALTA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Arricchimento dati B2B (logo, industry, revenue, employees) |
| **Costo** | Custom pricing (contattare sales) |
| **Endpoint Base** | `https://company.clearbit.com/v2/` |
| **Auth** | Bearer Token |

**Endpoints chiave**:
```
GET /companies/find?domain=X   → Dati completi azienda
GET /people/find?email=X       → Dati persona da email
```

**Note**: Già presente in config ma non implementato.

---

### 1.4 LinkedIn Sales Navigator API
**Priorità**: 🟡 MEDIA (richiede LinkedIn Partnership)

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Accesso a profili LinkedIn, lead lists, InMail |
| **Costo** | Enterprise only (partnership richiesta) |
| **Alternativa** | Usa Apollo.io che include dati LinkedIn |

---

## 2. Marketing Automation

### 2.1 Buffer/Hootsuite API
**Priorità**: 🟠 ALTA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Scheduling post multi-piattaforma |
| **Costo** | Buffer: Free 3 canali, Pro $6/mese |
| **Endpoint Base** | `https://api.bufferapp.com/1/` |
| **Auth** | OAuth 2.0 |

**Endpoints chiave**:
```
POST /updates/create.json     → Schedula post
GET /profiles.json            → Lista profili connessi
POST /updates/share.json      → Pubblica immediatamente
```

**Integrazione proposta**:
```python
# app/domain/social_publisher/buffer_service.py
class BufferService:
    async def schedule_post(self, profile_id: str, text: str, media_urls: List[str], scheduled_at: datetime)
    async def get_queue(self, profile_id: str) -> List[ScheduledPost]
    async def publish_now(self, profile_id: str, text: str) -> PostResult
```

---

### 2.2 Mailchimp API
**Priorità**: 🟠 ALTA (già in config)

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Email marketing, automazioni, audience management |
| **Costo** | Free: 500 contatti, Essentials: $13/mese |
| **Endpoint Base** | `https://<dc>.api.mailchimp.com/3.0/` |
| **Auth** | Basic Auth con API Key |

**Endpoints chiave**:
```
POST /lists/{list_id}/members      → Aggiungi subscriber
POST /campaigns                    → Crea campagna
POST /campaigns/{id}/actions/send  → Invia campagna
```

**Integrazione proposta**:
```python
# app/domain/email_marketing/mailchimp_service.py
class MailchimpService:
    async def add_subscriber(self, list_id: str, email: str, merge_fields: dict)
    async def create_campaign(self, list_id: str, subject: str, content: str) -> Campaign
    async def send_campaign(self, campaign_id: str)
    async def create_automation(self, trigger: str, emails: List[EmailTemplate])
```

---

### 2.3 Twilio API
**Priorità**: 🟡 MEDIA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | SMS, Voice, WhatsApp Business |
| **Costo** | Pay-per-use (~€0.05/SMS) |
| **Endpoint Base** | `https://api.twilio.com/2010-04-01/` |
| **Auth** | Basic Auth (Account SID + Token) |

**Endpoints chiave**:
```
POST /Accounts/{sid}/Messages.json  → Invia SMS/WhatsApp
POST /Accounts/{sid}/Calls.json     → Chiama numero
```

**Note**: WhatsApp già implementato con Cloud API nativa.

---

## 3. SEO & Analytics

### 3.1 Semrush API
**Priorità**: 🔴 CRITICA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Keyword research, competitor analysis, backlinks, audit SEO |
| **Costo** | Pro: $129.95/mese (API inclusa) |
| **Endpoint Base** | `https://api.semrush.com/` |
| **Auth** | API Key in query param |

**Endpoints chiave**:
```
GET /?type=domain_organic&domain=X  → Keywords organiche competitor
GET /?type=phrase_all&phrase=X      → Volume/difficoltà keyword
GET /?type=backlinks&target=X       → Backlink analysis
GET /?type=domain_ranks&domain=X    → Authority score
```

**Integrazione proposta**:
```python
# app/domain/seo/semrush_service.py
class SemrushService:
    async def get_organic_keywords(self, domain: str) -> List[KeywordData]
    async def analyze_keyword(self, keyword: str) -> KeywordAnalysis
    async def get_backlinks(self, domain: str) -> BacklinkReport
    async def competitor_analysis(self, my_domain: str, competitors: List[str]) -> CompetitorReport
```

---

### 3.2 Ahrefs API
**Priorità**: 🟡 MEDIA (alternativa a Semrush)

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Simile a Semrush, focus backlinks |
| **Costo** | Lite: $99/mese |
| **Endpoint Base** | `https://apiv2.ahrefs.com/` |

**Note**: Scegliere UNO tra Semrush e Ahrefs.

---

### 3.3 Google Analytics 4 API
**Priorità**: 🔴 CRITICA (già configurata)

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Web analytics, eventi, conversioni |
| **Costo** | Gratuito |
| **Endpoint Base** | `https://analyticsdata.googleapis.com/v1beta/` |
| **Auth** | OAuth 2.0 / Service Account |

**Endpoints chiave**:
```
POST /properties/{propertyId}:runReport  → Report personalizzati
POST /properties/{propertyId}:batchRunReports → Report multipli
```

**Integrazione proposta**:
```python
# app/domain/analytics/ga4_service.py
class GA4Service:
    async def get_traffic_report(self, property_id: str, date_range: DateRange) -> TrafficReport
    async def get_conversion_report(self, property_id: str) -> ConversionReport
    async def get_realtime_users(self, property_id: str) -> int
```

---

### 3.4 Google Search Console API
**Priorità**: 🔴 CRITICA (già configurata)

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Performance ricerca, indicizzazione, errori |
| **Costo** | Gratuito |
| **Endpoint Base** | `https://searchconsole.googleapis.com/v1/` |

**Endpoints chiave**:
```
POST /sites/{siteUrl}/searchAnalytics/query  → Performance keywords
GET /sites/{siteUrl}/sitemaps                → Sitemap status
```

---

### 3.5 SimilarWeb API
**Priorità**: 🟡 MEDIA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Competitive intelligence, traffic estimates, market share |
| **Costo** | Enterprise (contattare sales) |
| **Endpoint Base** | `https://api.similarweb.com/v1/` |

---

### 3.6 Brand24 API
**Priorità**: 🟢 BASSA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Social listening, brand monitoring, sentiment analysis |
| **Costo** | Individual: $99/mese |
| **Endpoint Base** | `https://api.brand24.com/v3/` |

---

## 4. AI Avanzata

### 4.1 ElevenLabs API
**Priorità**: 🔴 CRITICA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Text-to-speech ultra realistico, voice cloning |
| **Costo** | Free: 10k chars/mese, Starter: $5/mese (30k) |
| **Endpoint Base** | `https://api.elevenlabs.io/v1/` |
| **Auth** | xi-api-key header |

**Endpoints chiave**:
```
POST /text-to-speech/{voice_id}   → Genera audio
GET /voices                        → Lista voci disponibili
POST /voices/add                   → Clona voce (Premium)
```

**Integrazione proposta**:
```python
# app/domain/audio/elevenlabs_service.py
class ElevenLabsService:
    async def text_to_speech(self, text: str, voice_id: str = "default") -> bytes
    async def get_voices(self) -> List[Voice]
    async def generate_reel_audio(self, script: str, voice: str) -> AudioFile
```

**Caso d'uso**: Audio per Reels/TikTok, podcast, video marketing.

---

### 4.2 Deepgram API
**Priorità**: 🟠 ALTA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Speech-to-text, trascrizione real-time, speaker diarization |
| **Costo** | Free: $200 credit, Pay-as-you-go: $0.0043/min |
| **Endpoint Base** | `https://api.deepgram.com/v1/` |
| **Auth** | Token header |

**Endpoints chiave**:
```
POST /listen?model=nova-2    → Trascrivi file audio
WS /listen                   → Trascrizione real-time
```

**Integrazione proposta**:
```python
# app/domain/transcription/deepgram_service.py
class DeepgramService:
    async def transcribe_file(self, audio_url: str) -> Transcript
    async def transcribe_realtime(self, audio_stream) -> AsyncGenerator[str]
    async def transcribe_call(self, call_recording_url: str) -> CallTranscript
```

**Caso d'uso**: Trascrizione call commerciali per follow-up automatici.

---

### 4.3 HeyGen API
**Priorità**: ✅ GIÀ INTEGRATA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Video avatar AI |
| **Status** | Già presente in `.env.production` |

---

### 4.4 Runway ML API
**Priorità**: 🟢 BASSA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Video editing AI, Gen-3 video generation |
| **Costo** | Standard: $15/mese (625 credits) |
| **Endpoint Base** | `https://api.runwayml.com/v1/` |

---

### 4.5 Leonardo.ai API
**Priorità**: 🟡 MEDIA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Image generation avanzata, stile consistente |
| **Costo** | Apprentice: $12/mese (8500 tokens) |
| **Endpoint Base** | `https://cloud.leonardo.ai/api/rest/v1/` |

---

## 5. Business Operations

### 5.1 Stripe API
**Priorità**: 🔴 CRITICA (già in config)

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Pagamenti, abbonamenti, fatturazione |
| **Costo** | 1.4% + €0.25 per transazione |
| **Endpoint Base** | `https://api.stripe.com/v1/` |

**Endpoints chiave**:
```
POST /customers                    → Crea cliente
POST /subscriptions                → Crea abbonamento
POST /invoices                     → Genera fattura
POST /payment_intents              → Pagamento singolo
```

**Integrazione proposta**:
```python
# app/domain/billing/stripe_service.py
class StripeService:
    async def create_customer(self, email: str, name: str) -> Customer
    async def create_subscription(self, customer_id: str, price_id: str) -> Subscription
    async def generate_invoice(self, customer_id: str, items: List[InvoiceItem]) -> Invoice
```

---

### 5.2 DocuSign API
**Priorità**: 🟠 ALTA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Firma elettronica contratti |
| **Costo** | Personal: €10/mese, Standard: €25/mese |
| **Endpoint Base** | `https://demo.docusign.net/restapi/v2.1/` |
| **Auth** | OAuth 2.0 / JWT |

**Endpoints chiave**:
```
POST /accounts/{accountId}/envelopes  → Invia documento da firmare
GET /accounts/{accountId}/envelopes/{envelopeId}  → Status firma
```

**Integrazione proposta**:
```python
# app/domain/contracts/docusign_service.py
class DocuSignService:
    async def send_for_signature(self, document: bytes, signers: List[Signer]) -> Envelope
    async def get_signature_status(self, envelope_id: str) -> SignatureStatus
    async def download_signed_document(self, envelope_id: str) -> bytes
```

**Caso d'uso**: Onboarding clienti automatico con firma contratti.

---

### 5.3 Calendly API
**Priorità**: 🟠 ALTA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Scheduling appuntamenti, disponibilità |
| **Costo** | Free: base, Pro: $12/mese |
| **Endpoint Base** | `https://api.calendly.com/` |
| **Auth** | Bearer Token |

**Endpoints chiave**:
```
GET /users/me                              → Info utente
GET /event_types                           → Tipi appuntamento
GET /scheduled_events                      → Appuntamenti schedulati
POST /scheduling_links                     → Crea link booking
```

**Integrazione proposta**:
```python
# app/domain/scheduling/calendly_service.py
class CalendlyService:
    async def get_available_slots(self, event_type: str, date_range: DateRange) -> List[Slot]
    async def create_booking_link(self, event_type: str) -> str
    async def get_upcoming_meetings(self) -> List[Meeting]
```

---

### 5.4 Slack API
**Priorità**: 🟡 MEDIA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Notifiche team, bot, automazioni |
| **Costo** | Gratuito per notifiche base |
| **Endpoint Base** | `https://slack.com/api/` |

**Endpoints chiave**:
```
POST /chat.postMessage   → Invia messaggio
POST /files.upload       → Carica file
```

---

## 6. Media & Content Optimization

### 6.1 Cloudinary API
**Priorità**: 🔴 CRITICA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Gestione, ottimizzazione e trasformazione immagini/video |
| **Costo** | Free: 25GB storage, 25GB bandwidth |
| **Endpoint Base** | `https://api.cloudinary.com/v1_1/{cloud_name}/` |
| **Auth** | API Key + Secret |

**Endpoints chiave**:
```
POST /image/upload              → Upload con auto-ottimizzazione
GET /image/upload/{public_id}   → Transform on-the-fly
POST /video/upload              → Upload video
GET /<cloud>/image/upload/      → CDN delivery
```

**Integrazione proposta**:
```python
# app/domain/media/cloudinary_service.py
class CloudinaryService:
    async def upload_image(self, file: bytes, folder: str) -> ImageResult
    async def transform_image(self, public_id: str, width: int, height: int, format: str) -> str
    async def optimize_for_platform(self, public_id: str, platform: str) -> Dict[str, str]
    async def generate_responsive_urls(self, public_id: str) -> Dict[str, str]
```

**Caso d'uso**: CDN per immagini generate, resize automatico per ogni piattaforma social.

---

### 6.2 Google Translate API
**Priorità**: 🟠 ALTA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Traduzione automatica 100+ lingue |
| **Costo** | $20 per 1M caratteri |
| **Endpoint Base** | `https://translation.googleapis.com/language/translate/v2/` |
| **Auth** | API Key |

**Endpoints chiave**:
```
POST /translate              → Traduci testo
GET /languages               → Lingue supportate
POST /detect                 → Rileva lingua
```

**Integrazione proposta**:
```python
# app/domain/translation/translate_service.py
class GoogleTranslateService:
    async def translate_content(self, text: str, target_lang: str) -> str
    async def translate_batch(self, texts: List[str], target_lang: str) -> List[str]
    async def detect_language(self, text: str) -> str
    async def translate_post_multilang(self, content: str, languages: List[str]) -> Dict[str, str]
```

**Caso d'uso**: Contenuti multi-lingua per espansione mercati EU (DE, FR, ES, EN).

---

### 6.3 Unsplash/Pexels API
**Priorità**: 🟡 MEDIA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Foto stock gratuite e di alta qualità |
| **Costo** | Gratuito (rate limit: 50 req/ora) |
| **Endpoint Base** | `https://api.unsplash.com/` |
| **Auth** | Client-ID header |

**Endpoints chiave**:
```
GET /photos/random            → Foto casuale
GET /search/photos?query=X    → Cerca foto
GET /photos/{id}              → Dettagli foto
```

**Integrazione proposta**:
```python
# app/domain/media/stock_photos_service.py
class StockPhotosService:
    async def search_photos(self, query: str, count: int = 10) -> List[Photo]
    async def get_random_photo(self, topic: str) -> Photo
    async def download_photo(self, photo_id: str, size: str = "regular") -> bytes
```

**Caso d'uso**: Placeholder immagini per post quando non si hanno asset custom.

---

## 7. Search & Real-time

### 7.1 Algolia API
**Priorità**: 🟠 ALTA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Search-as-a-Service ultra veloce (<50ms) |
| **Costo** | Free: 10k ricerche/mese, Build: $29/mese |
| **Endpoint Base** | `https://{app-id}.algolia.net/1/` |
| **Auth** | API Key header |

**Endpoints chiave**:
```
POST /indexes/{index}/query          → Ricerca full-text
POST /indexes/{index}/batch          → Bulk index
POST /indexes/{index}/objects        → Aggiungi oggetti
```

**Integrazione proposta**:
```python
# app/domain/search/algolia_service.py
class AlgoliaService:
    async def index_leads(self, leads: List[Lead]) -> None
    async def search_leads(self, query: str, filters: dict) -> List[Lead]
    async def index_content(self, content: List[Content]) -> None
    async def search_content(self, query: str) -> List[Content]
```

**Caso d'uso**: Ricerca veloce nel Lead Finder e nel Content Library.

---

### 7.2 Pusher/Ably API
**Priorità**: 🟡 MEDIA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | WebSockets, real-time messaging |
| **Costo** | Free: 200k msg/giorno, Startup: $49/mese |
| **Endpoint Base** | `https://api-{cluster}.pusher.com/` |
| **Auth** | App Key + Secret |

**Endpoints chiave**:
```
POST /apps/{app_id}/events     → Publish event
GET /apps/{app_id}/channels    → Lista canali attivi
```

**Integrazione proposta**:
```python
# app/domain/realtime/pusher_service.py
class PusherService:
    async def notify_content_ready(self, user_id: str, content_id: str) -> None
    async def send_lead_alert(self, user_id: str, lead: Lead) -> None
    async def broadcast_update(self, channel: str, event: str, data: dict) -> None
```

**Caso d'uso**: Notifiche real-time quando contenuti sono pronti o lead qualificati.

---

## 8. Video & Meetings

### 8.1 Zoom API
**Priorità**: 🟠 ALTA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Video conferencing integrations |
| **Costo** | Free tier + API access con account Pro |
| **Endpoint Base** | `https://api.zoom.us/v2/` |
| **Auth** | OAuth 2.0 / JWT |

**Endpoints chiave**:
```
POST /users/{userId}/meetings              → Crea meeting
GET /users/{userId}/meetings               → Lista meeting
GET /meetings/{meetingId}                  → Dettagli meeting
DELETE /meetings/{meetingId}               → Cancella meeting
GET /meetings/{meetingId}/recordings       → Recording meeting
```

**Integrazione proposta**:
```python
# app/domain/meetings/zoom_service.py
class ZoomService:
    async def create_meeting(self, topic: str, start_time: datetime, duration: int) -> Meeting
    async def get_meeting_link(self, meeting_id: str) -> str
    async def get_recordings(self, meeting_id: str) -> List[Recording]
    async def schedule_sales_call(self, lead: Lead, datetime: datetime) -> MeetingInvite
```

**Caso d'uso**: Integrazione con Calendly per video call automatiche con lead.

---

### 8.2 Giphy API
**Priorità**: 🟢 BASSA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | GIF search e embedding |
| **Costo** | Gratuito |
| **Endpoint Base** | `https://api.giphy.com/v1/` |
| **Auth** | API Key in query |

**Endpoints chiave**:
```
GET /gifs/search?q=X     → Cerca GIF
GET /gifs/trending       → GIF trending
GET /stickers/search     → Cerca stickers
```

**Caso d'uso**: GIF per Stories e contenuti social engagement.

---

## 9. Geolocation & Data

### 9.1 IPGeolocation API
**Priorità**: 🟡 MEDIA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | IP geolocation, country detection |
| **Costo** | Free: 30k req/mese |
| **Endpoint Base** | `https://api.ipgeolocation.io/` |
| **Auth** | API Key |

**Endpoints chiave**:
```
GET /ipgeo?ip=X         → Info completa da IP
GET /timezone?ip=X      → Timezone da IP
```

**Integrazione proposta**:
```python
# app/domain/geo/ip_geolocation_service.py
class IPGeolocationService:
    async def get_visitor_location(self, ip: str) -> Location
    async def get_visitor_timezone(self, ip: str) -> str
    async def is_eu_visitor(self, ip: str) -> bool
```

**Caso d'uso**: Targeting geografico lead, compliance GDPR, localizzazione contenuti.

---

### 9.2 QR Code API
**Priorità**: 🟢 BASSA

| Campo | Valore |
|-------|--------|
| **Cosa fa** | Generazione QR codes |
| **Costo** | Gratuito |
| **Endpoint Base** | `https://api.qrserver.com/v1/` |
| **Auth** | Nessuna |

**Endpoints chiave**:
```
GET /create-qr-code/?data=X&size=200x200   → Genera QR
```

**Integrazione proposta**:
```python
# app/domain/marketing/qr_service.py
class QRCodeService:
    async def generate_qr(self, url: str, size: int = 200) -> bytes
    async def generate_vcard_qr(self, contact: Contact) -> bytes
    async def generate_tracking_qr(self, campaign_id: str) -> bytes
```

**Caso d'uso**: QR per materiale marketing, biglietti da visita, eventi.

---

## 10. Priorità Implementation (AGGIORNATA)

### 🔴 SPRINT 1 (Settimana 1-2) - Core Business
| API | Stima Sviluppo | Impatto |
|-----|----------------|---------|
| Apollo.io | 2 giorni | Lead generation potenziata |
| ElevenLabs | 1 giorno | Audio per Reels |
| Stripe (completa) | 2 giorni | Billing automatico |
| **Cloudinary** | 1 giorno | CDN immagini ottimizzate |

### 🟠 SPRINT 2 (Settimana 3-4) - Marketing & SEO
| API | Stima Sviluppo | Impatto |
|-----|----------------|---------|
| Semrush | 2 giorni | SEO content optimization |
| Mailchimp | 1 giorno | Email automation |
| Deepgram | 1 giorno | Trascrizione call |
| **Google Translate** | 1 giorno | Multi-lingua UE |

### 🟡 SPRINT 3 (Settimana 5-6) - Operations & Meetings
| API | Stima Sviluppo | Impatto |
|-----|----------------|---------|
| DocuSign | 2 giorni | Firma contratti |
| Calendly | 1 giorno | Scheduling automatico |
| Hunter.io | 1 giorno | Email verification |
| **Zoom** | 1 giorno | Video call integration |

### 🟢 SPRINT 4 (Settimana 7-8) - Search & Enhancement
| API | Stima Sviluppo | Impatto |
|-----|----------------|---------|
| Buffer | 1 giorno | Multi-platform scheduling |
| GA4 (avanzato) | 2 giorni | Dashboard analytics |
| Leonardo.ai | 1 giorno | Immagini premium |
| **Algolia** | 2 giorni | Search veloce |

### 🔵 SPRINT 5 (Settimana 9-10) - Nice-to-have
| API | Stima Sviluppo | Impatto |
|-----|----------------|---------|
| Unsplash/Pexels | 0.5 giorni | Stock photos |
| Pusher | 1 giorno | Real-time notifications |
| IPGeolocation | 0.5 giorni | Geo targeting |
| Giphy | 0.5 giorni | GIF per Stories |
| QR Code | 0.5 giorni | Marketing materiale |

---

## 📁 Struttura File (AGGIORNATA)

```
apps/ai_microservice/app/domain/
├── lead_finder/
│   ├── apollo_service.py      ← NEW
│   ├── hunter_service.py      ← NEW
│   └── clearbit_service.py    ← NEW
├── seo/
│   ├── semrush_service.py     ← NEW
│   └── ahrefs_service.py      ← NEW
├── analytics/
│   ├── ga4_service.py         ← NEW
│   └── search_console_service.py ← NEW
├── audio/
│   └── elevenlabs_service.py  ← NEW
├── transcription/
│   └── deepgram_service.py    ← NEW
├── contracts/
│   └── docusign_service.py    ← NEW
├── scheduling/
│   └── calendly_service.py    ← NEW
├── billing/
│   └── stripe_service.py      ← NEW (estendi esistente)
├── email_marketing/
│   └── mailchimp_service.py   ← NEW
├── media/                      ← NEW FOLDER
│   ├── cloudinary_service.py  ← NEW
│   └── stock_photos_service.py ← NEW
├── translation/               ← NEW FOLDER
│   └── translate_service.py   ← NEW
├── search/                    ← NEW FOLDER
│   └── algolia_service.py     ← NEW
├── realtime/                  ← NEW FOLDER
│   └── pusher_service.py      ← NEW
├── meetings/                  ← NEW FOLDER
│   └── zoom_service.py        ← NEW
├── geo/                       ← NEW FOLDER
│   └── ip_geolocation_service.py ← NEW
└── marketing/
    └── qr_service.py          ← NEW
```

---

## 🔑 Environment Variables da Aggiungere (AGGIORNATA)

```env
# Lead Intelligence
APOLLO_API_KEY=
HUNTER_API_KEY=
CLEARBIT_API_KEY=        # già presente

# SEO
SEMRUSH_API_KEY=         # già presente
AHREFS_API_KEY=          # già presente

# AI Audio/Video
ELEVENLABS_API_KEY=
DEEPGRAM_API_KEY=
LEONARDO_API_KEY=

# Business Ops
DOCUSIGN_INTEGRATION_KEY=
DOCUSIGN_USER_ID=
DOCUSIGN_ACCOUNT_ID=
CALENDLY_ACCESS_TOKEN=
BUFFER_ACCESS_TOKEN=

# Media & CDN (NEW)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Search (NEW)
ALGOLIA_APP_ID=
ALGOLIA_API_KEY=
ALGOLIA_ADMIN_KEY=

# Meetings (NEW)
ZOOM_CLIENT_ID=
ZOOM_CLIENT_SECRET=
ZOOM_ACCOUNT_ID=

# Real-time (NEW)
PUSHER_APP_ID=
PUSHER_KEY=
PUSHER_SECRET=
PUSHER_CLUSTER=

# Geo (NEW)
IPGEOLOCATION_API_KEY=

# Stock Photos (NEW)
UNSPLASH_ACCESS_KEY=
PEXELS_API_KEY=

# Translation (usa GOOGLE_API_KEY esistente)
```

---

## ✅ Checklist Implementazione (AGGIORNATA)

### Core
- [ ] Sprint 1: Apollo.io, ElevenLabs, Stripe, Cloudinary
- [ ] Sprint 2: Semrush, Mailchimp, Deepgram, Google Translate
- [ ] Sprint 3: DocuSign, Calendly, Hunter.io, Zoom
- [ ] Sprint 4: Buffer, GA4 avanzato, Leonardo.ai, Algolia
- [ ] Sprint 5: Unsplash, Pusher, IPGeo, Giphy, QR

### Quality
- [ ] Testing end-to-end per sprint
- [ ] Documentazione API interne
- [ ] Rate limiting e caching
- [ ] Error handling robusto
- [ ] Deploy produzione

---

## 📞 Contatti API (per chiavi) - COMPLETA

| API | Link Signup |
|-----|-------------|
| Apollo.io | https://app.apollo.io/signup |
| ElevenLabs | https://elevenlabs.io/sign-up |
| Semrush | https://www.semrush.com/signup/ |
| Deepgram | https://console.deepgram.com/signup |
| DocuSign | https://developers.docusign.com/ |
| Calendly | https://developer.calendly.com/ |
| Hunter.io | https://hunter.io/users/sign_up |
| **Cloudinary** | https://cloudinary.com/users/register_free |
| **Algolia** | https://www.algolia.com/users/sign_up |
| **Zoom** | https://marketplace.zoom.us/develop/create |
| **Pusher** | https://dashboard.pusher.com/accounts/sign_up |
| **Unsplash** | https://unsplash.com/developers |
| **IPGeolocation** | https://ipgeolocation.io/signup |

---

## 📊 Riepilogo Totale

| Categoria | API Count | Stima Totale |
|-----------|-----------|--------------|
| Lead Intelligence | 4 | 5 giorni |
| Marketing Automation | 3 | 3 giorni |
| SEO & Analytics | 6 | 7 giorni |
| AI Avanzata | 5 | 5 giorni |
| Business Operations | 4 | 5 giorni |
| Media & Content | 3 | 2 giorni |
| Search & Real-time | 2 | 3 giorni |
| Video & Meetings | 2 | 1.5 giorni |
| Geo & Data | 2 | 1 giorno |
| **TOTALE** | **31 API** | **~32.5 giorni** |

---

**Documento creato**: 2025-12-13
**Ultimo aggiornamento**: 2025-12-13 (Aggiunta sezioni 6-9 da top-50 list)
**Prossimo aggiornamento**: Al completamento Sprint 1
