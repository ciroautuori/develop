import { useMemo, useState, useEffect } from "react";
import { Search, Filter, X, Sparkles } from "lucide-react";
import { Input } from "../../../../shared/components/ui/input";
import { Button } from "../../../../shared/components/ui/button";
import { Badge } from "../../../../shared/components/ui/badge";
import { useFoodFavorites, useFoodSearch, useToggleFoodFavorite } from "../../hooks/useFoodSearch";
import { FoodItemCard } from "./FoodItemCard";
import type { FoodItem } from "../../types/food.types";
import { hapticFeedback } from "../../../../lib/haptics";
import { toast } from "../../../../components/ui/Toast";
import { authToken } from "../../../../lib/authToken";

interface FoodSearchPanelProps {
  onSelectFood?: (food: FoodItem) => void;
}

function isLikelyPreparedDish(food: FoodItem): boolean {
  const name = (food.name ?? "").toLowerCase();
  if (!name) return false;

  // Heuristic: exclude composite dishes for category quick filters.
  // Keep this minimal and focused on the most common patterns coming from FatSecret.
  const patterns = [
    " with ",
    " sauce",
    " salad",
    " mixture",
    " baked",
    " canned",
    " carbonara",
    " pesto",
    " marinara",
    " gravy",
    " garden",
    " flavored ",
    " beverage",
    " atole ",
    " con ",
    " salsa",
    " insalata",
    " al sugo",
    " alla ",
  ];

  return patterns.some((p) => name.includes(p));
}

// Map category to search keywords for better FatSecret results
function getCategoryKeywords(category: string): string {
  switch (category) {
    case "protein":
      return "pollo manzo pesce carne proteine";
    case "carbs":
      return "riso pasta pane avena";
    case "vegetables":
      return "verdure spinaci broccoli";
    case "fruits":
      return "frutta mela banana";
    case "dairy":
      return "latte formaggio yogurt";
    case "fats":
      return "avocado frutta secca olio";
    default:
      return "";
  }
}

function passesMacroCategoryFilter(category: string, food: FoodItem): boolean {
  const p = Number(food.protein) || 0;
  const c = Number(food.carbs) || 0;
  const f = Number(food.fat) || 0;
  const kcal = Number(food.calories) || 0;

  // Defensive: ignore items with no meaningful macros
  if (kcal <= 0 && p <= 0 && c <= 0 && f <= 0) return false;

  // Heuristic: categories are meant to show *alimenti base* (macro-driven), not prepared dishes.
  // Values are per 100g (backend normalization).
  switch (category) {
    case "protein":
      return p >= 15 && c <= 10 && kcal <= 350;
    case "carbs":
      return c >= 20 && f <= 10 && kcal <= 450;
    case "vegetables":
      return kcal <= 90 && c <= 15 && f <= 5;
    case "fruits":
      return kcal <= 120 && f <= 3 && p <= 5;
    case "dairy":
      return kcal <= 250 && (p >= 3 || f >= 3);
    case "fats":
      return f >= 10 && c <= 15 && p <= 15;
    default:
      return true;
  }
}

// Skeleton for loading state
function FoodSkeleton() {
  return (
    <div className="p-4 rounded-xl border border-border bg-card animate-pulse">
      <div className="flex items-start justify-between mb-3">
        <div className="space-y-2 flex-1">
          <div className="h-4 bg-muted rounded w-3/4" />
          <div className="h-3 bg-muted rounded w-1/2" />
        </div>
      </div>
      <div className="grid grid-cols-4 gap-2 mb-3">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="text-center space-y-1">
            <div className="h-6 bg-muted rounded w-12 mx-auto" />
            <div className="h-2 bg-muted rounded w-8 mx-auto" />
          </div>
        ))}
      </div>
      <div className="flex gap-2 pt-3 border-t border-border">
        <div className="h-8 bg-muted rounded flex-1" />
        <div className="h-8 bg-muted rounded flex-1" />
      </div>
    </div>
  );
}

