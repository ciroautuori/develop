/**
 * WizardChat v2.0 - Intelligent Quick Replies
 * Quick replies are now fetched from backend based on current phase
 * Build: 2024-11-27
 */
import type React from "react";
import { useState, useEffect } from "react";
import {
  Send, Loader2, Sparkles, CheckCircle2, ArrowRight,
  Apple, Activity, Calendar, Heart
} from "lucide-react";
import { wizardApi } from "../../lib/api";
import { logger } from "../../lib/logger";
import { hapticFeedback } from "../../lib/haptics";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface AgentConfig {
  medical_mode?: string;
  coach_mode?: string;
  nutrition_mode?: string;
  sport_type?: string;
  has_injury?: boolean;
}

interface InitializationResult {
  success: boolean;
  agent_config?: AgentConfig;
  agents_available?: string[];
  medical_assessment?: Record<string, unknown> & { mode?: string };
  initial_workout?: Record<string, unknown> & { sport_type?: string };
  nutrition_plan?: Record<string, unknown> & { mode?: string };
  errors?: string[];
}

interface WizardChatProps {
  onComplete?: (data: Record<string, unknown>) => void;
  initialBiometrics?: BiometricsData | null;
  initialContext?: {
    trainingGoals?: Record<string, unknown> | null;
    lifestyle?: Record<string, unknown> | null;
    nutritionGoals?: Record<string, unknown> | null;
  };
  mode?: "chat" | "summary"; // NEW: Support summary mode
}

interface BiometricsData {
  age: number;
  weight_kg: number;
  height_cm: number;
  sex: string;
}

// Quick replies now come from backend based on current phase
const WIZARD_VERSION = "2.0.1";

