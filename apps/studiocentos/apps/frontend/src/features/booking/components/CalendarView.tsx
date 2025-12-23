/**
 * CalendarView - Calendario mensile con slot disponibili
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card';
import { Button } from '../../../shared/components/ui/button';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { useAvailability } from '../hooks/useAvailability';
import type { ServiceType } from '../types/booking.types';

interface CalendarViewProps {
  serviceType?: ServiceType;
  onSlotSelect: (datetime: string, duration: number) => void;
}

export function CalendarView({ serviceType, onSlotSelect }: CalendarViewProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  const startDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
  const endDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0);
  
  const { availability, loading, error } = useAvailability({
    startDate,
    endDate,
    serviceType,
  });

  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-gray-400">Errore nel caricamento del calendario: {error.message}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            {currentMonth.toLocaleDateString('it-IT', { month: 'long', year: 'numeric' })}
          </CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={prevMonth}>
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={nextMonth}>
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">Caricamento...</div>
        ) : (
          <div className="space-y-4">
            {availability.map((day) => (
              <div key={day.date} className="border-b pb-4 last:border-0">
                <h3 className="font-semibold mb-2">
                  {new Date(day.date).toLocaleDateString('it-IT', {
                    weekday: 'long',
                    day: 'numeric',
                    month: 'long',
                  })}
                </h3>
                <div className="grid grid-cols-4 gap-2">
                  {day.slots.map((slot, idx) => (
                    <Button
                      key={idx}
                      variant="outline"
                      size="sm"
                      onClick={() => onSlotSelect(slot.datetime, slot.duration_minutes)}
                      disabled={!slot.available}
                    >
                      {new Date(slot.datetime).toLocaleTimeString('it-IT', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </Button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
