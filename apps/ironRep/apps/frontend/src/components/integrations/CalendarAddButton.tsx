/**
 * CalendarAddButton - Add workout to Google Calendar
 */
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Calendar, Loader2, Check, ExternalLink } from "lucide-react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";
 import { authToken } from "../../lib/authToken";
import { getApiUrl } from "../../config/api.config";

async function checkGoogleStatus(): Promise<{ connected: boolean }> {
  const token = authToken.get();
  const response = await fetch(getApiUrl("/google/auth/status"), { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) return { connected: false };
  return response.json();
}

interface CalendarEventRequest { title: string; description: string; start_time: string; duration_minutes: number; exercises?: string[]; }
interface CalendarEventResponse { event_id: string; html_link: string; summary: string; }

async function createCalendarEvent(event: CalendarEventRequest): Promise<CalendarEventResponse> {
  const token = authToken.get();
  const response = await fetch(getApiUrl("/google/calendar/events"), {
    method: "POST", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify(event),
  });
  if (!response.ok) throw new Error("Failed to create event");
  return response.json();
}

interface Props { title: string; description: string; startTime: Date; durationMinutes?: number; exercises?: string[]; variant?: "button" | "icon"; className?: string; }

export function CalendarAddButton({ title, description, startTime, durationMinutes = 60, exercises, variant = "button", className }: Props) {
  const [createdEvent, setCreatedEvent] = useState<CalendarEventResponse | null>(null);
  const { data: status } = useQuery({ queryKey: ["google-status"], queryFn: checkGoogleStatus, staleTime: 60_000 });

  const mutation = useMutation({
    mutationFn: createCalendarEvent,
    onSuccess: (data) => { setCreatedEvent(data); hapticFeedback.notification("success"); },
    onError: () => hapticFeedback.notification("error"),
  });

  const handleClick = () => {
    if (!status?.connected) return;
    hapticFeedback.selection();
    mutation.mutate({ title, description, start_time: startTime.toISOString(), duration_minutes: durationMinutes, exercises });
  };

  if (!status?.connected) return null;

  if (createdEvent) {
    return (
      <a href={createdEvent.html_link} target="_blank" rel="noopener noreferrer" className={cn("flex items-center gap-2 px-4 py-2 rounded-xl font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 hover:bg-green-200", className)}>
        <Check className="w-4 h-4" /><span>Aggiunto</span><ExternalLink className="w-3 h-3" />
      </a>
    );
  }

  if (variant === "icon") {
    return (
      <button onClick={handleClick} disabled={mutation.isPending} className={cn("p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 hover:bg-purple-200 active:scale-95 touch-manipulation min-h-[44px] min-w-[44px]", mutation.isPending && "opacity-50", className)} title="Aggiungi a Calendar">
        {mutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Calendar className="w-5 h-5" />}
      </button>
    );
  }

  return (
    <button onClick={handleClick} disabled={mutation.isPending} className={cn("flex items-center gap-2 px-4 py-2 rounded-xl font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 hover:bg-purple-200 active:scale-95 touch-manipulation min-h-[44px]", mutation.isPending && "opacity-50", className)}>
      {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Calendar className="w-4 h-4" />}
      <span>Aggiungi a Calendar</span>
    </button>
  );
}

export default CalendarAddButton;
