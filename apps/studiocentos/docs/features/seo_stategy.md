# SEO Strategy Feature Walkthrough

Implemented a new "SEO Strategy" feature in the Marketing Lead section capable of generating keyword opportunities and content plans.

## Changes

### Backend (`app.core.api.v1.marketing.py`)
- Added `POST /api/v1/marketing/seo/strategy` endpoint.
- Integrated [SEOAgent](file:///home/autcir_gmail_com/develop/apps/studiocentos/apps/ai_microservice/app/domain/marketing/seo_specialist.py#183-1503) to perform keyword research (using Google Search Console with fallback).
- Implemented logic to map keywords to a "Content Plan" (Blog Posts vs Landing Pages).

### Backend (`app.domain.marketing.seo_specialist.py`)
- Fixed [SEOAgent](file:///home/autcir_gmail_com/develop/apps/studiocentos/apps/ai_microservice/app/domain/marketing/seo_specialist.py#183-1503) instantiation errors by implementing abstract methods [get_capabilities](file:///home/autcir_gmail_com/develop/apps/studiocentos/apps/ai_microservice/app/domain/marketing/social_media_manager.py#268-296) and [execute](file:///home/autcir_gmail_com/develop/apps/studiocentos/apps/ai_microservice/app/domain/marketing/content_creator.py#1374-1420).
- Removed incorrect `super().on_start()` calls.

### Frontend ([LeadFinderInline.tsx](file:///home/autcir_gmail_com/develop/apps/studiocentos/apps/frontend/src/features/admin/pages/AIMarketing/components/LeadFinderInline.tsx))
- Added "Strategia SEO" button to the header of the Lead Finder component.
- Integrated [SEOStrategyModal](file:///home/autcir_gmail_com/develop/apps/studiocentos/apps/frontend/src/features/admin/pages/AIMarketing/components/SEOStrategyModal.tsx#34-188) to handle the interaction.

### Frontend ([SEOStrategyModal.tsx](file:///home/autcir_gmail_com/develop/apps/studiocentos/apps/frontend/src/features/admin/pages/AIMarketing/components/SEOStrategyModal.tsx))
- Created a new modal component.
- Displays "Genera Strategia" button.
- Shows results in a Keywords Table and a Content Plan card list.
- **UI Styling**: Applied "Premium Gold" aesthetic to match [BatchContentModal](file:///home/autcir_gmail_com/develop/apps/studiocentos/apps/frontend/src/features/admin/pages/AIMarketing/components/BatchContentModal.tsx#21-453), using gold borders, text accents (`text-gold`), and gradients.

## Verification results

### Backend Test
Ran [manual_test_seo_strategy.py](file:///home/autcir_gmail_com/develop/apps/studiocentos/apps/ai_microservice/manual_test_seo_strategy.py) inside the container:
```
✅ Strategy Generated Successfully!
Keywords Found: 5
 - Web Agency AI (Vol: 500, Diff: KeywordDifficulty.MEDIUM)
 - best Web Agency AI (Vol: 100, Diff: KeywordDifficulty.EASY)
...
Content Plan Items: 5
 - [Blog Post] Web Agency Ai: La Guida Completa per il 2025
...
```

## User Instructions
1.  **Restart Backend**: To ensure the new endpoint is active.
    ```bash
    docker restart studiocentos-ai
    ```
2.  **Access Marketing Hub**: Go to the "Trova Clienti" (Leads) tab.
3.  **Click Button**: Click "Strategia SEO" in the top right.
4.  **Generate**: Click "Genera Strategia Ora" in the modal.

## Future Improvements
- Connect to a real database to save the Strategy.
- Allow users to customize "Seed Topics" in the modal (currently hardcoded defaults).
