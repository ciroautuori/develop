# 🤖 MARKETING CONTENT SCHEDULER - Setup & Configuration

**Generazione automatica quotidiana di contenuti social con AI Batch Generator**

---

## 🎯 Overview

Lo **Marketing Content Scheduler** è un sistema automatizzato che genera ogni giorno un pacchetto completo di contenuti per tutti i tuoi social media:

- **4 Post** (1 per platform: Instagram, Facebook, TikTok, LinkedIn)
- **3 Stories** (Instagram/Facebook formato 9:16)
- **1 Video** (15s Reel/TikTok con audio nativo)

**Totale: 8 assets professionali pronti per la pubblicazione!**

---

## ⚙️ Configurazione

### Environment Variables

Aggiungi al file `.env` del backend:

```bash
# ============================================
# MARKETING CONTENT SCHEDULER
# ============================================

# Abilita/disabilita scheduler automatico
MARKETING_AUTO_GENERATION=true  # false per disabilitare

# Schedule time (CET timezone)
MARKETING_SCHEDULE_HOUR=7       # 07:00 AM
MARKETING_SCHEDULE_MINUTE=0     # Minuti

# Platforms target
MARKETING_PLATFORMS=instagram,facebook,tiktok,linkedin

# Content counts
MARKETING_POST_COUNT=1          # Post per platform
MARKETING_STORY_COUNT=3         # Stories totali
MARKETING_VIDEO_COUNT=1         # Videos totali

# Quality
MARKETING_USE_PRO=false         # true = 4K Pro mode ($0.40/day), false = FREE ($0.20/day)

# Auto-publish
MARKETING_AUTO_PUBLISH=false    # true = pubblica automaticamente, false = salva come DRAFT

# Topics (rotating by day of week) - separati da |
MARKETING_TOPICS=Digitalizzazione per PMI italiane|Strategie Marketing Digitale B2B|Automazione AI per servizi professionali|Trasformazione digitale manifatturiero|Social Media Marketing 2025|SEO e visibilità online PMI|Customer Experience digitale

# AI Microservice connection
AI_SERVICE_URL=http://ai_microservice:8001
AI_SERVICE_API_KEY=your-secure-api-key-here
```

---

## 🚀 Come Funziona

### 1. Automatic Daily Generation

Ogni giorno alle **7:00 AM CET**, lo scheduler:

1. **Seleziona topic** - Rotazione automatica basata sul giorno della settimana
2. **Genera contenuti** - Chiama `/api/v1/marketing/content/batch/generate`
3. **Salva come ScheduledPost** - Crea record nel database
4. **Schedule pubblicazione** - Orari ottimali per ogni platform

```python
# Orari ottimali pre-configurati:
{
    "instagram_post": 18:00,    # Peak engagement
    "facebook_post": 13:00,     # Lunch break
    "tiktok_post": 19:00,       # Evening peak
    "linkedin_post": 9:00,      # Morning professional
    "instagram_story_1": 8:00,  # Morning commute
    "instagram_story_2": 13:00, # Lunch
    "instagram_story_3": 20:00, # Evening
    "instagram_video": 18:00,   # Same as post
}
```

### 2. Manual Trigger (On-Demand)

Puoi generare contenuti manualmente tramite API:

```bash
# Trigger con topic default
curl -X POST http://localhost:8002/api/v1/marketing/scheduler/trigger \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Trigger con topic personalizzato
curl -X POST http://localhost:8002/api/v1/marketing/scheduler/trigger \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_topic": "Black Friday 2025 - Offerte speciali digitalizzazione"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Daily content generated successfully",
  "campaign_id": "daily_20251203",
  "posts_created": 8,
  "topic": "Digitalizzazione per PMI italiane - 03 December 2025",
  "generation_time": 387,
  "cost": 0.20,
  "scheduled_posts": [
    {
      "id": 123,
      "platform": "instagram",
      "content_type": "post",
      "scheduled_at": "2025-12-03T18:00:00Z",
      "status": "draft"
    }
  ]
}
```

---

## 📊 Monitoring & Control

### 1. Check Scheduler Status

```bash
GET /api/v1/marketing/scheduler/status
```

