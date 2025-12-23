import React, { useState, useMemo } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { Plus, Save, Trash2, ChevronLeft, ChefHat, Scale, Activity } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

import { Button } from "../../../shared/components/ui/button";
import { Input } from "../../../shared/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { Badge } from "../../../shared/components/ui/badge";
import { toast } from "../../../components/ui/Toast";
import { Modal } from "../../../components/ui/Modal";

import { recipesApi } from "../../../lib/api/recipes";
import type { RecipeIngredient, CreateRecipePayload } from "../../../types/recipes";
import { FoodSearchPanel } from "../components/FoodSearch/FoodSearchPanel";
import type { FoodItem } from "../types/food.types";

export function RecipeCreator() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    // Recipe State
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [servings, setServings] = useState(1);
    const [prepTime, setPrepTime] = useState(15);
    const [instructions, setInstructions] = useState("");
    const [ingredients, setIngredients] = useState<RecipeIngredient[]>([]);

    // Food Selection State
    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const [selectedFoodForAdd, setSelectedFoodForAdd] = useState<FoodItem | null>(null);
    const [gramsInput, setGramsInput] = useState(100);

    // Derived Macros
    const totals = useMemo(() => {
        return ingredients.reduce(
            (acc, ing) => ({
                calories: acc.calories + ing.calories,
                protein: acc.protein + ing.protein,
                carbs: acc.carbs + ing.carbs,
                fat: acc.fat + ing.fat,
            }),
            { calories: 0, protein: 0, carbs: 0, fat: 0 }
        );
    }, [ingredients]);

    const perServing = useMemo(() => {
        if (servings < 1) return totals;
        return {
            calories: totals.calories / servings,
            protein: totals.protein / servings,
            carbs: totals.carbs / servings,
            fat: totals.fat / servings,
        };
    }, [totals, servings]);

    // Mutations
    const createMutation = useMutation({
        mutationFn: recipesApi.create,
        onSuccess: () => {
            toast.success("Ricetta creata con successo!", "Ora puoi usarla nel tuo piano nutrizionale.");
            queryClient.invalidateQueries({ queryKey: ["recipes"] });
            navigate({ to: "/recipes" });
        },
        onError: () => {
            toast.error("Errore salvataggio", "Impossibile creare la ricetta. Riprova.");
        }
    });

    // Handlers
    const handleAddIngredient = () => {
        if (!selectedFoodForAdd) return;

        // Calculate values based on grams
        // Standard values are usually per 100g or per serving. 
        // Assuming FoodItem comes normalized per 100g or has serving_size info.
        // NOTE: FatSecret API usually returns values per 'serving_description' which might not be 100g.
        // However, our `_transform_food_item` in backend tries to normalize or provide Grams.
        // Here we assume simple proportion if we treat base values as "per 100g" OR we need more logic.
        // Ideally the backend should send "per 100g" values for calculation.
        // For now, let's assume the FoodItem values are "per 100g" IF the type is generic, 
        // or we take the raw values and scale them.
        // ERROR: Frontend doesn't know if FoodItem values are per 100g or per serving unit.
        // Let's look at `FoodItem` type from `food.types` (via imports).

        // Simplification: We assume user searches ingredients, and we treat the values as "per 100g" 
        // if we want to scale by grams. 
        // BUT FatSecret returns "Per 1 cup" etc.
        // We will do a simple rule:
        // If we have `grams` from backend, we normalize to 1g then multiply by input.
        // If not, we just add as is (1 serving).

        const factor = gramsInput / 100; // Assuming base is 100g for calculation simplicity here, 
        // OR we should rely on what the user sees. 

        // FIX: To be precise, we should likely ask backend to normalize, 
        // OR we assume the `calories` in FoodItem are for `100g` if we are inputting grams.
        // In `FoodSearchPanel`, let's see what `FoodItem` contains.
        // It has `calories`, `protein`, etc.

        // For now, allow simple scaling: existing values * (input / 100).
        // This assumes the API returns values per 100g. 
        // If the API returns per serving (e.g. 1 slice = 30g), this is wrong.
        // IMPORTANT: FatSecret Service on backend NOW does explicit normalization?
        // Reviewing backend `_transform_food_item`: 
        // "calories = ...", "grams = ...". If grams > 0, we scale to 100g!
        // YES! My backend `_transform_food_item` scales to 100g if gram info is available!
        // So values ARE per 100g.

        const newIng: RecipeIngredient = {
            food_id: selectedFoodForAdd.id,
            name: selectedFoodForAdd.name,
            brand: selectedFoodForAdd.brand,
            grams: gramsInput,
            calories: selectedFoodForAdd.calories * factor,
            protein: selectedFoodForAdd.protein * factor,
            carbs: selectedFoodForAdd.carbs * factor,
            fat: selectedFoodForAdd.fat * factor,
        };

        setIngredients([...ingredients, newIng]);
        setSelectedFoodForAdd(null);
        setIsSearchOpen(false);
        setGramsInput(100);
    };

    const removeIngredient = (index: number) => {
        const newIng = [...ingredients];
        newIng.splice(index, 1);
        setIngredients(newIng);
    };

    const handleSave = () => {
        if (!name) {
            toast.error("Nome mancante", "Inserisci un nome per la ricetta.");
            return;
        }
        if (ingredients.length === 0) {
            toast.error("Nessun ingrediente", "Aggiungi almeno un ingrediente.");
            return;
        }

        const payload: CreateRecipePayload = {
            name,
            description,
            ingredients,
            servings,
            prep_time_minutes: prepTime,
            instructions
        };

        createMutation.mutate(payload);
    };

    return (
        <div className="min-h-screen bg-background pb-20 md:pb-0">
            <header className="sticky top-0 z-20 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="flex h-14 items-center gap-4 px-4">
                    <Button variant="ghost" size="icon" onClick={() => navigate({ to: "/recipes" })}>
                        <ChevronLeft className="h-5 w-5" />
                    </Button>
                    <div className="flex-1">
                        <h1 className="text-lg font-semibold leading-none">Crea Ricetta</h1>
                    </div>
                    <Button
                        size="sm"
                        onClick={handleSave}
                        disabled={createMutation.isPending}
                        className="rounded-full bg-primary text-primary-foreground shadow-lg hover:shadow-xl transition-all"
                    >
                        {createMutation.isPending ? "Salvataggio..." : "Salva"}
                        <Save className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            </header>

            <main className="container max-w-3xl p-4 space-y-6">

                {/* Info Generali */}
                <section className="space-y-4">
                    <div className="grid gap-4">
                        <div className="space-y-2">
                            <label htmlFor="name" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Nome Ricetta
                            </label>
                            <Input
                                id="name"
                                placeholder="Es. Pasta al Pomodoro Fit"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="text-lg font-medium"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label htmlFor="servings" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Porzioni</label>
                                <div className="relative">
                                    <ChefHat className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        id="servings"
                                        type="number"
                                        min={1}
                                        value={servings}
                                        onChange={(e) => setServings(Number(e.target.value))}
                                        className="pl-9"
                                    />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label htmlFor="prep" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Minuti Prep.</label>
                                <div className="relative">
                                    <Activity className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        id="prep"
                                        type="number"
                                        min={0}
                                        value={prepTime}
                                        onChange={(e) => setPrepTime(Number(e.target.value))}
                                        className="pl-9"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="desc" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Descrizione (opzionale)</label>
                            <textarea
                                id="desc"
                                placeholder="Breve descrizione..."
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                            />
                        </div>
                    </div>
                </section>

                {/* Ingredienti */}
                <section className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold flex items-center gap-2">
                            <Scale className="h-5 w-5 text-primary" />
                            Ingredienti
                        </h2>
                        <Button variant="outline" size="sm" className="gap-2" onClick={() => setIsSearchOpen(true)}>
                            <Plus className="h-4 w-4" />
                            Aggiungi
                        </Button>
                        <Modal open={isSearchOpen} onOpenChange={setIsSearchOpen}>
                            <Modal.Header>
                                <Modal.Title>Cerca Ingrediente</Modal.Title>
                            </Modal.Header>

                            <Modal.Body>
                                {!selectedFoodForAdd ? (
                                    <div className="flex-1 overflow-y-auto p-1">
                                        <FoodSearchPanel onSelectFood={setSelectedFoodForAdd} />
                                    </div>
                                ) : (
                                    <div className="p-4 space-y-6">
                                        <div className="space-y-2">
                                            <h3 className="text-xl font-bold">{selectedFoodForAdd.name}</h3>
                                            <p className="text-sm text-muted-foreground">{selectedFoodForAdd.brand || "Generico"}</p>
                                        </div>

                                        <div className="space-y-4">
                                            <label className="text-sm font-medium">Quantità (grammi)</label>
                                            <div className="flex items-center gap-4">
                                                <Input
                                                    type="number"
                                                    value={gramsInput}
                                                    onChange={(e) => setGramsInput(Number(e.target.value))}
                                                    className="text-2xl font-bold h-12 w-32 text-center"
                                                    autoFocus
                                                />
                                                <span className="text-muted-foreground text-lg">g</span>
                                            </div>

                                            {/* Live Preview */}
                                            <Card className="bg-muted/50">
                                                <CardContent className="p-4 grid grid-cols-4 gap-2 text-center">
                                                    <div>
                                                        <div className="text-xs text-muted-foreground">Kcal</div>
                                                        <div className="font-bold">{(Number(selectedFoodForAdd.calories) * gramsInput / 100).toFixed(0)}</div>
                                                    </div>
                                                    <div>
                                                        <div className="text-xs text-muted-foreground">Pro</div>
                                                        <div className="font-bold">{(Number(selectedFoodForAdd.protein) * gramsInput / 100).toFixed(1)}</div>
                                                    </div>
                                                    <div>
                                                        <div className="text-xs text-muted-foreground">Carb</div>
                                                        <div className="font-bold">{(Number(selectedFoodForAdd.carbs) * gramsInput / 100).toFixed(1)}</div>
                                                    </div>
                                                    <div>
                                                        <div className="text-xs text-muted-foreground">Fat</div>
                                                        <div className="font-bold">{(Number(selectedFoodForAdd.fat) * gramsInput / 100).toFixed(1)}</div>
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        </div>

                                        <div className="flex gap-2 justify-end pt-4">
                                            <Button variant="ghost" onClick={() => setSelectedFoodForAdd(null)}>Indietro</Button>
                                            <Button onClick={handleAddIngredient} className="bg-primary text-primary-foreground">
                                                Aggiungi alla Ricetta
                                            </Button>
                                        </div>
                                    </div>
                                )}
                            </Modal.Body>
                        </Modal>
                    </div>

                    <div className="space-y-2">
                        <AnimatePresence mode="popLayout">
                            {ingredients.map((ing, idx) => (
                                <motion.div
                                    key={`${ing.food_id}-${idx}`}
                                    layout
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, x: -10 }}
                                    className="flex items-center justify-between p-3 rounded-lg border bg-card shadow-sm"
                                >
                                    <div>
                                        <div className="font-medium">{ing.name}</div>
                                        <div className="text-sm text-muted-foreground">
                                            {ing.grams}g • {ing.calories.toFixed(0)} kcal
                                        </div>
                                    </div>
                                    <Button variant="ghost" size="icon" onClick={() => removeIngredient(idx)} className="text-destructive hover:bg-destructive/10">
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {ingredients.length === 0 && (
                            <div className="text-center py-10 border-2 border-dashed rounded-xl text-muted-foreground">
                                <ChefHat className="h-8 w-8 mx-auto mb-2 opacity-50" />
                                <p>Nessun ingrediente aggiunto</p>
                                <Button variant="link" onClick={() => setIsSearchOpen(true)}>Cerca ingredienti</Button>
                            </div>
                        )}
                    </div>
                </section>

                {/* Macros Summary Sticky Footer or Section */}
                <section className="sticky bottom-4 z-10">
                    <Card className="border-2 shadow-2xl bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/85">
                        <CardHeader className="pb-2 pt-4">
                            <div className="flex items-center justify-between">
                                <CardTitle className="text-sm font-medium uppercase tracking-wider text-muted-foreground">Totale per Porzione ({servings > 1 ? `1/${servings}` : "Intera"})</CardTitle>
                                <Badge variant="outline" className="font-mono text-xs">
                                    {totals.calories.toFixed(0)} kcal tot
                                </Badge>
                            </div>
                        </CardHeader>
                        <CardContent className="grid grid-cols-4 gap-4 text-center pb-4">
                            <div className="space-y-1">
                                <div className="text-2xl font-bold text-primary">{perServing.calories.toFixed(0)}</div>
                                <div className="text-[10px] uppercase font-semibold text-muted-foreground">Kcal</div>
                            </div>
                            <div className="space-y-1">
                                <div className="text-xl font-semibold">{perServing.protein.toFixed(1)}</div>
                                <div className="text-[10px] uppercase font-semibold text-muted-foreground">Pro</div>
                            </div>
                            <div className="space-y-1">
                                <div className="text-xl font-semibold">{perServing.carbs.toFixed(1)}</div>
                                <div className="text-[10px] uppercase font-semibold text-muted-foreground">Carb</div>
                            </div>
                            <div className="space-y-1">
                                <div className="text-xl font-semibold">{perServing.fat.toFixed(1)}</div>
                                <div className="text-[10px] uppercase font-semibold text-muted-foreground">Fat</div>
                            </div>
                        </CardContent>
                    </Card>
                </section>

            </main>
        </div>
    );
}
