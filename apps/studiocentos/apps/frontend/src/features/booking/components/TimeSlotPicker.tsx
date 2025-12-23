/**
 * TimeSlotPicker - Selezione slot orario specifico
 */

import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card';
import { Button } from '../../../shared/components/ui/button';
import { Clock } from 'lucide-react';
import type { AvailableSlot } from '../types/booking.types';

interface TimeSlotPickerProps {
  date: Date;
  slots: AvailableSlot[];
  selectedSlot?: string;
  onSlotSelect: (datetime: string, duration: number) => void;
}

export function TimeSlotPicker({ date, slots, selectedSlot, onSlotSelect }: TimeSlotPickerProps) {
  const availableSlots = slots.filter(slot => slot.available);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Seleziona orario per {date.toLocaleDateString('it-IT', { 
            weekday: 'long', 
            day: 'numeric', 
            month: 'long' 
          })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {availableSlots.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            Nessuno slot disponibile per questa data
          </p>
        ) : (
          <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
            {availableSlots.map((slot, idx) => {
              const time = new Date(slot.datetime).toLocaleTimeString('it-IT', {
                hour: '2-digit',
                minute: '2-digit',
              });
              const isSelected = slot.datetime === selectedSlot;

              return (
                <Button
                  key={idx}
                  variant={isSelected ? 'default' : 'outline'}
                  className="h-auto py-3"
                  onClick={() => onSlotSelect(slot.datetime, slot.duration_minutes)}
                >
                  <div className="text-center">
                    <div className="font-semibold">{time}</div>
                    <div className="text-xs opacity-75">{slot.duration_minutes}min</div>
                  </div>
                </Button>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
