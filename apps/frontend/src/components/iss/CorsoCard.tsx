import React from 'react';
import { Calendar, MapPin, Users, Clock, Award, BookOpen, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/utils/cn';
import type { Corso } from '@/types/api';

interface CorsoCardProps {
  corso: Corso;
  onIscrizione?: (corso: Corso) => void;
  onInfo?: (corso: Corso) => void;
  className?: string;
  compact?: boolean;
}

const categoriaConfig = {
  alfabetizzazione: { 
    label: 'Alfabetizzazione Digitale', 
    variant: 'info' as const,
    color: 'bg-iss-bordeaux-100 text-iss-bordeaux-800'
  },
  professionale: { 
    label: 'Formazione Professionale', 
    variant: 'success' as const,
    color: 'bg-iss-green-100 text-iss-green-800'
  },
  assistive: { 
    label: 'Tecnologie Assistive', 
    variant: 'warning' as const,
    color: 'bg-iss-orange-100 text-iss-orange-800'
  },
  avanzato: { 
    label: 'Corso Avanzato', 
    variant: 'default' as const,
    color: 'bg-gray-100 text-gray-800'
  },
};

const livelloConfig = {
  base: { label: 'Base', color: 'bg-green-100 text-green-800' },
  intermedio: { label: 'Intermedio', color: 'bg-yellow-100 text-yellow-800' },
  avanzato: { label: 'Avanzato', color: 'bg-red-100 text-red-800' },
};

export const CorsoCard: React.FC<CorsoCardProps> = ({
  corso,
  onIscrizione,
  onInfo,
  className,
  compact = false,
}) => {
  const categoriaInfo = categoriaConfig[corso.categoria];
  const livelloInfo = livelloConfig[corso.livello];
  const postiRimanenti = corso.posti_disponibili;
  const isAlmostFull = postiRimanenti <= 3 && postiRimanenti > 0;
  const isFull = postiRimanenti === 0;
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('it-IT', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const isStartingSoon = () => {
    const startDate = new Date(corso.data_inizio);
    const now = new Date();
    const daysUntilStart = Math.ceil((startDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilStart <= 7 && daysUntilStart > 0;
  };

  const handleIscrizione = (e: React.MouseEvent) => {
    e.stopPropagation();
    onIscrizione?.(corso);
  };

  const handleInfo = () => {
    onInfo?.(corso);
  };

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all duration-200 hover:shadow-lg',
        isFull && 'opacity-75',
        isAlmostFull && 'ring-2 ring-iss-orange-200',
        className
      )}
      onClick={handleInfo}
    >
      <CardHeader className={cn('pb-3', compact && 'pb-2')}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Badge variant={categoriaInfo.variant} className="text-xs">
                {categoriaInfo.label}
              </Badge>
              <Badge className={cn('text-xs', livelloInfo.color)}>
                {livelloInfo.label}
              </Badge>
              {isStartingSoon() && (
                <Badge variant="warning" className="text-xs animate-pulse">
                  Inizia presto!
                </Badge>
              )}
            </div>
            
            <h3 className={cn(
              'font-semibold text-card-foreground line-clamp-2 leading-tight',
              compact ? 'text-sm' : 'text-base'
            )}>
              {corso.titolo}
            </h3>
            
            <div className="flex items-center gap-1 mt-1">
              <BookOpen className="h-3 w-3 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                {corso.docente}
              </span>
            </div>
          </div>

          <div className="text-right">
            <div className={cn(
              'text-lg font-bold',
              corso.prezzo === 0 ? 'text-iss-green-600' : 'text-foreground'
            )}>
              {corso.prezzo === 0 ? 'Gratuito' : `€${corso.prezzo}`}
            </div>
            {corso.certificazione && (
              <div className="flex items-center gap-1 mt-1">
                <Award className="h-3 w-3 text-iss-bordeaux-600" />
                <span className="text-xs text-iss-bordeaux-600">Certificazione</span>
              </div>
            )}
          </div>
        </div>
      </CardHeader>

      {!compact && (
        <CardContent className="pt-0">
          <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
            {corso.descrizione}
          </p>

          {/* Info Grid */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Inizio</p>
                <p className="font-medium">
                  {formatDate(corso.data_inizio)}
                </p>
                <p className="text-xs text-muted-foreground">
                  ore {formatTime(corso.data_inizio)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Durata</p>
                <p className="font-medium">{corso.durata_ore} ore</p>
                <p className="text-xs text-muted-foreground">
                  fino al {formatDate(corso.data_fine)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Sede</p>
                <p className="font-medium line-clamp-1">{corso.sede}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Posti</p>
                <p className={cn(
                  'font-medium',
                  isFull && 'text-red-600',
                  isAlmostFull && 'text-iss-orange-600'
                )}>
                  {postiRimanenti} / {corso.posti_totali}
                </p>
                {isAlmostFull && !isFull && (
                  <p className="text-xs text-iss-orange-600">Ultimi posti!</p>
                )}
              </div>
            </div>
          </div>

          {/* Prerequisites */}
          {corso.requisiti.length > 0 && corso.requisiti[0] !== "Nessun prerequisito" && (
            <div className="mt-4">
              <p className="text-xs text-muted-foreground mb-1">Prerequisiti:</p>
              <div className="flex flex-wrap gap-1">
                {corso.requisiti.slice(0, 2).map((requisito, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {requisito}
                  </Badge>
                ))}
                {corso.requisiti.length > 2 && (
                  <Badge variant="outline" className="text-xs">
                    +{corso.requisiti.length - 2}
                  </Badge>
                )}
              </div>
            </div>
          )}
        </CardContent>
      )}

      <CardFooter className={cn('pt-3 border-t', compact && 'pt-2')}>
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            {corso.materiali_inclusi && (
              <Badge variant="outline" className="text-xs">
                Materiali inclusi
              </Badge>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {onInfo && (
              <Button variant="outline" size="sm" className="gap-1">
                Dettagli
                <ChevronRight className="h-3 w-3" />
              </Button>
            )}
            
            <Button
              variant={isFull ? "outline" : "iss-primary"}
              size="sm"
              onClick={handleIscrizione}
              disabled={isFull}
              className="gap-1"
            >
              {isFull ? (
                "Completo"
              ) : isAlmostFull ? (
                "Iscriviti ora!"
              ) : (
                "Iscriviti"
              )}
            </Button>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
};
