"""
Smart Nutrition Tools - SOLO FatSecret API + Linee Guida RAG.

Workflow (MARKET-READY):
1. Ricerca alimenti: ESCLUSIVAMENTE FatSecret API (dati ufficiali, nessun RAG)
2. Linee guida nutrizionali: RAG locale (nutrition_guidelines_complete.md)
3. Preferenze utente: dal contesto utente
4. Tracking pasti: salvataggio diario alimentare
"""
from typing import List, Dict, Any, Optional
from datetime import date
from langchain_core.tools import Tool, StructuredTool, BaseTool
from pydantic import BaseModel, Field

from src.infrastructure.ai.rag_service import get_rag_service
from src.infrastructure.external.fatsecret_service import fatsecret_service
from src.infrastructure.logging import get_logger
from src.domain.entities.nutrition import DailyNutritionLog, Meal, FoodItem
from src.domain.repositories.nutrition_repository import INutritionRepository

logger = get_logger(__name__)


class FoodSearchInput(BaseModel):
    """Input per ricerca alimenti."""
    query: str = Field(description="Nome alimento da cercare (es. 'pollo', 'pasta integrale')")
    include_api: bool = Field(default=False, description="Se True, cerca anche su API esterne")


class RecipeSearchInput(BaseModel):
    """Input per ricerca ricette - DEPRECATO: usiamo FatSecret per tutto."""
    goal: str = Field(description="Obiettivo (es. 'massa muscolare', 'dimagrimento', 'recupero')")
    meal_type: str = Field(default="any", description="Tipo pasto: 'colazione', 'pranzo', 'cena', 'snack', 'any'")
    diet_restrictions: List[str] = Field(default=[], description="Restrizioni alimentari (es. 'vegetariano', 'senza lattosio')")


class TrackMealInput(BaseModel):
    """Input per tracciamento pasto."""
    food_name: str = Field(description="Nome del cibo (es. 'pollo', 'mela')")
    quantity: float = Field(description="Quantità in grammi")
    meal_type: str = Field(default="snack", description="Tipo pasto (colazione, pranzo, cena, snack)")


def create_smart_food_search_tool() -> Tool:
    """
    Tool per ricerca alimenti ESCLUSIVAMENTE tramite FatSecret API.

    NO RAG, NO database locale - SOLO API esterna per dati affidabili.
    """

    def search_food_smart(query: str, include_api: bool = True) -> str:
        """Cerca alimenti usando ESCLUSIVAMENTE FatSecret API."""

        try:
            # Ricerca diretta su FatSecret
            api_foods = fatsecret_service.search_foods(query, page=0, limit=5)

            if not api_foods:
                return f"Nessun risultato trovato per '{query}'."

            results = [f"🌐 **RISULTATI DA FATSECRET API per '{query}':**\n"]

            for food in api_foods:
                brand = f" ({food.get('brand')})" if food.get('brand') else ""
                results.append(
                    f"- **{food['name']}**{brand}\n"
                    f"  {food['calories']} kcal | P: {food['protein']}g | C: {food['carbs']}g | F: {food['fat']}g\n"
                    f"  Descrizione: {food.get('description', 'N/A')}\n"
                )

            return "\n".join(results)

        except Exception as e:
            logger.error(f"FatSecret API error: {e}")
            return f"Errore durante la ricerca su FatSecret: {str(e)}"

    return Tool(
        name="food_search",
        func=lambda q: search_food_smart(q, include_api=False),
        description="""Cerca valori nutrizionali di un alimento tramite FatSecret API.
Output: calorie e macro per l'alimento specifico."""
    )


# NOTA: create_recipe_search_tool RIMOSSA
# Le ricette non sono più nel RAG. Per suggerire pasti, usa le linee guida nutrizionali
# e combina con gli alimenti FatSecret trovati.


def create_user_preferences_tool(user_id: str = None) -> Tool:
    """
    Tool per recuperare preferenze alimentari dell'utente.
    """

    def get_preferences(query: str = "") -> str:
        """Recupera preferenze utente dal contesto."""

        if not user_id:
            return "Nessun profilo utente disponibile."

        try:
            from src.infrastructure.ai.user_context_rag import get_user_context_rag
            user_rag = get_user_context_rag()

            prefs = user_rag.retrieve_context(
                user_id=user_id,
                query="preferenze alimentari cibi preferiti evitare allergie dieta",
                categories=["preference", "medical", "goal"],
                k=5
            )

            if not prefs:
                return "Nessuna preferenza alimentare salvata per questo utente."

            output = "📋 **PREFERENZE UTENTE:**\n"
            for p in prefs:
                output += f"- {p['content'][:100]}...\n"

            return output

        except Exception as e:
            logger.warning(f"User preferences error: {e}")
            return "Impossibile recuperare preferenze utente."

    return Tool(
        name="user_preferences",
        func=get_preferences,
        description="""Recupera le preferenze alimentari dell'utente.
Usa questo tool per conoscere: cibi preferiti, cibi da evitare, allergie, obiettivi nutrizionali."""
    )


