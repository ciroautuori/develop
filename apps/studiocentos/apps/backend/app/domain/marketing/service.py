"""
Marketing Service - Lead Generation + Email Automation
Sistema automatico per Salerno e Campania
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import json

from .models import Lead, EmailCampaign, LeadSource, LeadStatus, BrandSettings
import os
import httpx
from .schemas import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadListResponse,
    EmailCampaignCreate,
    EmailCampaignResponse,
    GenerateEmailRequest,
    GenerateEmailResponse
)


class MarketingService:
    """Service per lead generation e email automation."""

    # ========================================================================
    # LEAD MANAGEMENT
    # ========================================================================

    @staticmethod
    def create_lead(db: Session, data: LeadCreate) -> LeadResponse:
        """Crea nuovo lead."""

        # Check if email exists
        check_query = text("SELECT id FROM leads WHERE email = :email")
        existing = db.execute(check_query, {"email": data.email}).fetchone()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lead con email {data.email} già esistente"
            )

        # Insert lead
        insert_query = text("""
            INSERT INTO leads (
                company_name, contact_name, email, phone, website,
                city, region, address,
                source, status,
                industry, company_size,
                notes, tags, custom_fields, score,
                created_at, updated_at
            ) VALUES (
                :company_name, :contact_name, :email, :phone, :website,
                :city, :region, :address,
                :source, :status,
                :industry, :company_size,
                :notes, :tags, :custom_fields, :score,
                NOW(), NOW()
            ) RETURNING id
        """)

        result = db.execute(insert_query, {
            "company_name": data.company_name,
            "contact_name": data.contact_name,
            "email": data.email,
            "phone": data.phone,
            "website": data.website,
            "city": data.city,
            "region": data.region,
            "address": data.address,
            "source": data.source.value,
            "status": data.status.value,
            "industry": data.industry,
            "company_size": data.company_size,
            "notes": data.notes,
            "tags": json.dumps(data.tags),
            "custom_fields": json.dumps(data.custom_fields),
            "score": data.score
        })

        lead_id = result.scalar()
        db.commit()

        # Get created lead
        return MarketingService.get_lead(db, lead_id)

    @staticmethod
    def get_lead(db: Session, lead_id: int) -> LeadResponse:
        """Ottieni lead per ID."""
        query = text("""
            SELECT id, company_name, contact_name, email, phone, website,
                   city, region, address,
                   source, status,
                   industry, company_size,
                   notes, tags, custom_fields, score,
                   last_contact_date, next_followup_date,
                   created_at, updated_at
            FROM leads
            WHERE id = :lead_id
        """)

        row = db.execute(query, {"lead_id": lead_id}).fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead {lead_id} non trovato"
            )

        return LeadResponse(
            id=row[0],
            company_name=row[1],
            contact_name=row[2],
            email=row[3],
            phone=row[4],
            website=row[5],
            city=row[6],
            region=row[7],
            address=row[8],
            source=row[9],
            status=row[10],
            industry=row[11],
            company_size=row[12],
            notes=row[13],
            tags=row[14] or [],
            custom_fields=row[15] or {},
            score=row[16],
            last_contact_date=row[17],
            next_followup_date=row[18],
            created_at=row[19],
            updated_at=row[20]
        )

    @staticmethod
    def search_leads_salerno_campania(
        db: Session,
        page: int = 1,
        page_size: int = 20
    ) -> LeadListResponse:
        """
        Ricerca automatica lead Salerno/Campania.

        External API integrations (Phase 3): Google Maps, LinkedIn, CCIAA
        """

        where_clause = "WHERE (city ILIKE '%salerno%' OR region ILIKE '%campania%')"

        # Count
        count_query = f"SELECT COUNT(*) FROM leads {where_clause}"
        total = db.execute(text(count_query)).scalar() or 0

        # Get leads
        offset = (page - 1) * page_size
        query = f"""
            SELECT id, company_name, contact_name, email, phone, website,
                   city, region, address,
                   source, status,
                   industry, company_size,
                   notes, tags, custom_fields, score,
                   last_contact_date, next_followup_date,
                   created_at, updated_at
            FROM leads
            {where_clause}
            ORDER BY score DESC, created_at DESC
            LIMIT :limit OFFSET :offset
        """

        result = db.execute(text(query), {"limit": page_size, "offset": offset})
        rows = result.fetchall()

        leads = []
        for row in rows:
            leads.append(LeadResponse(
                id=row[0],
                company_name=row[1],
                contact_name=row[2],
                email=row[3],
                phone=row[4],
                website=row[5],
                city=row[6],
                region=row[7],
                address=row[8],
                source=row[9],
                status=row[10],
                industry=row[11],
                company_size=row[12],
                notes=row[13],
                tags=row[14] or [],
                custom_fields=row[15] or {},
                score=row[16],
                last_contact_date=row[17],
                next_followup_date=row[18],
                created_at=row[19],
                updated_at=row[20]
            ))

        return LeadListResponse(
            items=leads,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )

    # ========================================================================
    # EMAIL GENERATION with AI
    # ========================================================================

    @staticmethod
    async def generate_email_with_ai(
        db: Session,
        request: GenerateEmailRequest,
        admin = None
    ) -> GenerateEmailResponse:
        """
        Genera email personalizzata con AI.
        Usa iModels per generare contenuto.
        """

        # Get available AI model
        model_query = text("""
            SELECT slug, model_id FROM ai_models
            WHERE is_active = true
            ORDER BY is_featured DESC
            LIMIT 1
        """)
        model_row = db.execute(model_query).fetchone()

        if not model_row:
             # Default to llama if not found
             model_slug = "llama-3.3-70b"
        else:
             model_slug = model_row[0]

        # Fetch Brand DNA
        brand_context = ""
        brand = None
        if admin:
            brand = db.query(BrandSettings).filter(BrandSettings.admin_id == admin.id).first()
            if brand:
                brand_context = f"""
