import React, { useState } from 'react';
import { Search, Sparkles, TrendingUp, ArrowRight } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/utils/cn';

interface AISearchHeaderProps {
  onSearch: (query: string) => void;
  initialQuery?: string;
  isSearching?: boolean;
}

export const AISearchHeader: React.FC<AISearchHeaderProps> = ({
  onSearch,
  initialQuery = '',
  isSearching = false
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);

  // Suggerimenti CONCRETI e REALI per le APS
  const suggestions = [
    { icon: "♿", text: "Disabilità e Inclusione", type: "trend" },
    { icon: "⚽", text: "Sport e Giovani", type: "trend" },
    { icon: "🎭", text: "Cultura e Eventi", type: "trend" },
    { icon: "🌳", text: "Ambiente e Verde", type: "trend" },
    { icon: "🚌", text: "Trasporti Sociali", type: "trend" },
    { icon: "🏫", text: "Ristrutturazione Sede", type: "trend" },
    { icon: "💻", text: "Digitalizzazione", type: "trend" },
    { icon: "📚", text: "Formazione", type: "trend" },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query);
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header compatto */}
      <div className="px-4 py-3 bg-gradient-to-r from-orange-50 to-white border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">👋</span>
          <span className="text-sm sm:text-base font-medium text-gray-800">
            Ciao! <span className="font-bold text-iss-bordeaux-600">Cosa cerchi oggi?</span>
          </span>
        </div>
        <div className="hidden sm:flex items-center gap-1 text-xs text-gray-500 bg-white px-2 py-1 rounded-full border">
          <Sparkles className="h-3 w-3 text-iss-gold-500" />
          <span>AI</span>
        </div>
      </div>

      {/* Form di ricerca */}
      <form onSubmit={handleSubmit} className="p-4">
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Search className={cn(
              "absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5",
              isFocused ? "text-iss-bordeaux-600" : "text-gray-400"
            )} />
            <Input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="Es. Pulmino disabili, campo estivo..."
              className="w-full pl-10 pr-4 h-11 text-sm border-gray-200 rounded-lg focus-visible:ring-1 focus-visible:ring-iss-bordeaux-300 focus-visible:border-iss-bordeaux-300"
            />
          </div>
          <Button
            type="submit"
            disabled={isSearching}
            className="h-11 px-6 bg-iss-bordeaux-600 hover:bg-iss-bordeaux-700 text-white font-medium rounded-lg"
          >
            {isSearching ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin">⏳</span> Cerco...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Trova <ArrowRight className="h-4 w-4" />
              </span>
            )}
          </Button>
        </div>
      </form>

      {/* Suggerimenti */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="h-3.5 w-3.5 text-iss-gold-600" />
          <span className="text-xs font-semibold text-gray-500 uppercase">Suggeriti</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {suggestions.map((s, i) => (
            <Badge
              key={i}
              variant="secondary"
              className="cursor-pointer hover:bg-white hover:border-iss-bordeaux-300 hover:text-iss-bordeaux-700 transition-all py-1 px-2.5 bg-white border border-gray-200 text-gray-600 text-xs font-normal rounded-md"
              onClick={() => {
                setQuery(s.text);
                onSearch(s.text);
              }}
            >
              <span className="mr-1.5">{s.icon}</span>
              {s.text}
            </Badge>
          ))}
        </div>
      </div>
    </div>
  );
};
