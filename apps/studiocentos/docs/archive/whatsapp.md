# WhatsApp Cloud API Integration

Integrazione del canale WhatsApp Business nel progetto StudioCentOS per:
- Invio messaggi di marketing ai lead dell'acquisition pipeline
- Notifiche automatiche (booking confirmations, follow-ups)
- Future: Chatbot AI integration

> [!IMPORTANT]
> L'API **On-Premises è stata deprecata**. Questa implementazione usa esclusivamente la **WhatsApp Cloud API**.

## User Review Required

> [!WARNING]
> **Credenziali Meta Business richieste:**
> - `WHATSAPP_PHONE_NUMBER_ID` - ID del numero WhatsApp Business
> - `WHATSAPP_ACCESS_TOKEN` - Token di accesso permanente
> - `WHATSAPP_BUSINESS_ACCOUNT_ID` - Account business ID
> - `WHATSAPP_WEBHOOK_VERIFY_TOKEN` - Token per verifica webhook
>
> Queste credenziali devono essere configurate nel [Meta Business Manager](https://business.facebook.com/settings/whatsapp-business-accounts/).

---

## Proposed Changes

### Core Configuration

#### [MODIFY] [config.py](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/core/config.py)

Aggiunta variabili d'ambiente per WhatsApp Cloud API:

```python
# WhatsApp Cloud API
WHATSAPP_PHONE_NUMBER_ID: str = Field(default="", description="WhatsApp Business Phone Number ID")
WHATSAPP_ACCESS_TOKEN: str = Field(default="", description="WhatsApp Cloud API Access Token")
WHATSAPP_BUSINESS_ACCOUNT_ID: str = Field(default="", description="WhatsApp Business Account ID")
WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = Field(default="", description="Webhook verification token")
WHATSAPP_API_VERSION: str = Field(default="v18.0", description="Meta Graph API version")
```

---

### WhatsApp Domain

#### [NEW] [whatsapp/](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/domain/whatsapp/)

Nuovo dominio con struttura standard:

```
apps/backend/app/domain/whatsapp/
├── __init__.py
├── models.py      # SQLAlchemy models (WhatsAppMessage, WhatsAppTemplate)
├── schemas.py     # Pydantic schemas
├── service.py     # WhatsAppService - Cloud API integration
├── router.py      # API endpoints
└── webhook.py     # Webhook handler per message status
```

#### [NEW] models.py

```python
class WhatsAppMessageStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    waba_id: Mapped[str]          # WhatsApp message ID from API
    lead_id: Mapped[Optional[int]] = mapped_column(ForeignKey("leads.id"))
    phone_number: Mapped[str]      # Recipient phone
    template_name: Mapped[Optional[str]]
    message_text: Mapped[Optional[str]]
    status: Mapped[str] = mapped_column(default=WhatsAppMessageStatus.PENDING)
    error_message: Mapped[Optional[str]]
    sent_at: Mapped[Optional[datetime]]
    delivered_at: Mapped[Optional[datetime]]
    read_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime]
```

#### [NEW] service.py

Pattern basato su [EmailMarketingService](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/domain/marketing/email_service.py#81-636):

| Metodo | Descrizione |
|--------|-------------|
| `send_template_message()` | Invio template pre-approvato |
| `send_text_message()` | Invio messaggio testo (solo entro 24h window) |
| `get_templates()` | Lista template approvati |
| `track_status()` | Aggiornamento status da webhook |

#### [NEW] router.py

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/whatsapp/send` | POST | Invia messaggio template |
| `/whatsapp/send-bulk` | POST | Invio massivo a lista lead |
| `/whatsapp/templates` | GET | Lista template disponibili |
| `/whatsapp/messages` | GET | Storico messaggi inviati |
| `/whatsapp/webhook` | GET/POST | Webhook Meta (verifica + eventi) |

---

### Database Migration

#### [NEW] whatsapp_messages migration

```sql
CREATE TABLE whatsapp_messages (
    id SERIAL PRIMARY KEY,
    waba_id VARCHAR(100) UNIQUE,
    lead_id INTEGER REFERENCES leads(id),
    phone_number VARCHAR(20) NOT NULL,
    template_name VARCHAR(100),
    message_text TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_whatsapp_messages_lead ON whatsapp_messages(lead_id);
CREATE INDEX idx_whatsapp_messages_status ON whatsapp_messages(status);
```

---

### App Registration

#### [MODIFY] [main.py](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/main.py)

Registrazione nuovo router:

```python
from app.domain.whatsapp.router import router as whatsapp_router

app.include_router(whatsapp_router, prefix="/api/v1")
```

---

## Verification Plan

### Automated Tests

#### Unit Tests (nuovi)

File: `apps/backend/tests/domain/whatsapp/test_whatsapp_service.py`

```bash
cd /home/autcir_gmail_com/studiocentos_ws/apps/backend
pytest tests/domain/whatsapp/ -v
```

Test coverage:
1. `test_send_template_message_success` - Mock API response
2. `test_send_template_message_invalid_phone` - Validazione numero
3. `test_webhook_status_update` - Aggiornamento status da callback
4. `test_get_templates` - Recupero template list

### Manual Verification

1. **Config check**: Verificare che le variabili siano caricate correttamente:
   ```bash
   cd /home/autcir_gmail_com/studiocentos_ws/apps/backend
   python -c "from app.core.config import settings; print(settings.WHATSAPP_PHONE_NUMBER_ID)"
   ```

2. **API Endpoint test** (richiede credenziali reali):
   ```bash
   curl -X POST http://localhost:8000/api/v1/whatsapp/send \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"phone": "+393331234567", "template_name": "hello_world"}'
   ```

3. **Webhook verification**: Il webhook Meta richiede HTTPS. Per testing locale, usare ngrok:
   ```bash
   ngrok http 8000
   # Configurare callback URL in Meta Business Manager
   ```
