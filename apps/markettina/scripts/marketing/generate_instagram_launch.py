#!/usr/bin/env python3
"""
Generate Instagram Launch Content - Prima Settimana

Genera i primi 7 post professionali per il lancio del profilo Instagram @markettina.
Usa il Marketing Batch Generator con topic personalizzati per ogni giorno.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import List, Dict

# ============================================================================
# CONFIGURATION
# ============================================================================

AI_SERVICE_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:8002"
API_KEY = "dev-api-key-change-in-production"

# ============================================================================
# LANCIO CONTENT - 7 GIORNI
# ============================================================================

LAUNCH_CONTENT = [
    {
        "day": 1,
        "topic": """POST DI LANCIO - Presentazione markettina

OBIETTIVO: Far capire CHI SIAMO e COSA FACCIAMO

TONE: Friendly, professionale ma accessibile, Made in Italy pride

KEY POINTS:
- Non siamo la solita software house
- Team developer, AI specialist, designer senior
- Trasformiamo PMI italiane con tech enterprise
- Made in Italy 100%
- React 19, FastAPI, AI Integration
- Da idea a produzione in 45 giorni

SERVIZI HIGHLIGHT:
- Assistenti Virtuali AI 24/7
- Dashboard Business Intelligence
- E-commerce su misura
- Automazione processi

TARGET AUDIENCE: CEO/Founder PMI, Marketing Manager, Imprenditori digitali

CTA: "Segui per dietro le quinte, novità AI e tips digitalizzazione. Link in bio per consulenza gratuita."

HASHTAGS: #SoftwareHouse #AIItalia #DigitalTransformation #MadeinItaly #TechItalia #PMI #Innovation

STILE VISUALE: Team photo o workspace con laptop, codice sullo schermo, atmosfera moderna""",
        "content_type": "post"
    },
    {
        "day": 2,
        "topic": """POST SERVIZI - Cosa Offriamo

OBIETTIVO: Mostrare VALORE e RISULTATI CONCRETI

TONE: Value-focused, concrete, risultati misurabili

SERVIZI DA MOSTRARE (carousel 4 slide):

1. ASSISTENTI AI 24/7
- Rispondono clienti H24 italiano/inglese
- WhatsApp, sito, Telegram integrati
- Risultato: -70% carico operatori

2. DASHBOARD INTELLIGENTI
- KPI in tempo reale
- Report automatici settimanali
- Alert su anomalie
- Risultato: Decisioni data-driven immediate

3. E-COMMERCE ENTERPRISE
- Catalogo illimitato
- Pagamenti integrati Stripe/PayPal
- Fatturazione elettronica
- Risultato: Live in 30 giorni, +300% conversioni

4. AUTOMAZIONE PROCESSI
- Email automatiche
- Workflow personalizzati
- Integrazione CRM/ERP
- Risultato: Risparmio 20 ore/settimana

PREZZI: Da €3,000 | Pagamenti dilazionati disponibili

CTA: "DM per preventivo personalizzato o prenota consulenza gratuita → link in bio"

HASHTAGS: #WebDevelopment #AIBusiness #Ecommerce #BusinessAutomation #DigitalServices

STILE VISUALE: Carousel con screenshot servizi, grafici risultati, icone moderne""",
        "content_type": "carousel"
    },
    {
        "day": 3,
        "topic": """POST TECH STACK - Cosa Usiamo

OBIETTIVO: Mostrare COMPETENZA TECNICA e differenziarci da competitor

TONE: Tech-savvy ma comprensibile, passionate about technology

KEY MESSAGE: "Non usiamo WordPress. Usiamo ciò che usano Netflix, Uber, Spotify."

TECH STACK DA MOSTRARE:

FRONTEND 🎨
- React 19 (ultima versione, server components)
- TypeScript (zero errori runtime)
- Vite (build 10x più veloce)

BACKEND 🔧
- FastAPI (performance 10x superiori a Flask)
- PostgreSQL 16 (database enterprise-grade)
- Redis 7 (cache millisecondo)

