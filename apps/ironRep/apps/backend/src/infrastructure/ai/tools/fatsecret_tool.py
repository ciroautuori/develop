import httpx
import base64
import logging
import asyncio
from typing import Dict, Any, Optional, List
from src.infrastructure.config.settings import settings
from .base import BaseTool

logger = logging.getLogger(__name__)

class FatSecretTool(BaseTool):
    """Tool for retrieving verified nutrition data from FatSecret API."""
    
    BASE_URL = "https://platform.fatsecret.com/rest/server.api"
    AUTH_URL = "https://oauth.fatsecret.com/connect/token"
    
    def __init__(self):
        self.client_id = settings.fatsecret_key
        self.client_secret = settings.fatsecret_secret
        self._token = None
        self._token_expiry = 0
    
    @property
    def name(self) -> str:
        return "fatsecret_nutrition"

    @property
    def description(self) -> str:
        return "Useful for finding precise nutritional information (calories, macros) for foods and recipes. Input should be a food name (e.g. 'Apple', 'Pizza Margherita')."

    async def _get_token(self) -> str:
        """Get OAuth 2.0 token (Client Credentials)."""
        if self._token:
            # Simple expiry check (TODO: better expiry handling)
            return self._token
            
        if not self.client_id or not self.client_secret:
            raise ValueError("FatSecret API keys not configured")

        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.AUTH_URL,
                data={"grant_type": "client_credentials", "scope": "basic"},
                headers={"Authorization": f"Basic {b64_auth}"}
            )
            response.raise_for_status()
            data = response.json()
            self._token = data["access_token"]
            return self._token

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for food items."""
        token = await self._get_token()
        
        params = {
            "method": "foods.search.v2",
            "search_expression": query,
            "format": "json",
            "max_results": 5,
            "region": "IT",  # Geo-localized for Italy
            "language": "it"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.BASE_URL,
                params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"FatSecret API Error: {response.text}")
                return []
                
            data = response.json()
            foods = data.get("foods_search", {}).get("food", [])
            
            # Normalize list/dict return from API
            if isinstance(foods, dict):
                foods = [foods]
                
            return foods

    async def get_details(self, food_id: str) -> Dict[str, Any]:
        """Get detailed nutrition for a specific food."""
        token = await self._get_token()
        
        params = {
            "method": "food.get.v4",
            "food_id": food_id,
            "format": "json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.BASE_URL,
                params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
            data = response.json()
            return data.get("food", {})

    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute tool: Search and return details of top result.
        Returns formatted string or dict for AI context.
        """
        try:
            logger.info(f"FatSecret searching for: {query}")
            foods = await self.search(query)
            
            if not foods:
                return {"error": f"No foods found for '{query}'"}
                
            # Get details for top result to be precise
            top_food = foods[0]
            details = await self.get_details(top_food["food_id"])
            
            # Parse servings to find meaningful one (e.g. 100g or 1 portion)
            servings = details.get("servings", {}).get("serving", [])
            if isinstance(servings, dict):
                servings = [servings]
                
            # Prefer 100g or first serving
            selected_serving = next((s for s in servings if "100g" in s.get("serving_description", "")), servings[0])
            
            return {
                "food_name": details.get("food_name"),
                "brand": details.get("brand_name", "Generic"),
                "calories": selected_serving.get("calories"),
                "protein": selected_serving.get("protein"),
                "carbs": selected_serving.get("carbohydrate"),
                "fat": selected_serving.get("fat"),
                "unit": selected_serving.get("serving_description"),
                "source": "FatSecret (Verified)"
            }
            
        except Exception as e:
            logger.error(f"FatSecret Tool failed: {e}")
            return {"error": str(e)}
