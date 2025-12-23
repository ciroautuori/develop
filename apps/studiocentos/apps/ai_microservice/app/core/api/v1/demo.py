"""
Demo AI Endpoint - Pubblico per test
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import aiohttp
import asyncio
import os
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

class DemoRequest(BaseModel):
    question: str
    provider: str = "groq"

class DemoResponse(BaseModel):
    answer: str
    provider: str
    confidence: int
    processing_time: int

@router.post("/demo/ask", response_model=DemoResponse)
async def demo_ask(request: DemoRequest):
    """Demo AI endpoint - pubblico per test"""
    try:
        logger.info("demo_ask", question=request.question[:50], provider=request.provider)

        # Context StudioCentOS
        context = """Sei un assistente AI per StudioCentOS, software house di Salerno specializzata in:
        - Sviluppo web con React 19 + FastAPI
        - App mobile con React Native
        - Soluzioni AI enterprise
        - E-commerce e siti web
        - Servizi per aziende in Campania

        Clienti target: PMI, startup, aziende in Salerno e Campania
        Settori: tecnologia, e-commerce, servizi, manifatturiero
        """

        if request.provider == "gemini":
            return await _gemini_demo(request.question, context)
        elif request.provider == "groq":
            return await _groq_demo(request.question, context)
        elif request.provider == "demo":
            return await _demo_fallback(request.question, context)
        else:
            raise HTTPException(400, "Provider non supportato per demo")

    except Exception as e:
        logger.error("demo_error", error=str(e))
        raise HTTPException(500, f"Errore AI: {str(e)}")

async def _gemini_demo(question: str, context: str):
    """Test con Google Gemini"""
    import time
    start_time = time.time()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(500, "Google API Key non configurata")

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

    prompt = f"{context}\n\nDomanda: {question}\n\nRispondi in italiano, professionale e specifico per StudioCentOS:"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300,
            "topP": 0.8,
        },
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status == 200:
                data = await response.json()

                if "candidates" in data and len(data["candidates"]) > 0:
                    ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
                    processing_time = int((time.time() - start_time) * 1000)

                    return DemoResponse(
                        answer=ai_response.strip(),
                        provider="gemini",
                        confidence=85,
                        processing_time=processing_time
                    )

            error_text = await response.text()
            raise HTTPException(500, f"Gemini API error: {response.status} - {error_text}")

async def _groq_demo(question: str, context: str):
    """Test con GROQ"""
    import time
    start_time = time.time()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(500, "GROQ API Key non configurata")

    api_url = "https://api.groq.com/openai/v1/chat/completions"

    prompt = f"{context}\n\nDomanda: {question}\n\nRispondi in italiano, professionale e specifico per StudioCentOS:"

    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": question}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
        "top_p": 0.9
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status == 200:
                data = await response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    ai_response = data["choices"][0]["message"]["content"]
                    processing_time = int((time.time() - start_time) * 1000)

                    return DemoResponse(
                        answer=ai_response.strip(),
                        provider="groq",
                        confidence=90,
                        processing_time=processing_time
                    )

            error_text = await response.text()
            raise HTTPException(500, f"GROQ API error: {response.status} - {error_text}")

async def _demo_fallback(question: str, context: str):
    """Demo fallback con risposte intelligenti"""
    import time
    start_time = time.time()

    # Simula processing time realistico
    await asyncio.sleep(0.5)

    # Risposte intelligenti basate su keywords
    question_lower = question.lower()

    if "servizi" in question_lower or "offre" in question_lower:
        answer = """StudioCentOS offre servizi completi per aziende in Campania:

🚀 **Sviluppo Web Enterprise**
- React 19 + FastAPI + PostgreSQL 16
- Architettura scalabile e production-ready
- 850+ file di codice enterprise

📱 **App Mobile Native**
- iOS e Android con React Native
- Offline-first e push notifications
- Integrazione backend completa

🤖 **Soluzioni AI**
- Chatbot intelligenti
- Automazione processi
- Analisi dati avanzata

💼 **Per PMI in Salerno e Campania**
- Time to market: 45 giorni
- Supporto completo post-lancio
- Made in Italy 🇮🇹"""

    elif "prezzo" in question_lower or "costo" in question_lower:
        answer = """I nostri prezzi sono competitivi e trasparenti:

💰 **Sviluppo Web**: Da €5.000 a €25.000
📱 **App Mobile**: Da €8.000 a €30.000
🤖 **Soluzioni AI**: Da €3.000 a €15.000

✅ **Incluso sempre**:
- Analisi e progettazione
- Sviluppo completo
- Testing e deployment
- 3 mesi supporto gratuito

📞 **Contattaci per preventivo personalizzato**
Ogni progetto è unico, analizziamo le tue esigenze specifiche."""

    elif "tempo" in question_lower or "quanto" in question_lower:
        answer = """Tempi di sviluppo StudioCentOS:

⚡ **MVP**: 15-30 giorni
🚀 **Prodotto completo**: 45-90 giorni
📱 **App mobile**: 60-120 giorni

🎯 **Metodologia Agile**:
- Sprint settimanali
- Demo ogni 2 settimane
- Feedback continuo
- Consegna incrementale

✅ **Garanzia rispetto tempi**
Il 95% dei nostri progetti viene consegnato in anticipo o nei tempi previsti."""

    else:
        answer = f"""Grazie per la domanda: "{question}"

StudioCentOS è la software house di riferimento per Salerno e Campania. Specializziamo in:

🎯 **Sviluppo Enterprise**: React 19, FastAPI, PostgreSQL
📱 **App Mobile**: React Native per iOS/Android
🤖 **AI Integration**: Chatbot e automazione
💼 **E-commerce**: Soluzioni complete

**Perché scegliere StudioCentOS?**
✅ 850+ file di codice production-ready
✅ Time to market: 45 giorni
✅ Supporto locale in Campania
✅ Made in Italy 🇮🇹

Vuoi saperne di più su un servizio specifico?"""

    processing_time = int((time.time() - start_time) * 1000)

    return DemoResponse(
        answer=answer,
        provider="demo",
        confidence=95,
        processing_time=processing_time
    )