BRAND IDENTITY: {brand.company_name or 'Azienda'}
Tone of Voice: {brand.tone_of_voice.value}
Valori: {', '.join(brand.values)}
Parole da evitare: {', '.join(brand.forbidden_words)}
Mission: {brand.description or ''}
Target: {brand.target_audience or ''}
"""

        # Call AI Microservice
        ai_url = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")

        try:
             async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{ai_url}/api/v1/marketing/content/generate",
                    json={
                        "topic": f"Email marketing per {request.target_industry} a {request.target_region}",
                        "tone": request.tone or (brand.tone_of_voice.value if brand else "professional"),
                        "type": "newsletter",
                        "brand_context": brand_context,
                        "call_to_action": "Prenota consulenza gratuita"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data.get("content", "")
                    # Simple parse for subject/body if AI returns markdown or plain text
                    # Ideally AI returns JSON but ContentCreatorAgent returns string.
                    # We will wrap it.

                    # Fallback parsing/splitting if content is just text
                    lines = content.split('\n')
                    subject = lines[0].replace('Subject:', '').replace('Oggetto:', '').strip()
                    body = '\n'.join(lines[1:]).strip()

                    # Convert body to HTML
                    html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
    <div style="background: #D4AF37; padding: 20px; text-align: center;"><h1>{brand.company_name if brand else 'StudioCentOS'}</h1></div>
    <div style="padding: 20px; background: #fff;">
        {body.replace(chr(10), '<br>')}
    </div>
    <div style="padding: 20px; text-align: center; font-size: 12px; color: #666;">
        <p>Inviato con MarketingHub AI</p>
    </div>
</body>
</html>
"""
                    return GenerateEmailResponse(
                        subject=subject,
                        html_content=html_content,
                        text_content=body
                    )

        except Exception as e:
            print(f"AI Service Error: {e}")
            # Fallback to template if AI fails
            pass

        # Fallback Template logic when AI service unavailable
        # iModels API integration in ai_microservice/app/core/api/v1/marketing.py

        subject = f"🚀 Trasforma il tuo business con AI - {request.target_region}"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #D4AF37; color: #000; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .cta {{ background: #D4AF37; color: #000; padding: 15px 30px; text-decoration: none; display: inline-block; margin: 20px 0; border-radius: 5px; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>STUDIOCENTOS</h1>
            <p>Software House Salerno</p>
        </div>
        <div class="content">
            <h2>Ciao da {request.target_region}! 👋</h2>
            <p>Sono Ciro di StudioCentOS, software house specializzata in:</p>
            <ul>
                <li>🤖 <strong>AI Integration</strong> - Chatbot, RAG, Automation</li>
                <li>💻 <strong>Sviluppo Software</strong> - React, FastAPI, Enterprise</li>
                <li>📱 <strong>App Mobile</strong> - iOS e Android</li>
                <li>🌐 <strong>Web Development</strong> - Siti e webapp</li>
            </ul>
            <p>Trasformiamo la tua idea in prodotto digitale in <strong>45 giorni</strong>.</p>
            <p><strong>Specializzazione {request.target_industry}:</strong> Soluzioni su misura per il tuo settore.</p>

            <a href="https://studiocentos.it#prenota" class="cta">
                📅 Prenota Consulenza Gratuita 30min
            </a>

            <p><small>Made in {request.target_region} 🇮🇹 | Rispondo entro 24h</small></p>
        </div>
        <div class="footer">
            <p><strong>StudioCentOS</strong><br>
            Salerno, Campania<br>
            info@studiocentos.it<br>
            https://studiocentos.it</p>
        </div>
    </div>