def create_meal_plan_context_tool() -> Tool:
    """
    Tool per ottenere contesto per pianificazione pasti con Cross-Reference.
    """

    def get_meal_context(goal: str, context: str = "") -> str:
        """Ottieni linee guida nutrizionali per obiettivo e contesto allenamento."""

        rag = get_rag_service()

        # Cross-reference: Modifica query in base all'allenamento
        context_modifier = ""
        if "leg" in context.lower() or "gambe" in context.lower():
             context_modifier = "post workout gambe carboidrati alti recupero"
        elif "hiit" in context.lower() or "cardio" in context.lower():
             context_modifier = "post cardio idratazione elettroliti"
        elif "rest" in context.lower() or "riposo" in context.lower():
             context_modifier = "giorno riposo carboidrati bassi proteine"

        # Mappa obiettivi a query
        goal_queries = {
            "massa": "ipertrofia muscolare bulk surplus calorico proteine alte",
            "dimagrimento": "deficit calorico cutting perdita grasso proteine",
            "mantenimento": "mantenimento peso equilibrio macronutrienti",
            "recupero": "recupero infortunio anti-infiammatorio omega-3 vitamina C",
            "performance": "energia pre-workout carboidrati performance sportiva"
        }

        base_query = goal_queries.get(goal.lower(), f"nutrizione sportiva {goal}")
        final_query = f"{base_query} {context_modifier}"

        try:
            results = rag.retrieve_context(
                query=final_query,
                k=3,
                filter_metadata={"category": "nutrition"}
            )

            if not results:
                return f"Linee guida standard per {goal}: bilancia i macronutrienti secondo i tuoi obiettivi."

            output = f"📚 **LINEE GUIDA NUTRIZIONALI per {goal.upper()} ({context if context else 'Generale'}):**\n\n"
            for r in results:
                content = r['content'][:300]
                output += f"• {content}...\n\n"

            return output

        except Exception as e:
            logger.error(f"Meal context error: {e}")
            return "Usa le linee guida standard per la nutrizione sportiva."

    return Tool(
        name="nutrition_guidelines",
        func=lambda q: get_meal_context(q), # Semplificazione per LangChain
        description="""Ottieni linee guida nutrizionali per un obiettivo specifico.
Input: obiettivo (es. 'massa', 'dimagrimento'). Può includere contesto allenamento (es. 'massa post leg day').
Output: raccomandazioni nutrizionali dal knowledge base."""
    )


def create_meal_tracking_tool(user_id: str, nutrition_repo: INutritionRepository) -> Tool:
    """
    Tool per tracciare i pasti dell'utente.
    """

    def track_meal(food_name: str, quantity: float, meal_type: str = "snack") -> str:
        """Registra un pasto nel diario."""

        if not user_id or not nutrition_repo:
            return "Impossibile tracciare: utente non identificato."

        try:
            # 1. Cerca valori nutrizionali (FatSecret diretto)
            try:
                api_foods = fatsecret_service.search_foods(food_name, page=0, limit=1)

                calories = 0
                protein = 0
                carbs = 0
                fat = 0

                if api_foods:
                     f = api_foods[0]
                     # FatSecret ritorna già valori float/int
                     calories = float(f['calories'])
                     protein = float(f['protein'])
                     carbs = float(f['carbs'])
                     fat = float(f['fat'])
                else:
                    return f"Non ho trovato informazioni nutrizionali per '{food_name}'. Specifica meglio o inserisci i macro se li conosci."

            except Exception as e:
                logger.error(f"FatSecret lookup failed: {e}")
                return "Errore nel recupero dati nutrizionali."

            # Calcola totali per quantità
            factor = quantity / 100.0
            tot_cal = calories * factor
            tot_prot = protein * factor
            tot_carb = carbs * factor
            tot_fat = fat * factor

            # Crea oggetti dominio
            food_item = FoodItem(
                name=food_name,
                quantity=quantity,
                unit="g",
                calories=tot_cal,
                protein=tot_prot,
                carbs=tot_carb,
                fat=tot_fat
            )

            new_meal = Meal(name=meal_type, foods=[food_item], time=None)

            # Recupera o crea log giornaliero
            today = date.today()
            log = nutrition_repo.get_log_by_date(user_id, today)

            if not log:
                log = DailyNutritionLog(user_id=user_id, date=today, meals=[])

            log.meals.append(new_meal)
            nutrition_repo.save_log(log)

            return f"✅ Tracciato: {quantity}g di {food_name} ({tot_cal:.0f} kcal, P:{tot_prot:.1f}g) in {meal_type}."

        except Exception as e:
            logger.error(f"Tracking error: {e}")
            return f"Errore durante il tracciamento: {e}"

    return StructuredTool.from_function(
        func=track_meal,
        name="track_meal",
        description="Registra un pasto nel diario alimentare. Input: nome cibo, quantità (g), tipo pasto.",
        args_schema=TrackMealInput
    )


def create_smart_nutrition_tools(user_id: str = None, nutrition_repo: INutritionRepository = None) -> List[Tool]:
    """
    Crea set completo di tools nutrizionali intelligenti.

    Integra (MARKET-READY):
    - FatSecret API ESCLUSIVAMENTE per ricerca alimenti
    - RAG locale solo per linee guida nutrizionali
    - Preferenze utente
    - Tracking pasti
    """

    tools = [
        create_smart_food_search_tool(),
        create_meal_plan_context_tool(),
    ]

    if user_id:
        tools.append(create_user_preferences_tool(user_id))

        if nutrition_repo:
            tools.append(create_meal_tracking_tool(user_id, nutrition_repo))

    return tools
