/**
 * ServiceSelector - Selezione tipo di servizio
 */

import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card';
import { Button } from '../../../shared/components/ui/button';
import { MessageSquare } from 'lucide-react';
import type { ServiceType } from '../types/booking.types';
import { SERVICE_TYPES } from '../types/booking.types';

interface ServiceSelectorProps {
  selectedService?: ServiceType;
  onServiceSelect: (service: ServiceType) => void;
}

const SERVICE_ICONS: Record<ServiceType, React.ReactNode> = {
  consultation: <MessageSquare className="w-6 h-6" />,
  demo: <span className="text-2xl">📊</span>,
  technical_support: <span className="text-2xl">🔧</span>,
  training: <span className="text-2xl">🎓</span>,
  discovery_call: <span className="text-2xl">📞</span>,
};

const SERVICE_DESCRIPTIONS: Record<ServiceType, string> = {
  consultation: 'Consulenza personalizzata per il tuo progetto',
  demo: 'Demo live dei nostri prodotti e servizi',
  technical_support: 'Supporto tecnico per problemi specifici',
  training: 'Sessione di formazione su tecnologie e best practices',
  discovery_call: 'Chiamata conoscitiva per valutare collaborazioni',
};

export function ServiceSelector({ selectedService, onServiceSelect }: ServiceSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Seleziona il tipo di servizio</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid md:grid-cols-2 gap-4">
          {(Object.keys(SERVICE_TYPES) as ServiceType[]).map((serviceKey) => {
            const isSelected = selectedService === serviceKey;
            
            return (
              <Button
                key={serviceKey}
                variant={isSelected ? 'default' : 'outline'}
                className="h-auto p-4 flex flex-col items-start gap-2"
                onClick={() => onServiceSelect(serviceKey)}
              >
                <div className="flex items-center gap-3 w-full">
                  {SERVICE_ICONS[serviceKey]}
                  <span className="font-semibold">{SERVICE_TYPES[serviceKey]}</span>
                </div>
                <p className="text-sm text-left opacity-75">
                  {SERVICE_DESCRIPTIONS[serviceKey]}
                </p>
              </Button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
