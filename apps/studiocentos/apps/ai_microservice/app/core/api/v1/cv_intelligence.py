"""CV Intelligence API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from app.core.security import verify_api_key
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(dependencies=[Depends(verify_api_key)])

class SkillExtractionRequest(BaseModel):
    text: str = Field(..., min_length=10)
    user_id: int

class Skill(BaseModel):
    name: str
    level: str
    confidence: float

class SkillsResponse(BaseModel):
    skills: List[Skill]
    total: int

@router.post("/extract-skills", response_model=SkillsResponse)
async def extract_skills(request: SkillExtractionRequest):
    """Extract skills from CV text"""
    try:
        logger.info("extract_skills", text_length=len(request.text))
        # Use Groq Llama 3 for real skill extraction
        from app.core.llm.groq_client import get_groq_client

        client = get_groq_client()

        prompt = f"""
        Analizza il seguente testo di un CV e estrai le competenze tecniche e soft skills.
        Per ogni skill stima il livello (Junior, Mid, Senior) basandoti sul contesto.
        Restituisci SOLO un JSON valido con questa struttura:
        {{
            "skills": [
                {{"name": "Python", "level": "Senior", "confidence": 0.95}},
                ...
            ],
            "total": N
        }}

        TESTO CV:
        {request.text[:4000]}
        """

        result = await client.generate_json(prompt, system_prompt="Sei un esperto HR Technical Recruiter. Rispondi solo in JSON.")

        # Validate and return
        skills_data = result.get("skills", [])
        return SkillsResponse(
            skills=[Skill(**s) for s in skills_data],
            total=len(skills_data)
        )
    except Exception as e:
        logger.error("extract_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def cv_root():
    return {"service": "cv_intelligence", "status": "available"}
