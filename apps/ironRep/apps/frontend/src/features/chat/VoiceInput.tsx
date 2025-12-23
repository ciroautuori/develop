import { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";
import { logger } from "../../lib/logger";

// Web Speech API type declarations (not in standard TS lib)
interface SpeechRecognitionResult {
  readonly isFinal: boolean;
  readonly length: number;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}

interface SpeechRecognitionResultList {
  readonly length: number;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string;
  readonly message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onstart: ((this: SpeechRecognition, ev: Event) => void) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => void) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => void) | null;
  onend: ((this: SpeechRecognition, ev: Event) => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  onError?: (error: string) => void;
}

export function VoiceInput({ onTranscript, onError }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    // Check if browser supports Web Speech API
    if (
      !("webkitSpeechRecognition" in window) &&
      !("SpeechRecognition" in window)
    ) {
      onError?.("Il tuo browser non supporta il riconoscimento vocale.");
      return;
    }

    // Initialize Speech Recognition
    const SpeechRecognitionCtor =
      window.webkitSpeechRecognition || window.SpeechRecognition;
    const recognition = new SpeechRecognitionCtor();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "it-IT"; // Italian language

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript("");
      hapticFeedback.notification("success");
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPart + " ";
        } else {
          interimTranscript += transcriptPart;
        }
      }

      setTranscript(finalTranscript || interimTranscript);

      if (finalTranscript) {
        setIsProcessing(true);
        onTranscript(finalTranscript.trim());
        setTimeout(() => {
          setIsProcessing(false);
          setTranscript("");
        }, 500);
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      logger.error("Speech recognition error", { error: event.error });
      setIsListening(false);
      setIsProcessing(false);
      hapticFeedback.notification("error");

      const errorMessages: Record<string, string> = {
        "no-speech": "Nessun parlato rilevato. Riprova.",
        "audio-capture": "Microfono non disponibile.",
        "not-allowed": "Permesso microfono negato.",
        network: "Errore di rete. Controlla la connessione.",
      };

      const errorMessage =
        errorMessages[event.error] || "Errore nel riconoscimento vocale.";
      onError?.(errorMessage);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [onTranscript, onError]);

  const toggleListening = () => {
    hapticFeedback.impact("medium");
    if (!recognitionRef.current) {
      onError?.("Riconoscimento vocale non supportato dal browser.");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error("Error starting recognition:", error);
        onError?.("Errore nell'avvio del riconoscimento vocale.");
      }
    }
  };

  return (
    <div className="relative">
      <button
        onClick={toggleListening}
        disabled={isProcessing}
        className={cn(
          "p-2.5 md:p-4 rounded-full transition-all duration-200 active:scale-95 min-w-[44px] min-h-[44px] flex items-center justify-center",
          isListening
            ? "bg-red-500 hover:bg-red-600 text-white animate-pulse"
            : "bg-primary hover:bg-primary/90 text-primary-foreground",
          isProcessing && "opacity-50 cursor-not-allowed"
        )}
        title={
          isListening ? "Stop registrazione" : "Inizia registrazione vocale"
        }
        aria-label={
          isListening ? "Stop registrazione" : "Inizia registrazione vocale"
        }
      >
        {isProcessing ? (
          <Loader2 className="h-4 w-4 md:h-5 md:w-5 animate-spin" />
        ) : isListening ? (
          <MicOff className="h-4 w-4 md:h-5 md:w-5" />
        ) : (
          <Mic className="h-4 w-4 md:h-5 md:w-5" />
        )}
      </button>

      {/* Live Transcript Display */}
      {(isListening || transcript) && (
        <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-60 bg-popover border rounded-lg p-2.5 shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <div className="flex gap-1">
              <span className="w-1 h-4 bg-red-500 rounded-full animate-pulse"></span>
              <span className="w-1 h-4 bg-red-500 rounded-full animate-pulse delay-75"></span>
              <span className="w-1 h-4 bg-red-500 rounded-full animate-pulse delay-150"></span>
            </div>
            <span className="text-xs font-medium text-red-500">
              In ascolto...
            </span>
          </div>
          <p className="text-[13px] leading-relaxed text-foreground min-h-[36px]">
            {transcript || "Parla ora..."}
          </p>
        </div>
      )}
    </div>
  );
}
