import { useState, useCallback } from "react";

export function useChatSession() {
  const [sessionId, setSessionId] = useState<string | null>(null);

  const updateSession = useCallback((newSessionId: string) => {
    setSessionId(newSessionId);
  }, []);

  const resetSession = useCallback(() => {
    setSessionId(null);
  }, []);

  return {
    sessionId,
    updateSession,
    resetSession,
  };
}