</body>
</html>
"""

        text_content = f"""
STUDIOCENTOS - Software House Salerno

Ciao da {request.target_region}!

Sono Ciro di StudioCentOS, software house specializzata in:

- AI Integration (Chatbot, RAG, Automation)
- Sviluppo Software (React, FastAPI, Enterprise)
- App Mobile (iOS e Android)
- Web Development (Siti e webapp)

Trasformiamo la tua idea in prodotto digitale in 45 giorni.

Specializzazione {request.target_industry}: Soluzioni su misura per il tuo settore.

PRENOTA CONSULENZA GRATUITA 30MIN:
https://studiocentos.it#prenota

Made in {request.target_region} 🇮🇹
Rispondo entro 24h

---
StudioCentOS
Salerno, Campania
info@studiocentos.it
https://studiocentos.it
"""

        return GenerateEmailResponse(
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            ai_model=model_slug
        )

    # ========================================================================
    # EMAIL CAMPAIGN
    # ========================================================================

    @staticmethod
    def create_campaign(
        db: Session,
        data: EmailCampaignCreate
    ) -> EmailCampaignResponse:
        """Crea nuova campagna email."""

        insert_query = text("""
            INSERT INTO email_campaigns (
                name, subject,
                html_content, text_content,
                target_region, target_industry, target_tags,
                scheduled_date,
                is_active, is_sent,
                ai_generated, ai_model,
                created_at, updated_at
            ) VALUES (
                :name, :subject,
                :html_content, :text_content,
                :target_region, :target_industry, :target_tags,
                :scheduled_date,
                true, false,
                :ai_generated, :ai_model,
                NOW(), NOW()
            ) RETURNING id
        """)

        result = db.execute(insert_query, {
            "name": data.name,
            "subject": data.subject,
            "html_content": data.html_content,
            "text_content": data.text_content,
            "target_region": data.target_region,
            "target_industry": data.target_industry,
            "target_tags": json.dumps(data.target_tags),
            "scheduled_date": data.scheduled_date,
            "ai_generated": data.ai_generated,
            "ai_model": data.ai_model
        })

        campaign_id = result.scalar()
        db.commit()

        # Return created campaign
        query = text("SELECT * FROM email_campaigns WHERE id = :id")
        row = db.execute(query, {"id": campaign_id}).fetchone()

        return EmailCampaignResponse(
            id=row[0],
            name=row[1],
            subject=row[2],
            html_content=row[3],
            text_content=row[4],
            target_region=row[5],
            target_industry=row[6],
            target_tags=row[7] or [],
            scheduled_date=row[8],
            sent_date=row[9],
            is_active=row[10],
            is_sent=row[11],
            total_sent=row[12],
            total_opened=row[13],
            total_clicked=row[14],
            total_replied=row[15],
            ai_generated=row[16],
            ai_model=row[17],
            created_at=row[18],
            updated_at=row[19]
        )