export function WizardChat({ onComplete, initialBiometrics, initialContext, mode = "chat" }: WizardChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [collectedData, setCollectedData] = useState<Record<string, unknown>>({});
  const [agentConfig, setAgentConfig] = useState<AgentConfig>({});
  const [initialization, setInitialization] = useState<InitializationResult | null>(null);
  const [currentPhase, setCurrentPhase] = useState<string>("greeting");
  const [suggestedReplies, setSuggestedReplies] = useState<Array<{ label: string; value: string; icon?: string; color: string }>>([]);

  // Log version on mount for debugging cache issues
  useEffect(() => {
    logger.info(`WizardChat ${WIZARD_VERSION} loaded - intelligent replies enabled`);
  }, []);



  // Start wizard on mount
  useEffect(() => {
    startWizard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Suggested replies now come from backend - phase-aware and intelligent

  const startWizard = async () => {
    setIsLoading(true);
    try {
      // Pass initial biometrics AND collected inline data to give context to RAG immediately
      const contextData = {
        ...initialBiometrics,
        ...(initialContext || {}),
      };
      const response = await wizardApi.start(
        Object.keys(contextData).length > 0 ? contextData : undefined,
        { googleSyncFields: (initialContext as any)?.googleSyncFields || [] }
      );

      if (response.success) {
        setSessionId(response.session_id);
        setCurrentPhase(response.phase || "greeting");
        setMessages([
          {
            id: "1",
            role: "assistant",
            content: response.message,
            timestamp: new Date(),
          },
        ]);
        // Load suggested replies from backend for first message
        if (response.suggested_replies && response.suggested_replies.length > 0) {
          setSuggestedReplies(response.suggested_replies);
        }
      }
    } catch (error) {
      logger.error("Failed to start wizard", { error });
      setMessages([
        {
          id: "1",
          role: "assistant",
          content: "Ciao! 👋 Sono qui per personalizzare la tua esperienza. Cosa ti porta su IronRep oggi?",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (messageText?: string) => {
    const text = messageText || input.trim();
    if (!text || !sessionId || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSuggestedReplies([]); // Clear replies while loading
    setIsLoading(true);

    try {
      const response = await wizardApi.sendMessage(sessionId, text);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.message,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setCurrentPhase(response.phase || currentPhase);

      // Update collected data
      if (response.extracted_data) {
        setCollectedData((prev) => ({ ...prev, ...response.extracted_data }));
      }

      // Update agent config from response
      if (response.agent_config) {
        setAgentConfig((prev) => ({ ...prev, ...response.agent_config }));
      }

      // Use suggested_replies from backend (intelligent, phase-based)
      if (response.suggested_replies && response.suggested_replies.length > 0) {
        setSuggestedReplies(response.suggested_replies);
      } else {
        setSuggestedReplies([]);
      }

      if (response.completed) {
        setIsComplete(true);
        setCollectedData(response.collected_data || {});
        setAgentConfig(response.agent_config || {});
        setSuggestedReplies([]); // No replies when complete

        if (response.initialization) {
          setInitialization(response.initialization as InitializationResult);
          logger.info("Agents initialized", { initialization: response.initialization });
        }

        // Notify parent (WizardOrchestrator) that chat phase is complete
        if (onComplete) {
          hapticFeedback.notification("success");
          onComplete({
            ...(response.collected_data || {}),
            agent_config: response.agent_config || {}
          });
        }
      }
    } catch (error) {
      logger.error("Failed to send message", { error });
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Mi dispiace, ho avuto un problema. Puoi ripetere?",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickReply = (value: string, updateConfig?: Partial<AgentConfig>) => {
    hapticFeedback.selection();
    if (updateConfig) {
      setAgentConfig((prev) => ({ ...prev, ...updateConfig }));
    }
    sendMessage(value);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleComplete = () => {
    // Notify orchestrator instead of navigating directly
    if (onComplete) {
      hapticFeedback.notification("success");
      onComplete({
        ...collectedData,
        agent_config: agentConfig
      });
    }
  };

  const colorClasses: Record<string, string> = {
    red: "bg-red-50 hover:bg-red-100 border-red-200 text-red-700",
    green: "bg-green-50 hover:bg-green-100 border-green-200 text-green-700",
    blue: "bg-blue-50 hover:bg-blue-100 border-blue-200 text-blue-700",
    orange: "bg-orange-50 hover:bg-orange-100 border-orange-200 text-orange-700",
    amber: "bg-amber-50 hover:bg-amber-100 border-amber-200 text-amber-700",
    purple: "bg-purple-50 hover:bg-purple-100 border-purple-200 text-purple-700",
    gray: "bg-gray-50 hover:bg-gray-100 border-gray-200 text-gray-700",
  };

  // Helper for injury pill styling
  const getInjuryPillClass = () => {
    return agentConfig.has_injury ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700';
  };

  // === RENDER for SUMMARY MODE ===
  if (mode === "summary") {
    const summaryMessage = messages.find(m => m.role === "assistant")?.content || "Generazione riepilogo...";

    return (
      <div className="flex flex-col h-[100dvh] min-h-[100dvh] bg-background p-4 sm:p-6">
        <div className="flex-1 flex flex-col items-center justify-center max-w-lg mx-auto w-full">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-6">
            <Sparkles className="w-8 h-8 text-primary animate-pulse" />
          </div>

          <h2 className="text-2xl font-bold mb-2 text-center">Riepilogo Profilo</h2>
          <p className="text-muted-foreground text-center mb-8">Ecco cosa abbiamo raccolto. Confermi?</p>

          <div className="bg-card border rounded-2xl p-6 w-full shadow-sm mb-8">
            {isLoading && messages.length === 0 ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Analisi contesto...</span>
              </div>
            ) : (
              <p className="whitespace-pre-wrap text-base leading-relaxed">{summaryMessage}</p>
            )}
          </div>

          <div className="w-full space-y-3">
            <button
              onClick={() => sendMessage("Tutto corretto, procedi pure.")}
              disabled={isLoading}
              className="w-full bg-primary text-primary-foreground h-14 rounded-xl font-bold text-lg hover:bg-primary/90 transition-all active:scale-[0.98] flex items-center justify-center gap-2 shadow-lg shadow-primary/25"
            >
              {isLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <CheckCircle2 className="w-6 h-6" />}
              Conferma e Genera Piano
            </button>

            <button
              onClick={() => alert("Funzione modifica in arrivo! Per ora usa la chat completa.")}
              className="w-full bg-secondary/50 text-foreground h-12 rounded-xl font-medium hover:bg-secondary transition-colors"
            >
              Modifica dettagli
            </button>
          </div>
        </div>
      </div>
    );
  }

  // === RENDER for CHAT MODE (Classic) ===
  return (
    <div className="flex flex-col h-[100dvh] min-h-[100dvh] bg-gradient-to-b from-background to-secondary/10 overflow-y-auto">
      {/* Header with selections */}
      <div className="bg-primary/10 border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-bold">Configura IronRep</h1>
              <p className="text-xs text-muted-foreground">Rispondi per personalizzare la tua esperienza</p>
            </div>
          </div>
        </div>

        {/* Current selections - compact pills */}
        {(agentConfig.sport_type || agentConfig.has_injury !== undefined || agentConfig.nutrition_mode) && (
          <div className="mt-3 flex gap-2 overflow-x-auto no-scrollbar md:flex-wrap md:overflow-visible">
            {agentConfig.has_injury !== undefined && (
              <span className={"px-2 py-1 rounded-full text-xs flex items-center gap-1 " + getInjuryPillClass()}>
                {agentConfig.has_injury ? <Heart className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                {agentConfig.has_injury ? 'Recovery' : 'Wellness'}
              </span>
            )}
            {agentConfig.sport_type && (
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs flex items-center gap-1">
                <Activity className="w-3 h-3" />
                {agentConfig.sport_type.replace('_', ' ')}
              </span>
            )}
            {agentConfig.nutrition_mode && agentConfig.nutrition_mode !== 'disabled' && (
              <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded-full text-xs flex items-center gap-1">
                <Apple className="w-3 h-3" />
                {agentConfig.nutrition_mode === 'full_diet_plan' ? 'Dieta' :
                  agentConfig.nutrition_mode === 'recipes_only' ? 'Ricette' : 'Tips'}
              </span>
            )}
            {collectedData.training_days && (
              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {String(collectedData.training_days)}gg/sett
              </span>
            )}
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 p-3 sm:p-4 flex flex-col gap-3 overflow-y-auto">


        {messages.map((message) => (
          <div
            key={message.id}
            className={"flex " + (message.role === "user" ? "justify-end" : "justify-start")}
          >
            <div
              className={"max-w-[90%] sm:max-w-[85%] rounded-2xl px-3 sm:px-4 py-2 sm:py-2.5 " + (
                message.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-card border shadow-sm"
              )}
            >
              <p
                className={
                  "whitespace-pre-wrap text-sm " +
                  (message.role === "assistant" ? "line-clamp-6 md:line-clamp-none" : "")
                }
              >
                {message.content}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-card border rounded-2xl px-4 py-3 shadow-sm">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
            </div>
          </div>
        )}
      </div>

      {/* Quick Reply Buttons + Input Area (BOTH visible) */}
      <div className="p-3 sm:p-4 border-t bg-background safe-area-bottom flex flex-col gap-3">
        {isComplete ? (
          <button
            onClick={handleComplete}
            className="w-full bg-green-600 hover:bg-green-700 text-white py-4 rounded-xl font-semibold flex items-center justify-center gap-2 transition-colors touch-manipulation"
          >
            Inizia il tuo percorso
            <ArrowRight className="w-5 h-5" />
          </button>
        ) : (
          <>
            {/* Quick Reply Buttons */}
            {suggestedReplies.length > 0 && !isLoading && (
              <div className="flex gap-2 overflow-x-auto no-scrollbar animate-in slide-in-from-bottom-4 duration-300">
                {suggestedReplies.map((reply) => (
                  <button
                    key={reply.value}
                    onClick={() => handleQuickReply(reply.value)}
                    className={
                      "shrink-0 flex items-center gap-2 px-4 py-3 rounded-xl border shadow-sm active:scale-95 transition-all touch-manipulation " +
                      (colorClasses[reply.color] || colorClasses.gray)
                    }
                  >
                    <span className="text-sm font-bold">{reply.label}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Text Input (always visible) */}
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Oppure scrivi la tua risposta..."
                disabled={isLoading || !sessionId}
                className="flex-1 px-3 sm:px-4 py-3 rounded-xl border bg-background focus:ring-2 focus:ring-primary/20 outline-none transition-all disabled:opacity-50 text-[16px] min-h-[48px]"
              />
              <button
                onClick={() => sendMessage()}
                disabled={!input.trim() || isLoading || !sessionId}
                className="px-4 py-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation min-h-[48px]"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default WizardChat;
