import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { Plus, ChefHat, Trash2, Utensils } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

import { Button } from "../../../shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../../shared/components/ui/card";
import { Badge } from "../../../shared/components/ui/badge";
import { Skeleton } from "../../../shared/components/ui/skeleton";
import { toast } from "../../../components/ui/Toast";

import { recipesApi } from "../../../lib/api/recipes";
import type { Recipe } from "../../../types/recipes";

export function RecipesPage() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const { data: recipes, isLoading, error } = useQuery({
        queryKey: ["recipes"],
        queryFn: () => recipesApi.getAll(),
    });

    const deleteMutation = useMutation({
        mutationFn: recipesApi.delete,
        onSuccess: () => {
            toast.success("Ricetta eliminata");
            queryClient.invalidateQueries({ queryKey: ["recipes"] });
        },
        onError: () => {
            toast.error("Errore eliminazione");
        }
    });

    const handleDelete = (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        if (confirm("Sei sicuro di voler eliminare questa ricetta?")) {
            deleteMutation.mutate(id);
        }
    };

    const handleEdit = (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        // For now, navigation to edit not implemented in routing, 
        // but assuming /recipes/edit/$id or just /recipes/$id
        // But my plan was simply Create and List.
        // I'll leave this for now or navigate to create logic (if I add edit mode later).
        toast.info("Funzione modifica in arrivo!");
    };

    const handleCreate = () => {
        navigate({ to: "/recipes/create" });
    };

    if (isLoading) {
        return (
            <div className="container p-4 space-y-4">
                <Skeleton className="h-10 w-40" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[1, 2, 3, 4].map((i) => (
                        <Skeleton key={i} className="h-40 w-full rounded-xl" />
                    ))}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center p-10 text-destructive">
                <p>Errore caricamento ricette.</p>
                <Button variant="outline" onClick={() => queryClient.invalidateQueries({ queryKey: ["recipes"] })}>Riprova</Button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background pb-20 md:pb-0">
            <header className="sticky top-0 z-20 w-full bg-background/95 backdrop-blur border-b px-4 h-14 flex items-center justify-between">
                <h1 className="text-xl font-bold flex items-center gap-2">
                    <ChefHat className="text-primary h-6 w-6" />
                    Le Mie Ricette
                </h1>
                <Button size="sm" onClick={handleCreate} className="rounded-full gap-1">
                    <Plus className="h-4 w-4" />
                    Nuova
                </Button>
            </header>

            <main className="container p-4">
                {recipes?.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
                        <div className="bg-muted p-6 rounded-full">
                            <Utensils className="h-10 w-10 text-muted-foreground" />
                        </div>
                        <div className="space-y-1">
                            <h3 className="text-lg font-semibold">Nessuna ricetta salvata</h3>
                            <p className="text-muted-foreground max-w-xs mx-auto">
                                Crea le tue ricette personali usando ingredienti puri per un tracciamento preciso.
                            </p>
                        </div>
                        <Button onClick={handleCreate}>Inizia ora</Button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <AnimatePresence>
                            {recipes?.map((recipe) => (
                                <motion.div
                                    key={recipe.id}
                                    layout
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0 }}
                                >
                                    <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-primary" onClick={() => handleEdit(null as any, recipe.id)}>
                                        <CardHeader className="pb-2">
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <CardTitle className="text-lg">{recipe.name}</CardTitle>
                                                    {recipe.description && (
                                                        <CardDescription className="line-clamp-1">{recipe.description}</CardDescription>
                                                    )}
                                                </div>
                                                <div className="flex gap-1">
                                                    <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive/70 hover:text-destructive hover:bg-destructive/10" onClick={(e) => handleDelete(e, recipe.id)}>
                                                        <Trash2 className="h-4 w-4" />
                                                    </Button>
                                                </div>
                                            </div>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="grid grid-cols-4 gap-2 text-center text-sm py-2 bg-muted/30 rounded-lg">
                                                <div>
                                                    <span className="block font-bold text-primary">{recipe.total_calories.toFixed(0)}</span>
                                                    <span className="text-xs text-muted-foreground">kcal</span>
                                                </div>
                                                <div>
                                                    <span className="block font-semibold">{recipe.total_protein.toFixed(0)}</span>
                                                    <span className="text-xs text-muted-foreground">Pro</span>
                                                </div>
                                                <div>
                                                    <span className="block font-semibold">{recipe.total_carbs.toFixed(0)}</span>
                                                    <span className="text-xs text-muted-foreground">Carb</span>
                                                </div>
                                                <div>
                                                    <span className="block font-semibold">{recipe.total_fat.toFixed(0)}</span>
                                                    <span className="text-xs text-muted-foreground">Fat</span>
                                                </div>
                                            </div>
                                            <div className="mt-3 flex gap-2 text-xs text-muted-foreground">
                                                <Badge variant="secondary" className="font-normal">
                                                    {recipe.ingredients.length} ingredienti
                                                </Badge>
                                                <Badge variant="secondary" className="font-normal">
                                                    {recipe.servings} porzioni
                                                </Badge>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                )}
            </main>
        </div>
    );
}