**Response:**
```json
{
  "is_running": true,
  "enabled": true,
  "schedule": "07:00 CET",
  "platforms": ["instagram", "facebook", "tiktok", "linkedin"],
  "post_count": 1,
  "story_count": 3,
  "video_count": 1,
  "use_pro_quality": false,
  "auto_publish": false,
  "next_run": "2025-12-04T06:00:00Z",
  "topics_count": 7
}
```

### 2. Get Topics Rotation

```bash
GET /api/v1/marketing/scheduler/topics
```

**Response:**
```json
{
  "topics": [
    "Digitalizzazione per PMI italiane",
    "Strategie Marketing Digitale B2B",
    "Automazione AI per servizi professionali",
    ...
  ],
  "count": 7,
  "current_day": 2,
  "today_topic_index": 2
}
```

### 3. Start/Stop Scheduler

```bash
# Start
POST /api/v1/marketing/scheduler/start

# Stop
POST /api/v1/marketing/scheduler/stop
```

---

## 🔄 Workflow Completo

### Scenario 1: Auto-Publish Disabled (Recommended)

```
07:00 AM - Scheduler genera 8 assets
   ↓
Database: Salva come DRAFT con orari ottimali
   ↓
Dashboard: Admin revisiona contenuti
   ↓
Admin: Approva o modifica
   ↓
PostScheduler: Pubblica agli orari schedulati
```

### Scenario 2: Auto-Publish Enabled (Advanced)

```
07:00 AM - Scheduler genera 8 assets
   ↓
Database: Salva come SCHEDULED con orari ottimali
   ↓
PostScheduler: Auto-pubblica agli orari programmati
   ↓
Metrics: Traccia engagement automaticamente
```

---

## 💰 Costi & Budget

### FREE Tier (Default)

```
MARKETING_USE_PRO=false

Daily generation:
- 4 posts (FREE Nano Banana 1K) = $0
- 3 stories (FREE) = $0
- 1 video (Veo 3.1) = $0.20

Total: $0.20/day = $6/month
```

### PRO Tier (4K Quality)

```
MARKETING_USE_PRO=true

Daily generation:
- 4 posts (Pro 4K) = $0.20
- 3 stories (standard) = $0
- 1 video (Veo 3.1) = $0.20

Total: $0.40/day = $12/month
```

### Google FREE Tier Quotas

- **Nano Banana:** ~50-100 immagini/giorno GRATIS
- **Veo 3.1:** Pay-per-use (~$0.20/video)

Con FREE mode, usi solo quota video (già pagato), immagini GRATIS!

---

## 🛠️ Troubleshooting

### Scheduler non parte

```bash
# Check logs
docker logs studiocentos-backend --tail 100 | grep "marketing_scheduler"

# Verifica env var
docker exec -it studiocentos-backend env | grep MARKETING

# Expected:
# MARKETING_AUTO_GENERATION=true
# MARKETING_SCHEDULE_HOUR=7
```

### Generazione fallisce

```bash
# Check AI Microservice
curl http://ai_microservice:8001/health

# Check API key
echo $AI_SERVICE_API_KEY

# Test manual generation
curl -X POST http://localhost:8002/api/v1/marketing/scheduler/trigger \
  -H "Authorization: Bearer TOKEN"
```

### Contenuti non vengono pubblicati

```bash
# Check PostScheduler
curl http://localhost:8002/api/v1/marketing/calendar/posts?status=scheduled

# Verifica MARKETING_AUTO_PUBLISH
# Se false, contenuti salvati come DRAFT (serve approvazione manuale)
```

---

## 📋 Database Schema

I contenuti generati vengono salvati in `scheduled_posts`:

```sql
SELECT
    id,
    campaign_id,
    content_type,
    platforms,
    scheduled_at,
    status,
    media_urls,
    metadata->'generated_by' as source
FROM scheduled_posts
WHERE metadata->>'generated_by' = 'marketing_scheduler'
ORDER BY scheduled_at DESC;
```

---

## 🎨 Frontend Integration (TODO)

### Dashboard Widget