export function FoodSearchPanel({ onSelectFood }: FoodSearchPanelProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [favoritesErrorShown, setFavoritesErrorShown] = useState(false);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Include category in search query for better results
  const searchQuery = useMemo(() => {
    const q = debouncedQuery.trim();
    if (!selectedCategory) return q;

    // OPTIMIZATION: If user typed a query ("Mela"), DO NOT append keywords ("...pollo manzo").
    // Let the backend/FatSecret search for "Mela" specifically.
    // Client-side filtering (passesMacroCategoryFilter) will handle the "Protein" aspect.
    if (q) return q;

    // If query is empty, use keywords to populate "Quick Action" results
    const keywords = getCategoryKeywords(selectedCategory).trim();
    return keywords;
  }, [debouncedQuery, selectedCategory]);

  const { data: foods, isLoading, isFetching } = useFoodSearch(searchQuery);
  const token = authToken.get();
  const isAuthed = !!token;

  const {
    data: favorites,
    isError: isFavoritesError,
  } = useFoodFavorites({ enabled: isAuthed });
  const toggleFavorite = useToggleFoodFavorite();

  useEffect(() => {
    if (!isAuthed) {
      if (favoritesErrorShown) {
        setFavoritesErrorShown(false);
      }
      return;
    }

    if (isFavoritesError && !favoritesErrorShown) {
      toast.error("Preferiti non disponibili al momento");
      setFavoritesErrorShown(true);
    }
  }, [favoritesErrorShown, isAuthed, isFavoritesError]);

  const favoriteIds = useMemo(() => {
    return new Set((favorites ?? []).map((f) => String(f.id)));
  }, [favorites]);

  // Static categories with icons
  const categories = [
    { id: "protein", name: "Proteine", icon: "🥩" },
    { id: "carbs", name: "Carboidrati", icon: "🍞" },
    { id: "vegetables", name: "Verdure", icon: "🥬" },
    { id: "fruits", name: "Frutta", icon: "🍎" },
    { id: "dairy", name: "Latticini", icon: "🥛" },
    { id: "fats", name: "Grassi", icon: "🥑" },
  ];

  const clearSearch = () => {
    hapticFeedback.selection();
    setQuery("");
    setDebouncedQuery("");
  };

  const filteredFoods = useMemo(() => {
    if (!foods) return foods;
    if (!selectedCategory) return foods;
    const strict = foods.filter(
      (f) => !isLikelyPreparedDish(f) && passesMacroCategoryFilter(selectedCategory, f)
    );
    if (strict.length > 0) return strict;

    const macroOnly = foods.filter((f) => passesMacroCategoryFilter(selectedCategory, f));
    if (macroOnly.length > 0) return macroOnly;

    const noPrepared = foods.filter((f) => !isLikelyPreparedDish(f));
    if (noPrepared.length > 0) return noPrepared;

    return foods;
  }, [foods, selectedCategory]);

  return (
    <div className="space-y-4">
      {/* Search Bar - Mobile Optimized */}
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur-xl pb-3 -mx-1 px-1">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground pointer-events-none" />
            <Input
              placeholder="Cerca alimenti..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-11 pr-10 h-12 text-base rounded-xl border-2 focus:border-primary transition-colors"
            />
            {query && (
              <button
                onClick={clearSearch}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-muted transition-colors"
              >
                <X className="h-4 w-4 text-muted-foreground" />
              </button>
            )}
          </div>
          <Button variant="outline" size="icon" className="h-12 w-12 rounded-xl shrink-0">
            <Filter className="h-5 w-5" />
          </Button>
        </div>

        {/* Category Pills - Horizontal Scroll */}
        <div className="flex gap-2 overflow-x-auto scrollbar-hide py-3 -mx-1 px-1">
          {categories?.map((cat) => (
            <Badge
              key={cat.id}
              variant={selectedCategory === cat.id ? "default" : "outline"}
              className="cursor-pointer whitespace-nowrap px-4 py-2 text-sm rounded-full transition-all active:scale-95 touch-manipulation"
              onClick={() => {
                hapticFeedback.selection();
                setSelectedCategory(cat.id === selectedCategory ? null : cat.id);
              }}
            >
              <span className="mr-1.5">{cat.icon}</span>
              {cat.name}
            </Badge>
          ))}
        </div>
      </div>

      {/* Results */}
      <div className="space-y-3">
        {/* Loading State */}
        {isLoading || isFetching ? (
          <div className="space-y-3 animate-fade-in">
            {[...Array(3)].map((_, i) => (
              <FoodSkeleton key={i} />
            ))}
          </div>
        ) : !debouncedQuery && !selectedCategory ? (
          /* Empty State - Initial */
          <div className="text-center py-12 animate-fade-in">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-8 h-8 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Cerca Alimenti</h3>
            <p className="text-muted-foreground text-sm max-w-xs mx-auto">
              Cerca tra migliaia di alimenti per tracciare i tuoi macro
            </p>
          </div>
        ) : debouncedQuery.trim().length > 0 && debouncedQuery.trim().length < 3 ? (
          <div className="text-center py-12 animate-fade-in">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Scrivi almeno 3 caratteri</h3>
            <p className="text-muted-foreground text-sm">La ricerca richiede minimo 3 lettere</p>
          </div>
        ) : filteredFoods?.length === 0 ? (
          /* No Results */
          <div className="text-center py-12 animate-fade-in">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Nessun risultato</h3>
            <p className="text-muted-foreground text-sm">
              {selectedCategory ? "Nessun alimento trovato in questa categoria" : "Prova con un termine diverso"}
            </p>
          </div>
        ) : (
          /* Results List */
          <div className="space-y-3">
            <p className="text-xs text-muted-foreground px-1">
              {filteredFoods?.length} risultati{selectedCategory ? " nella categoria selezionata" : ""}
              {debouncedQuery ? ` per "${debouncedQuery}"` : ""}
            </p>
            {filteredFoods?.map((food, index) => (
              <div
                key={food.id}
                className="animate-slide-up"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <FoodItemCard
                  food={food}
                  onAdd={() => onSelectFood?.(food)}
                  isFavorite={favoriteIds.has(String(food.id))}
                  favoriteDisabled={!isAuthed || toggleFavorite.isPending}
                  onToggleFavorite={() =>
                    isAuthed
                      ? toggleFavorite.mutate(
                        {
                          foodId: String(food.id),
                          isFavorite: favoriteIds.has(String(food.id)),
                        },
                        {
                          onError: () => {
                            toast.error("Errore preferiti: verifica connessione e riprova");
                          },
                        }
                      )
                      : toast.info("Accedi per usare i preferiti")
                  }
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
