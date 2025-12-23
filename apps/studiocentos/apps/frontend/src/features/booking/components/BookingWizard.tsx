/**
 * BookingWizard - Wizard completo multi-step per prenotazione
 */

import { useState } from 'react';
import { ServiceSelector } from './ServiceSelector';
import { CalendarView } from './CalendarView';
import { BookingForm } from './BookingForm';
import { BookingConfirmation } from './BookingConfirmation';
import type { ServiceType, Booking } from '../types/booking.types';

type WizardStep = 'service' | 'calendar' | 'form' | 'confirmation';

export function BookingWizard() {
  const [currentStep, setCurrentStep] = useState<WizardStep>('service');
  const [selectedService, setSelectedService] = useState<ServiceType>();
  const [selectedDatetime, setSelectedDatetime] = useState<string>();
  const [selectedDuration, setSelectedDuration] = useState<number>(30);
  const [confirmedBooking, setConfirmedBooking] = useState<Booking>();

  const handleServiceSelect = (service: ServiceType) => {
    setSelectedService(service);
    setCurrentStep('calendar');
  };

  const handleSlotSelect = (datetime: string, duration: number) => {
    setSelectedDatetime(datetime);
    setSelectedDuration(duration);
    setCurrentStep('form');
  };

  const handleBookingSuccess = (booking: Booking) => {
    setConfirmedBooking(booking);
    setCurrentStep('confirmation');
  };

  const handleReset = () => {
    setCurrentStep('service');
    setSelectedService(undefined);
    setSelectedDatetime(undefined);
    setConfirmedBooking(undefined);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Progress indicator */}
      <div className="flex items-center justify-center gap-2 mb-8">
        {['service', 'calendar', 'form', 'confirmation'].map((step, idx) => (
          <div key={step} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                currentStep === step
                  ? 'bg-gold text-white'
                  : idx < ['service', 'calendar', 'form', 'confirmation'].indexOf(currentStep)
                  ? 'bg-gold text-white'
                  : 'bg-gray-200 text-gray-500'
              }`}
            >
              {idx + 1}
            </div>
            {idx < 3 && <div className="w-12 h-0.5 bg-gray-200" />}
          </div>
        ))}
      </div>

      {/* Step content */}
      {currentStep === 'service' && (
        <ServiceSelector
          selectedService={selectedService}
          onServiceSelect={handleServiceSelect}
        />
      )}

      {currentStep === 'calendar' && (
        <CalendarView
          serviceType={selectedService}
          onSlotSelect={handleSlotSelect}
        />
      )}

      {currentStep === 'form' && (
        <BookingForm
          selectedDatetime={selectedDatetime}
          selectedDuration={selectedDuration}
          onSuccess={(booking) => {
            // Riceve la booking reale dalla API
            handleBookingSuccess(booking);
          }}
          onCancel={() => setCurrentStep('calendar')}
        />
      )}

      {currentStep === 'confirmation' && confirmedBooking && (
        <BookingConfirmation
          booking={confirmedBooking}
          onClose={handleReset}
        />
      )}
    </div>
  );
}
