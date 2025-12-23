"""Debug & Error Analysis API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from app.core.security import verify_api_key
from app.core.logging import get_logger
from app.domain.debug.service import DebugService

logger = get_logger(__name__)
router = APIRouter(dependencies=[Depends(verify_api_key)])

# Initialize debug service
debug_service = DebugService()

class DebugRequest(BaseModel):
    error_type: str
    stack_trace: str
    language: str = "python"
    context: Optional[dict] = None

class Solution(BaseModel):
    title: str
    description: str
    confidence: int

class DebugResponse(BaseModel):
    diagnosis: dict
    solutions: List[Solution]
    severity: str

@router.post("/analyze", response_model=DebugResponse)
async def analyze_error(request: DebugRequest):
    """
    Analyze error and provide solutions using Auto-Debug Agent (DDD Architecture)
    
    - **error_type**: Type of error (runtime, syntax, type, etc.)
    - **stack_trace**: Full stack trace
    - **language**: Programming language (python, javascript, typescript)
    - **context**: Additional context (file, line, environment)
    """
    try:
        logger.info("debug_analyze", error_type=request.error_type, language=request.language)
        
        # Call debug service with full DDD implementation
        result = await debug_service.analyze_error(
            error_type=request.error_type,
            stack_trace=request.stack_trace,
            language=request.language,
            context=request.context
        )
        
        return DebugResponse(**result)
        
    except Exception as e:
        logger.error("analyze_error_endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Debug analysis failed: {str(e)}")

@router.post("/scan-hardcoded")
async def scan_hardcoded_text(directory: str = "src"):
    """
    Scan codebase for hardcoded text that needs translation
    
    - **directory**: Directory to scan (default: "src")
    
    Returns list of files with hardcoded text issues
    """
    try:
        results = await debug_service.scan_hardcoded_text(directory)
        return results
    except Exception as e:
        logger.error("scan_hardcoded_endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-translations")
async def analyze_translations(file_path: str):
    """
    Analyze file for translation issues
    
    - **file_path**: Path to file to analyze
    
    Returns analysis with wrong prefixes, hardcoded text, etc.
    """
    try:
        results = await debug_service.analyze_translations(file_path)
        return results
    except Exception as e:
        logger.error("analyze_translations_endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fix-translations")
async def fix_translations(file_path: str, dry_run: bool = True):
    """
    Fix translation issues in file
    
    - **file_path**: Path to file to fix
    - **dry_run**: If True, only analyze without making changes (default: True)
    
    Returns fix results with changes made (or would be made in dry-run)
    """
    try:
        results = await debug_service.fix_translations(file_path, dry_run)
        return results
    except Exception as e:
        logger.error("fix_translations_endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def debug_root():
    """Debug service root - includes health check"""
    health = await debug_service.health_check()
    return {
        "service": "debug",
        "status": "available",
        "health": health,
        "endpoints": [
            "/analyze - POST - Analyze error and get solutions",
            "/scan-hardcoded - POST - Scan for hardcoded text",
            "/analyze-translations - POST - Analyze translation issues",
            "/fix-translations - POST - Fix translation issues"
        ]
    }