AI & ML 🤖
- Google Gemini Pro (4K images, thinking mode)
- OpenAI GPT-4 (reasoning avanzato)
- Fine-tuning custom models

INFRASTRUCTURE 🏗️
- Docker (deploy in minuti)
- Nginx (performance ottimali)
- SSL/TLS (sicurezza massima)

RISULTATI:
✅ App 3x più veloci
✅ 99.9% uptime garantito
✅ Scalabilità illimitata
✅ Sicurezza enterprise

CTA: "Commenta 'TECH' per un'analisi gratuita del tuo stack attuale"

HASHTAGS: #React #FastAPI #WebDevelopment #TechStack #EnterpriseIT #PostgreSQL #Docker

STILE VISUALE: Infografica stack con loghi tecnologie, diagramma architettura moderna""",
        "content_type": "post"
    },
    {
        "day": 4,
        "topic": """CASE STUDY - E-commerce +350% Conversioni

OBIETTIVO: Mostrare RISULTATI REALI e ROI

TONE: Data-driven, concrete numbers, success story

PROBLEMA DEL CLIENTE:
- E-commerce vecchio su WordPress/WooCommerce
- Lento (5+ secondi caricamento)
- Carrello abbandonato: 78%
- Mobile experience pessima
- Perdeva vendite ogni giorno

SOLUZIONE markettina:
✅ Redesign completo con React 19
✅ Checkout ottimizzato 1-click
✅ AI product recommendations
✅ Mobile-first architecture
✅ Loading time <1 secondo

RISULTATI IN 6 MESI:
→ +350% tasso di conversione (2.1% → 7.3%)
→ Abbandono carrello: 78% → 32%
→ Tempo medio checkout: 8 min → 2 min
→ Ordini da mobile: +480%
→ Revenue mensile: +€120,000

TIMELINE: 45 giorni dal brief al launch
INVESTMENT: €12,000
ROI: 10x in 6 mesi (recovered investment + €108k profit)

TECH USATO:
- React 19 + Next.js per SEO
- Stripe per pagamenti
- PostgreSQL per catalogo
- Redis per cache prodotti
- Gemini AI per recommendations

CTA: "Il tuo e-commerce sta perdendo vendite? DM o link in bio per audit gratuito"

HASHTAGS: #Ecommerce #CaseStudy #ROI #DigitalMarketing #ConversionRate #SuccessStory

STILE VISUALE: Before/After screenshots, grafici conversioni, dashboard analytics risultati""",
        "content_type": "post"
    },
    {
        "day": 5,
        "topic": """PROCESSO - Come Lavoriamo (Zero Sorprese)

OBIETTIVO: Rassicurare clienti su TRASPARENZA e PROFESSIONALITÀ

TONE: Clear, transparent, customer-focused

IL NOSTRO PROCESSO IN 5 STEP:

1️⃣ DISCOVERY (1 settimana)
→ Chiamata gratuita 30 minuti
→ Analisi esigenze business
→ Audit tech esistente (se applicabile)
→ Brief dettagliato condiviso

2️⃣ PROPOSTA (3 giorni)
→ Preventivo trasparente (no costi nascosti)
→ Timeline chiara con milestone
→ Deliverable specifici
→ Opzioni pagamento dilazionato

3️⃣ DESIGN (2 settimane)
→ Wireframe low-fi
→ Mockup alta fedeltà
→ Revisioni illimitate in fase design
→ Sign-off prima di sviluppo

4️⃣ SVILUPPO (3-6 settimane)
→ Aggiornamenti settimanali via Slack
→ Demo ogni 2 settimane
→ Test continui (automated + manual)
→ Ambiente staging per review

5️⃣ LAUNCH & SUPPORTO
→ Deploy graduale (no big bang)
→ Monitoring 24/7 primi 30 giorni
→ Supporto tecnico 3 mesi incluso
→ Training team interno

GARANZIA: Se non sei soddisfatto del risultato finale, non paghi. Zero risk.

