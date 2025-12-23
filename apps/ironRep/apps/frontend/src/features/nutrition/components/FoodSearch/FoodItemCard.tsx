import type React from "react";
import { Plus, Info, Star, Flame, Beef, Wheat, Droplets } from "lucide-react";
import { Button } from "../../../../shared/components/ui/button";
import { Badge } from "../../../../shared/components/ui/badge";
import type { FoodItem } from "../../types/food.types";
import { touchTarget } from "../../../../lib/touch-targets";
import { cn } from "../../../../lib/utils";
import { hapticFeedback } from "../../../../lib/haptics";

interface FoodItemCardProps {
  food: FoodItem;
  onSelect?: () => void;
  onAdd?: () => void;
  isFavorite?: boolean;
  onToggleFavorite?: () => void;
  favoriteDisabled?: boolean;
}

export function FoodItemCard({
  food,
  onSelect,
  onAdd,
  isFavorite = false,
  onToggleFavorite,
  favoriteDisabled = false,
}: FoodItemCardProps) {
  const handleAdd = (e: React.MouseEvent) => {
    e.stopPropagation();
    hapticFeedback.impact("medium");
    onAdd?.();
  };

  const handleSelect = () => {
    hapticFeedback.selection();
    onSelect?.();
  };

  const handleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    hapticFeedback.selection();
    onToggleFavorite?.();
  };

  return (
    <div
      className={cn(
        "p-5 rounded-2xl border-2 border-border bg-card hover:border-primary/30 hover:shadow-lg",
        "transition-all duration-300 cursor-pointer group",
        touchTarget.manipulation,
        touchTarget.active
      )}
      onClick={handleSelect}
    >
      {/* Header */}
      <div className="flex items-start gap-4 mb-4">
        {/* Food Icon */}
        <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center shrink-0">
          <span className="text-3xl">🍽️</span>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-bold text-lg line-clamp-1 group-hover:text-primary transition-colors">
                {food.name}
              </h3>
              {food.brand && (
                <p className="text-sm text-muted-foreground mt-1">{food.brand}</p>
              )}
            </div>
            <button
              onClick={handleFavorite}
              disabled={favoriteDisabled}
              className={cn(
                touchTarget.icon.sm,
                "rounded-full hover:bg-muted transition-colors opacity-60 hover:opacity-100 disabled:opacity-40 disabled:pointer-events-none"
              )}
              aria-label={isFavorite ? "Rimuovi dai preferiti" : "Aggiungi ai preferiti"}
            >
              <Star
                className={cn("h-5 w-5", isFavorite && "text-primary")}
                {...(isFavorite ? { fill: "currentColor" } : {})}
              />
            </button>
          </div>

          {/* Type Badge */}
          {food.type && (
            <Badge
              variant="secondary"
              className="text-xs mt-2 px-2.5 py-1 rounded-full"
            >
              {String(food.type).toLowerCase().includes("brand") ? "🏷️ Marca" : "📦 Generico"}
            </Badge>
          )}
        </div>
      </div>

      {/* Macros Grid */}
      <div className="grid grid-cols-4 gap-2 p-4 rounded-xl bg-muted/50 mb-4">
        <MacroItem
          icon={<Flame className="w-4 h-4" />}
          value={Math.round(food.calories)}
          unit=""
          valueSuffix="kcal"
          color="text-orange-500"
          bgColor="bg-orange-500/10"
        />
        <MacroItem
          icon={<Beef className="w-4 h-4" />}
          value={food.protein}
          unit="prot"
          valueSuffix="g"
          color="text-red-500"
          bgColor="bg-red-500/10"
        />
        <MacroItem
          icon={<Wheat className="w-4 h-4" />}
          value={food.carbs}
          unit="carb"
          valueSuffix="g"
          color="text-amber-500"
          bgColor="bg-amber-500/10"
        />
        <MacroItem
          icon={<Droplets className="w-4 h-4" />}
          value={food.fat}
          unit="fat"
          valueSuffix="g"
          color="text-blue-500"
          bgColor="bg-blue-500/10"
        />
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          variant="outline"
          size="sm"
          className={cn(
            "flex-1 h-12 rounded-xl font-semibold",
            touchTarget.manipulation
          )}
          onClick={(e) => {
            e.stopPropagation();
            handleSelect();
          }}
        >
          <Info className="h-5 w-5 mr-2" />
          Dettagli
        </Button>
        <Button
          size="sm"
          className={cn(
            "flex-1 h-12 rounded-xl bg-primary hover:bg-primary/90 font-bold shadow-lg",
            touchTarget.manipulation
          )}
          onClick={handleAdd}
        >
          <Plus className="h-5 w-5 mr-2" />
          Aggiungi
        </Button>
      </div>
    </div>
  );
}

function MacroItem({
  icon,
  value,
  unit,
  valueSuffix,
  color,
  bgColor
}: {
  icon: React.ReactNode;
  value: number;
  unit: string;
  valueSuffix: string;
  color: string;
  bgColor: string;
}) {
  return (
    <div className="text-center">
      <div className={`inline-flex items-center justify-center w-8 h-8 rounded-lg ${bgColor} ${color} mb-1.5`}>
        {icon}
      </div>
      <div className={`text-base font-bold ${color}`}>
        {value}
        {valueSuffix ? (
          <span className="text-xs font-normal ml-0.5">{valueSuffix}</span>
        ) : null}
      </div>
      {unit ? (
        <div className="text-[10px] text-muted-foreground uppercase tracking-wider mt-0.5">
          {unit}
        </div>
      ) : null}
    </div>
  );
}
