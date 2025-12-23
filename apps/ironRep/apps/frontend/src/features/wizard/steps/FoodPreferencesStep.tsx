import { useState } from "react";
import { hapticFeedback } from "../../../lib/haptics";
import { cn } from "../../../lib/utils";
import { Search, Check, X, ChefHat, Loader2 } from "lucide-react";
import { useFoodSearch } from "../../nutrition/hooks/useFoodSearch";
import type { FoodItem } from "../../nutrition/types/food.types";

interface FoodPreferencesStepProps {
  onComplete: (preferences: { liked: string[], disliked: string[] }) => void;
  onSkip: () => void;
  initialData?: { liked?: string[], disliked?: string[] };
}

export function FoodPreferencesStep({ onComplete, onSkip, initialData }: FoodPreferencesStepProps) {
  const [liked, setLiked] = useState<string[]>(initialData?.liked || []);
  const [disliked, setDisliked] = useState<string[]>(initialData?.disliked || []);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // REAL FatSecret API calls - NO MOCKS
  const { data: searchResults, isLoading } = useFoodSearch(searchQuery);

  const MAX_VISIBLE_RESULTS = 6;
  const visibleResults = (searchResults || []).slice(0, MAX_VISIBLE_RESULTS);
  const isTruncated = (searchResults || []).length > MAX_VISIBLE_RESULTS;

  const togglePreference = (foodId: string, type: "like" | "dislike") => {
    hapticFeedback.selection();

    if (type === "like") {
      if (liked.includes(foodId)) {
        setLiked(prev => prev.filter(i => i !== foodId));
      } else {
        setLiked(prev => [...prev, foodId]);
        setDisliked(prev => prev.filter(i => i !== foodId));
      }
    } else {
      if (disliked.includes(foodId)) {
        setDisliked(prev => prev.filter(i => i !== foodId));
      } else {
        setDisliked(prev => [...prev, foodId]);
        setLiked(prev => prev.filter(i => i !== foodId));
      }
    }
  };

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden">
      {/* Header */}
      <div className="p-6 pb-4 safe-area-top">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl text-green-600">
            <ChefHat className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">Preferenze Alimentari</h2>
            <p className="text-sm text-muted-foreground">
              Cerca e seleziona i tuoi cibi preferiti o da evitare
            </p>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="px-6 mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Cerca alimenti reali (es: pollo, riso, avena)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-12 pl-10 pr-4 text-[16px] bg-secondary rounded-xl border-2 border-transparent focus:border-primary transition-colors touch-manipulation"
          />
        </div>
      </div>

      {/* Food Results - REAL DATA ONLY */}
      <div className="flex-1 px-6 pb-24 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <span className="ml-2 text-muted-foreground">Ricerca FatSecret in corso...</span>
          </div>
        ) : searchQuery && searchResults && searchResults.length > 0 ? (
          <div className="grid grid-cols-1 gap-3">
            {isTruncated && (
              <div className="text-[11px] text-muted-foreground/70 bg-secondary/40 border border-border/40 rounded-xl px-3 py-2">
                Risultati molti: mostro i primi {MAX_VISIBLE_RESULTS} (NO SCROLL attivo).
              </div>
            )}

            {visibleResults.map((food: FoodItem) => {
              const isLiked = liked.includes(food.id);
              const isDisliked = disliked.includes(food.id);

              return (
                <div
                  key={food.id}
                  className={cn(
                    "p-4 rounded-xl border-2 transition-all",
                    isLiked ? "border-green-500 bg-green-50 dark:bg-green-950/20" :
                      isDisliked ? "border-red-500 bg-red-50 dark:bg-red-950/20" :
                        "border-transparent bg-secondary/50"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-semibold">{food.name}</div>
                      {food.brand && (
                        <div className="text-xs text-muted-foreground">{food.brand}</div>
                      )}
                    </div>

                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => togglePreference(food.id, "dislike")}
                        className={cn(
                          "p-2 rounded-full transition-colors touch-manipulation min-h-[44px] min-w-[44px]",
                          isDisliked ? "bg-red-500 text-white" : "bg-background text-muted-foreground hover:text-red-500"
                        )}
                      >
                        <X className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => togglePreference(food.id, "like")}
                        className={cn(
                          "p-2 rounded-full transition-colors touch-manipulation min-h-[44px] min-w-[44px]",
                          isLiked ? "bg-green-500 text-white" : "bg-background text-muted-foreground hover:text-green-500"
                        )}
                      >
                        <Check className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : searchQuery ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-orange-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Nessun risultato</h3>
            <p className="text-muted-foreground text-sm max-w-xs mx-auto">
              Prova a cercare un altro alimento. Usa termini specifici come "pollo", "riso integrale" o "mela"
            </p>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Cerca Alimenti Reali</h3>
            <p className="text-muted-foreground text-sm max-w-xs mx-auto">
              Inizia a digitare per cercare tra migliaia di alimenti reali dal database FatSecret
            </p>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="absolute bottom-0 left-0 right-0 p-6 bg-background/95 backdrop-blur-md border-t safe-area-bottom">
        <div className="flex gap-3">
          <button
            onClick={onSkip}
            className="flex-1 h-14 rounded-xl font-semibold text-muted-foreground hover:bg-secondary transition-colors touch-manipulation"
          >
            Salta
          </button>
          <button
            onClick={() => onComplete({ liked, disliked })}
            disabled={liked.length === 0 && disliked.length === 0}
            className="flex-[2] h-14 bg-primary text-primary-foreground rounded-xl font-bold shadow-lg active:scale-[0.98] transition-all disabled:opacity-50 touch-manipulation"
          >
            Conferma ({liked.length + disliked.length} selezionati)
          </button>
        </div>
      </div>
    </div>
  );
}
