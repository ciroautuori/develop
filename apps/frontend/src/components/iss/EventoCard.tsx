import React from 'react';
import { Calendar, MapPin, Users, Trophy, Clock, Share2, Star } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/utils/cn';
import type { Evento } from '@/types/api';

interface EventoCardProps {
  evento: Evento;
  onPartecipa?: (evento: Evento) => void;
  onCondividi?: (evento: Evento) => void;
  onDettagli?: (evento: Evento) => void;
  className?: string;
  compact?: boolean;
}

const tipoConfig = {
  hackathon: { 
    label: 'Hackathon', 
    variant: 'default' as const,
    color: 'bg-purple-100 text-purple-800',
    icon: '🚀'
  },
  workshop: { 
    label: 'Workshop', 
    variant: 'info' as const,
    color: 'bg-iss-bordeaux-100 text-iss-bordeaux-800',
    icon: '🛠️'
  },
  conferenza: { 
    label: 'Conferenza', 
    variant: 'success' as const,
    color: 'bg-iss-green-100 text-iss-green-800',
    icon: '🎤'
  },
  laboratorio: { 
    label: 'Laboratorio', 
    variant: 'warning' as const,
    color: 'bg-iss-orange-100 text-iss-orange-800',
    icon: '🔬'
  },
};

export const EventoCard: React.FC<EventoCardProps> = ({
  evento,
  onPartecipa,
  onCondividi,
  onDettagli,
  className,
  compact = false,
}) => {
  const tipoInfo = tipoConfig[evento.tipo];
  const postiRimanenti = evento.partecipanti_max - (evento.partecipanti_attuali || 0);
  const isAlmostFull = postiRimanenti <= 5 && postiRimanenti > 0;
  const isFull = postiRimanenti <= 0;
  const isRegistrationClosed = !evento.iscrizioni_aperte;
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('it-IT', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getDuration = () => {
    const start = new Date(evento.data_evento);
    const end = new Date(evento.data_fine);
    const diffHours = Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60));
    
    if (diffHours < 24) {
      return `${diffHours}h`;
    } else {
      const days = Math.round(diffHours / 24);
      return `${days} giorni`;
    }
  };

  const isUpcoming = () => {
    const eventDate = new Date(evento.data_evento);
    const now = new Date();
    const daysUntilEvent = Math.ceil((eventDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilEvent <= 14 && daysUntilEvent > 0;
  };

  const handlePartecipa = (e: React.MouseEvent) => {
    e.stopPropagation();
    onPartecipa?.(evento);
  };

  const handleCondividi = (e: React.MouseEvent) => {
    e.stopPropagation();
    onCondividi?.(evento);
  };

  const handleDettagli = () => {
    onDettagli?.(evento);
  };

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all duration-200 hover:shadow-lg',
        isFull && 'opacity-75',
        isAlmostFull && 'ring-2 ring-iss-orange-200',
        isUpcoming() && 'ring-2 ring-iss-bordeaux-200',
        className
      )}
      onClick={handleDettagli}
    >
      <CardHeader className={cn('pb-3', compact && 'pb-2')}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Badge className={cn('text-xs', tipoInfo.color)}>
                {tipoInfo.icon} {tipoInfo.label}
              </Badge>
              {isUpcoming() && (
                <Badge variant="info" className="text-xs animate-pulse">
                  In programma
                </Badge>
              )}
              {evento.premi && evento.premi.length > 0 && (
                <Badge variant="warning" className="text-xs gap-1">
                  <Trophy className="h-3 w-3" />
                  Premi
                </Badge>
              )}
            </div>
            
            <h3 className={cn(
              'font-semibold text-card-foreground line-clamp-2 leading-tight',
              compact ? 'text-sm' : 'text-base'
            )}>
              {evento.titolo}
            </h3>
            
            {evento.tema && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
                {evento.tema}
              </p>
            )}
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleCondividi}
              className="h-8 w-8 hover:bg-accent"
            >
              <Share2 className="h-4 w-4" />
            </Button>
            
            {evento.quota_partecipazione > 0 && (
              <div className="text-right">
                <div className="text-lg font-bold text-foreground">
                  €{evento.quota_partecipazione}
                </div>
              </div>
            )}
          </div>
        </div>
      </CardHeader>

      {!compact && (
        <CardContent className="pt-0">
          <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
            {evento.descrizione}
          </p>

          {/* Info Grid */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Data</p>
                <p className="font-medium">
                  {formatDate(evento.data_evento)}
                </p>
                <p className="text-xs text-muted-foreground">
                  ore {formatTime(evento.data_evento)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Durata</p>
                <p className="font-medium">{getDuration()}</p>
                <p className="text-xs text-muted-foreground">
                  fino al {formatDate(evento.data_fine)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Luogo</p>
                <p className="font-medium line-clamp-1">{evento.luogo}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Partecipanti</p>
                <p className={cn(
                  'font-medium',
                  isFull && 'text-red-600',
                  isAlmostFull && 'text-iss-orange-600'
                )}>
                  {evento.partecipanti_attuali || 0} / {evento.partecipanti_max}
                </p>
                {isAlmostFull && !isFull && (
                  <p className="text-xs text-iss-orange-600">Ultimi posti!</p>
                )}
              </div>
            </div>
          </div>

          {/* Premi */}
          {evento.premi && evento.premi.length > 0 && (
            <div className="mt-4">
              <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                <Trophy className="h-3 w-3" />
                Premi in palio:
              </p>
              <div className="space-y-1">
                {evento.premi.slice(0, 3).map((premio, index) => (
                  <div key={index} className="flex items-center gap-2 text-xs">
                    <Star className="h-3 w-3 text-yellow-500 fill-current" />
                    <span className="font-medium">{premio.posizione}° posto:</span>
                    <span className="text-muted-foreground">{premio.premio}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sponsor */}
          {evento.sponsor && evento.sponsor.length > 0 && (
            <div className="mt-4">
              <p className="text-xs text-muted-foreground mb-1">Partner:</p>
              <div className="flex flex-wrap gap-1">
                {evento.sponsor.slice(0, 3).map((sponsor, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {sponsor}
                  </Badge>
                ))}
                {evento.sponsor.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{evento.sponsor.length - 3}
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
            {evento.quota_partecipazione === 0 && (
              <Badge variant="success" className="text-xs">
                Gratuito
              </Badge>
            )}
            {isRegistrationClosed && (
              <Badge variant="outline" className="text-xs">
                Iscrizioni chiuse
              </Badge>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {onDettagli && (
              <Button variant="outline" size="sm">
                Dettagli
              </Button>
            )}
            
            <Button
              variant={isFull || isRegistrationClosed ? "outline" : "iss-primary"}
              size="sm"
              onClick={handlePartecipa}
              disabled={isFull || isRegistrationClosed}
              className="gap-1"
            >
              {isFull ? (
                "Completo"
              ) : isRegistrationClosed ? (
                "Chiuso"
              ) : isAlmostFull ? (
                "Registrati ora!"
              ) : (
                "Partecipa"
              )}
            </Button>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
};
