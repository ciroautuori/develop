import React from 'react';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Bando } from '@/types/api';
import {
  Calendar,
  Euro,
  Building2,
  ExternalLink,
  Bookmark,
  BookmarkPlus,
  Target,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { cn } from '@/utils/cn';

interface SmartBandoCardProps {
  bando: Bando;
  matchScore?: number; // 0-100
  isSaved?: boolean;
  onSave?: (bando: Bando) => void;
  onView?: (bando: Bando) => void;
}

export const SmartBandoCard: React.FC<SmartBandoCardProps> = ({
  bando,
  matchScore = 0,
  isSaved = false,
  onSave,
  onView
}) => {
  // Calcolo colori dinamici basati sullo stato
  const isExpiringSoon = bando.giorni_rimanenti !== undefined && bando.giorni_rimanenti <= 7;
  const isExpired = bando.scaduto;

  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat('it-IT', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(dateString));
  };

  const formatMoney = (amount: number) => {
    return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(amount);
  };

  return (
    <Card
      className={cn(
        "group relative overflow-hidden transition-all duration-300 hover:shadow-xl border-gray-200 hover:border-iss-bordeaux-200 flex flex-col h-full bg-white",
        isExpired && "opacity-75 grayscale-[0.5]"
      )}
    >
      {/* Top Bar - Match Score & Status */}
      <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-gray-100 to-gray-200">
        <div
          className={cn(
            "h-full transition-all duration-1000",
            matchScore > 80 ? "bg-green-500" : matchScore > 50 ? "bg-iss-gold-500" : "bg-gray-300"
          )}
          style={{ width: `${matchScore}%` }}
        />
      </div>

      <CardContent className="p-5 flex-grow">
        <div className="flex justify-between items-start mb-4">
          <div className="flex gap-2 mb-1">
            {matchScore > 0 && (
              <Badge variant={matchScore > 80 ? "success" : "secondary"} className="rounded-full px-3 py-0.5 text-xs font-semibold">
                <Target className="w-3 h-3 mr-1" />
                {matchScore}% Match
              </Badge>
            )}

            {/* Badge Speciali per Invitalia/Ministeri */}
            {bando.ente && (bando.ente.toLowerCase().includes('invitalia') || bando.fonte === 'altro') ? (
              <Badge className="bg-blue-600 text-white border-blue-700 rounded-full text-xs font-bold shadow-sm">
                🇮🇹 NAZIONALE
              </Badge>
            ) : (
              <Badge variant="outline" className="text-gray-500 border-gray-200 rounded-full text-xs">
                {bando.categoria || 'Generale'}
              </Badge>
            )}
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => { e.stopPropagation(); onSave?.(bando); }}
            className="h-8 w-8 text-gray-400 hover:text-iss-gold-600 -mr-2 -mt-2"
          >
            {isSaved ? <Bookmark className="h-5 w-5 fill-current text-iss-gold-600" /> : <BookmarkPlus className="h-5 w-5" />}
          </Button>
        </div>

        {/* Title & Organization */}
        <div className="mb-6">
          <h3 className="text-lg font-bold text-gray-900 leading-tight mb-2 group-hover:text-iss-bordeaux-700 transition-colors line-clamp-2">
            {bando.title}
          </h3>
          <div className="flex items-center text-sm text-gray-500 font-medium">
            <Building2 className="w-4 h-4 mr-1.5 text-gray-400" />
            {bando.ente}
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-50 rounded-lg p-3 border border-gray-100 group-hover:bg-iss-gold-50/30 transition-colors">
            <div className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1 flex items-center">
              <Euro className="w-3 h-3 mr-1" /> Contributo Max
            </div>
            <div className="text-lg font-bold text-gray-900">
              {bando.importo_max ? formatMoney(bando.importo_max) : "N/D"}
            </div>
          </div>

          <div className={cn(
            "rounded-lg p-3 border transition-colors",
            isExpiringSoon ? "bg-orange-50 border-orange-100 text-orange-900" : "bg-gray-50 border-gray-100 group-hover:bg-iss-gold-50/30"
          )}>
            <div className="text-xs font-medium uppercase tracking-wide mb-1 flex items-center opacity-70">
              <Clock className="w-3 h-3 mr-1" /> Scadenza
            </div>
            <div className="text-lg font-bold">
              {bando.scadenza ? formatDate(bando.scadenza) : "Aperto"}
            </div>
            {isExpiringSoon && (
              <div className="text-xs font-bold text-orange-600 mt-1 animate-pulse">
                Scade tra {bando.giorni_rimanenti} giorni!
              </div>
            )}
          </div>
        </div>

        {/* Description Preview */}
        <p className="text-sm text-gray-600 line-clamp-3 mb-4 leading-relaxed">
          {bando.descrizione || "Nessuna descrizione disponibile per questo bando."}
        </p>
      </CardContent>

      <CardFooter className="p-5 pt-0 mt-auto flex gap-3">
        <Button
          onClick={() => onView?.(bando)}
          className="flex-1 bg-white border-2 border-gray-200 text-gray-700 hover:border-iss-bordeaux-600 hover:text-iss-bordeaux-700 font-semibold"
        >
          Dettagli
        </Button>
        <Button
          onClick={() => window.open(bando.link, '_blank')}
          className="flex-1 bg-gray-900 hover:bg-iss-bordeaux-700 text-white shadow-lg shadow-gray-200"
        >
          Sito Ufficiale <ExternalLink className="w-4 h-4 ml-2" />
        </Button>
      </CardFooter>
    </Card>
  );
};
