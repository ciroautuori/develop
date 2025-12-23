from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.models import RecipeModel, UserModel
from src.interfaces.api.schemas.recipes import RecipeCreate, RecipeResponse, RecipeUpdate
from src.infrastructure.security.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe_in: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Create a new recipe for the current user.
    """
    # Calculate totals from ingredients
    total_calories = sum(i.calories for i in recipe_in.ingredients)
    total_protein = sum(i.protein for i in recipe_in.ingredients)
    total_carbs = sum(i.carbs for i in recipe_in.ingredients)
    total_fat = sum(i.fat for i in recipe_in.ingredients)

    # Convert Pydantic models to dicts for JSON storage
    # Pydantic v2: model_dump()
    ingredients_data = [i.model_dump() for i in recipe_in.ingredients]

    db_recipe = RecipeModel(
        user_id=current_user.id,
        name=recipe_in.name,
        description=recipe_in.description,
        ingredients=ingredients_data,
        total_calories=round(total_calories, 2),
        total_protein=round(total_protein, 2),
        total_carbs=round(total_carbs, 2),
        total_fat=round(total_fat, 2),
        servings=recipe_in.servings,
        prep_time_minutes=recipe_in.prep_time_minutes,
        instructions=recipe_in.instructions,
    )
    
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.get("/", response_model=List[RecipeResponse])
def get_recipes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get all recipes created by the current user.
    """
    recipes = (
        db.query(RecipeModel)
        .filter(RecipeModel.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return recipes


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get a specific recipe by ID.
    """
    recipe = (
        db.query(RecipeModel)
        .filter(RecipeModel.id == recipe_id, RecipeModel.user_id == current_user.id)
        .first()
    )
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
        )
    return recipe


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: str,
    recipe_in: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update a recipe. Recalculates macros if ingredients change.
    """
    recipe = (
        db.query(RecipeModel)
        .filter(RecipeModel.id == recipe_id, RecipeModel.user_id == current_user.id)
        .first()
    )
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
        )

    update_data = recipe_in.model_dump(exclude_unset=True)
    
    # If ingredients are updated, recalculate totals
    if "ingredients" in update_data and update_data["ingredients"]:
        # ingredients are passed as list of dicts or objects depending on Pydantic handling
        # Since we use model_dump above, they might be dicts. 
        # But wait, recipe_in.ingredients is a list of Ingredient (Pydantic models).
        # We need to access them carefully.
        
        # Re-access source object for calculation
        new_ingredients = recipe_in.ingredients
        
        total_calories = sum(i.calories for i in new_ingredients)
        total_protein = sum(i.protein for i in new_ingredients)
        total_carbs = sum(i.carbs for i in new_ingredients)
        total_fat = sum(i.fat for i in new_ingredients)
        
        update_data["total_calories"] = round(total_calories, 2)
        update_data["total_protein"] = round(total_protein, 2)
        update_data["total_carbs"] = round(total_carbs, 2)
        update_data["total_fat"] = round(total_fat, 2)
        update_data["ingredients"] = [i.model_dump() for i in new_ingredients]

    for field, value in update_data.items():
        setattr(recipe, field, value)

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Delete a recipe.
    """
    recipe = (
        db.query(RecipeModel)
        .filter(RecipeModel.id == recipe_id, RecipeModel.user_id == current_user.id)
        .first()
    )
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
        )

    db.delete(recipe)
    db.commit()
    return None
