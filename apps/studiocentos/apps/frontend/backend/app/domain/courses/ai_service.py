
import os
import openai
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class CoursesAIService:
    """
    Service for AI-powered operations in Courses domain.
    Handles automatic translation of course content.
    """
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("OPENAI_API_KEY not found. AI translation will be disabled.")

    async def translate_course_content(self, title: str, description: str) -> Dict[str, Dict[str, str]]:
        """
        Translates course title and description into English and Spanish.
        Returns a dictionary suitable for the `translations` JSONB field.
        """
        if not self.api_key:
            return {}

        try:
            prompt = f"""
            You are a professional translator for a tech/AI course platform.
            Translate the following course details from Italian to English and Spanish.
            
            Title: "{title}"
            Description: "{description}"
            
            Return ONLY a valid JSON object with this structure:
            {{
                "en": {{
                    "title": "Translated Title EN",
                    "description": "Translated Description EN"
                }},
                "es": {{
                    "title": "Translated Title ES",
                    "description": "Translated Description ES"
                }}
            }}
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4o",  # Use robust model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            translations = json.loads(content)
            return translations

        except Exception as e:
            logger.error(f"AI Translation failed: {e}")
            return {}

# Singleton
courses_ai_service = CoursesAIService()
