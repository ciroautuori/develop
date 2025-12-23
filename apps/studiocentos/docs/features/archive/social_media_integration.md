# Social Media Integration Plan

## Objetivo
Integrare le credenziali Meta/Facebook e Threads fornite dall'utente per automatizzare la pubblicazione di contenuti generati dall'AI Marketing.

## Credenziali Fornite

### Facebook/Meta App
- **App Name**: StudioCentOS-Marketing
- **App ID**: `832697706350252`
- **App Secret**: `8d1a6eddb0e4391bd2703cc5f651abd0`

### Threads App
- **App ID**: `1142047478046537`
- **App Secret**: `b20c55e8e7a2338cba0fe0eefc6583e5`

## Proposed Changes

### 1. Backend Configuration
**File**: [apps/backend/app/core/config.py](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/core/config.py)
- Add Meta/Facebook credentials
- Add Threads credentials
- Add feature flags for social media publishing

### 2. Environment Variables
**File**: [config/docker/.env.production](file:///home/autcir_gmail_com/studiocentos_ws/config/docker/.env.production) (example)
```bash
# Meta/Facebook Integration
META_APP_ID=832697706350252
META_APP_SECRET=8d1a6eddb0e4391bd2703cc5f651abd0
META_ACCESS_TOKEN=  # Long-lived token (to be generated)

# Threads Integration
THREADS_APP_ID=1142047478046537
THREADS_APP_SECRET=b20c55e8e7a2338cba0fe0eefc6583e5
THREADS_ACCESS_TOKEN=  # Long-lived token (to be generated)
```

### 3. Update Social Media Integration
**File**: [apps/backend/app/integrations/social_media.py](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/integrations/social_media.py)
- Add Meta Graph API client
- Add Threads API client
- Implement post publishing methods

### 4. Extend Copilot Router
**File**: [apps/backend/app/domain/copilot/routers.py](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/domain/copilot/routers.py)
- Add `POST /marketing/publish` endpoint
- Support multi-platform publishing (Facebook, Threads, LinkedIn, etc.)

### 5. Frontend Enhancement (Optional)
**File**: [apps/frontend/src/features/admin/pages/AIMarketing.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/admin/pages/AIMarketing.tsx)
- Add "Publish" button dopo content generation
- Show preview before publishing
- Multi-platform selection

## Implementation Steps

1. **Add credentials to config.py** ✅
2. **Update [.env.production](file:///home/autcir_gmail_com/studiocentos_ws/.env.production) template** ✅
3. **Extend [social_media.py](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/integrations/social_media.py) with Meta/Threads support** ✅
4. **Add publishing endpoint to copilot router** ✅
5. **Update frontend with publish functionality** (Optional)

## Security Notes

> [!IMPORTANT]
> - App secrets devono essere salvati in [.env.production](file:///home/autcir_gmail_com/studiocentos_ws/.env.production) e NON committati in Git
> - Access tokens dovranno essere generati tramite OAuth flow
> - Consider using long-lived tokens (60 days) per evitare re-auth continuo

## Next Actions

1. Generare long-lived access token per Meta
2. Generare long-lived access token per Threads
3. Testare pubblicazione su account test
4. Deploy in produzione
