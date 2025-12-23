"""
AI Parsing Service

Parses unstructured AI text outputs into structured data.
"""
import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AIParsingService:
    """Service to parse AI generated content."""

    @staticmethod
    def parse_exercises_from_text(text: str) -> List[Dict]:
        """
        Parse AI-generated program text into structured exercises.
        
        Supported formats:
        - "3x10 Squat"
        - "Squat: 3 sets x 10 reps"
        - "- Squat - 3x10"
        """
        exercises = []
        
        # Regex patterns for common exercise formats
        patterns = [
            r'(\d+)\s*[xX]\s*(\d+)\s+([A-Za-z\s]+)',  # 3x10 Squat
            r'([A-Za-z\s]+):\s*(\d+)\s*(?:sets?|serie)\s*[xX]?\s*(\d+)',  # Squat: 3 sets x 10
            r'[-•]\s*([A-Za-z\s]+)\s*[-–]\s*(\d+)\s*[xX]\s*(\d+)',  # - Squat - 3x10
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    if len(match) < 3:
                        continue
                        
                    # Normalize based on pattern position
                    if pattern == patterns[0]:
                        sets, reps, name = int(match[0]), int(match[1]), match[2].strip()
                    elif pattern == patterns[1]:
                        name, sets, reps = match[0].strip(), int(match[1]), int(match[2])
                    else:
                        name, sets, reps = match[0].strip(), int(match[1]), int(match[2])
                    
                    if name and len(name) > 2:
                        exercises.append({
                            "name": name.title(),
                            "sets": sets,
                            "reps": str(reps),
                            "rest_seconds": 90,
                            "notes": "",
                            "coaching_cues": [],
                            "completed": False
                        })
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse match {match}: {e}")
                    continue
                    
        return exercises