COSA CI RENDE DIVERSI:
✅ Comunicazione costante (no sparizioni)
✅ Code ownership (documentazione completa)
✅ Testing rigoroso (40%+ coverage)
✅ Scalabilità built-in (pensa in grande)

CTA: "Trasparenza. Qualità. Risultati. Prenota discovery call → link in bio"

HASHTAGS: #WebAgency #ProcessoTrasparente #ClientFirst #SoftwareDevelopment #Transparency

STILE VISUALE: Timeline infografica 5 step, icone processo, screenshot Slack/tools""",
        "content_type": "post"
    },
    {
        "day": 6,
        "topic": """AI SHOWCASE - AI che Funziona (Davvero)

OBIETTIVO: Dimostrare COMPETENZA AI con esempi CONCRETI

TONE: Innovative but practical, no buzzwords, real implementations

KEY MESSAGE: "Tutti parlano di AI. Noi la mettiamo in produzione."

3 AI CHE ABBIAMO COSTRUITO QUESTO MESE:

1️⃣ ASSISTENTE VIRTUALE E-COMMERCE
Problema: Supporto clienti 9-18, weekend chiusi
Soluzione AI:
- Risponde domande prodotti 24/7
- Traccia ordini real-time
- Suggerisce prodotti personalizzati
- Escalation a umano quando necessario
Risultato: -60% ticket supporto, +35% customer satisfaction
Tech: OpenAI GPT-4 + fine-tuning su catalogo prodotti

2️⃣ LEAD QUALIFIER B2B
Problema: Sales team spende 80% tempo su lead freddi
Soluzione AI:
- Analizza comportamento visitatori sito
- Scoring automatico 0-100 (BANT criteria)
- Prioritizza follow-up sales team
- Enrichment automatico da LinkedIn
Risultato: +40% conversion rate, -60% tempo per lead
Tech: Custom ML model + Google Gemini + Clearbit API

3️⃣ CONTENT GENERATOR SOCIAL
Problema: Content marketing richiede 15 ore/settimana
Soluzione AI:
- Genera post Instagram/LinkedIn/Facebook
- Immagini 4K con Gemini Pro
- Video Reels 15s con Veo 3.1
- 8 assets pronti in 6 minuti
Risultato: -93% tempo creazione, +120% output
Tech: Gemini 3 Pro Image + Veo 3.1 + custom prompts

NON È MAGIA. È INGEGNERIA.

AI = Augmented Intelligence
Non sostituisce umani. Potenzia il tuo team.

CTA: "Vuoi vedere cosa può fare l'AI per il tuo business? DM 'AI DEMO' per prova gratuita"

HASHTAGS: #ArtificialIntelligence #AIItalia #Automation #MachineLearning #Innovation #AIBusiness

STILE VISUALE: Screenshot AI in azione, demo video 30s, grafici risultati before/after""",
        "content_type": "post"
    },
    {
        "day": 7,
        "topic": """TEAM - Chi Siamo Davvero

OBIETTIVO: Creare CONNECTION umana e TRUST

TONE: Authentic, personal, passionate, local pride

KEY MESSAGE: "Non siamo una corporate anonima. Siamo un team di appassionati."

IL TEAM markettina:

CIRO AUTUORI - Founder & Tech Lead
→ 850+ file enterprise code scritti (repo pubblico GitHub)
→ Ex developer per clienti Fortune 500 USA
→ Specialista React 19 + FastAPI + AI Integration
→ "Amo risolvere problemi complessi con codice elegante"

[NOTA: Aggiungi altri membri team se presenti]

LA NOSTRA BASE:
📍 Salerno, Campania - 100% Made in Italy 🇮🇹
Remote-first ma incontri in persona quando serve

COSA CI RENDE DIVERSI:

✅ RISPONDIAMO NOI (no call center offshore)
✅ PARLIAMO ITALIANO (no barriere linguistiche)
✅ CODICE NOSTRO (no outsourcing India/Ucraina)
✅ SUPPORTO LOCALE (no ticket dimenticati)
✅ PARTNERSHIP (no "arrivederci e grazie")