```typescript
// src/features/admin/components/MarketingSchedulerWidget.tsx

const MarketingSchedulerWidget = () => {
  const [status, setStatus] = useState<SchedulerStatus>();

  useEffect(() => {
    fetch('/api/v1/marketing/scheduler/status')
      .then(r => r.json())
      .then(setStatus);
  }, []);

  const triggerGeneration = async () => {
    const result = await fetch('/api/v1/marketing/scheduler/trigger', {
      method: 'POST'
    });
    const data = await result.json();
    toast.success(`Generated ${data.posts_created} assets!`);
  };

  return (
    <Card>
      <CardHeader>
        <h3>🤖 Auto Content Generator</h3>
        <Badge variant={status?.is_running ? "success" : "warning"}>
          {status?.is_running ? "Active" : "Inactive"}
        </Badge>
      </CardHeader>

      <CardContent>
        <p>Next run: {status?.next_run}</p>
        <p>Schedule: {status?.schedule}</p>
        <Button onClick={triggerGeneration}>
          ⚡ Generate Now
        </Button>
      </CardContent>
    </Card>
  );
};
```

---

## 🔐 Security

- ✅ Richiede **Admin authentication** per tutti gli endpoint
- ✅ API key sicura per AI Microservice
- ✅ Rate limiting su generazione manuale
- ✅ Logging completo di tutte le operazioni

---

## 📈 Analytics & Metrics

### Post Performance Tracking

Lo `PostScheduler` aggiorna automaticamente ogni ora le metriche:

```python
# Metrics aggiornate automaticamente:
{
    "instagram": {
        "likes": 245,
        "comments": 12,
        "shares": 8,
        "reach": 3421,
        "engagement_rate": 7.8
    },
    "facebook": {
        "reactions": 189,
        "comments": 23,
        "shares": 45,
        "reach": 5632
    }
}
```

### Cost Tracking

```sql
-- Monthly cost report
SELECT
    DATE(scheduled_at) as date,
    COUNT(*) as posts_generated,
    SUM((metadata->>'batch_cost')::float) as daily_cost
FROM scheduled_posts
WHERE metadata->>'generated_by' = 'marketing_scheduler'
  AND scheduled_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(scheduled_at)
ORDER BY date DESC;
```

---

## 🎯 Best Practices

### 1. Start with DRAFT mode

```bash
MARKETING_AUTO_PUBLISH=false
```

Rivedi manualmente i primi giorni per verificare qualità.

### 2. Monitor costs

```bash
# Check mensile
curl /api/v1/marketing/analytics/costs?period=month
```

### 3. Rotate topics

Aggiorna `MARKETING_TOPICS` ogni mese con nuove campagne:

```bash
MARKETING_TOPICS=Black Friday 2025|Natale Digital|Capodanno Tech|...
```

### 4. A/B Testing

Usa trigger manuale per testare varianti:

```bash
# Variante A
curl -X POST /scheduler/trigger -d '{"custom_topic": "Prezzo competitivo"}'

# Variante B
curl -X POST /scheduler/trigger -d '{"custom_topic": "Qualità premium"}'
```

Confronta metriche dopo 48h e usa la migliore per auto-generation.

---

## 🚀 Quick Start

### 1. Abilita scheduler

```bash
# In .env backend
MARKETING_AUTO_GENERATION=true
MARKETING_AUTO_PUBLISH=false  # Start with manual review
```

### 2. Restart backend

```bash
docker-compose -f config/docker/docker-compose.production.yml restart backend
```

### 3. Verifica avvio

```bash
docker logs studiocentos-backend --tail 50 | grep "marketing_scheduler"

# Expected:
# marketing_scheduler_started schedule=07:00 CET platforms=['instagram', 'facebook', 'tiktok', 'linkedin']
```

### 4. Test immediato

```bash
curl -X POST http://localhost:8002/api/v1/marketing/scheduler/trigger \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  | jq
```

### 5. Check risultati

```bash
curl http://localhost:8002/api/v1/marketing/calendar/posts?campaign_id=daily_$(date +%Y%m%d) \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 📞 Support

- **Logs:** `docker logs studiocentos-backend | grep marketing_scheduler`
- **Status endpoint:** `GET /api/v1/marketing/scheduler/status`
- **Manual trigger:** `POST /api/v1/marketing/scheduler/trigger`

---

**Made with 🤖🍌⭐🎥 by StudioCentOS AI Team**

**"1 POST + 3 STORIE + 1 VIDEO AL GIORNO" → ✅ COMPLETAMENTE AUTOMATIZZATO!**