CERCHIAMO CLIENTI CHE VOGLIONO:
→ Qualità senza compromessi
→ Tecnologia che scala long-term
→ Partnership collaborative
→ Innovazione continua

NON CERCHIAMO:
→ "Copia sito di competitor X"
→ "Quanto costa logo + sito?"
→ Progetti one-shot senza vision
→ Clienti che scelgono solo su prezzo

IL FIT CULTURALE È IMPORTANTE QUANTO QUELLO TECNICO.

Valori markettina:
🎯 Eccellenza tecnica
🤝 Trasparenza totale
🚀 Innovazione continua
🇮🇹 Pride Made in Italy
💡 Learning mindset

CTA: "Parliamo? Se i nostri valori risuonano con te → link in bio"

HASHTAGS: #Team #MadeInItaly #SoftwareEngineering #Passion #Quality #Campania #Salerno

STILE VISUALE: Team photo genuino (no stock), workspace behind-the-scenes, coding session""",
        "content_type": "post"
    }
]


async def generate_launch_posts():
    """Genera tutti i 7 post di lancio."""
    print("🚀 INSTAGRAM LAUNCH CONTENT GENERATOR")
    print("=" * 60)
    print()

    results = []

    async with aiohttp.ClientSession() as session:
        for day_content in LAUNCH_CONTENT:
            day = day_content["day"]
            topic = day_content["topic"]
            content_type = day_content["content_type"]

            print(f"📝 Giorno {day}: Generazione {content_type}...")

            # Call batch generator (genererà 1 post Instagram 1:1)
            url = f"{AI_SERVICE_URL}/api/v1/marketing/content/batch/generate"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "topic": topic,
                "platforms": ["instagram"],
                "post_count": 1,
                "story_count": 0,  # No stories per ora
                "video_count": 0,  # No video per ora
                "style": "professional",
                "use_pro_quality": True  # 4K quality
            }

            try:
                async with session.post(url, json=payload, headers=headers, timeout=300) as resp:
                    if resp.status == 200:
                        result = await resp.json()

                        if result.get("items"):
                            post = result["items"][0]

                            print(f"✅ Giorno {day} generato!")
                            print(f"   Caption: {post['caption'][:100]}...")
                            print(f"   Image: {post['image_url']}")
                            print(f"   Hashtags: {', '.join(post['hashtags'][:5])}...")
                            print()

                            results.append({
                                "day": day,
                                "content_type": content_type,
                                "caption": post["caption"],
                                "image_url": post["image_url"],
                                "hashtags": post["hashtags"],
                                "aspect_ratio": post["aspect_ratio"],
                                "topic": topic[:100]
                            })
                        else:
                            print(f"⚠️ Giorno {day}: Nessun contenuto generato")
                    else:
                        error = await resp.text()
                        print(f"❌ Giorno {day} errore: {resp.status}")
                        print(f"   {error[:200]}")

            except asyncio.TimeoutError:
                print(f"⏱️ Giorno {day}: Timeout (generazione troppo lenta)")
            except Exception as e:
                print(f"❌ Giorno {day} errore: {e}")

            # Pausa tra generazioni per evitare rate limiting
            await asyncio.sleep(2)

    # Save results to JSON
    output_file = f"instagram_launch_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print(f"✅ COMPLETATO! {len(results)}/7 post generati")
    print(f"📄 Risultati salvati in: {output_file}")
    print()
    print("NEXT STEPS:")
    print("1. Review post nel file JSON")
    print("2. Edita caption se necessario")
    print("3. Schedule posting su Instagram (18:00 ogni giorno)")
    print("4. Pubblica Giorno 1 oggi!")
    print()
    print("POSTING SCHEDULE SUGGERITO:")

    start_date = datetime.now()
    for i in range(7):
        post_date = start_date + timedelta(days=i)
        print(f"   Giorno {i+1}: {post_date.strftime('%d/%m/%Y')} ore 18:00")

    return results


if __name__ == "__main__":
    asyncio.run(generate_launch_posts())
