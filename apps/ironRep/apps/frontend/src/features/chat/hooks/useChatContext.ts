import { useState, useEffect } from "react";
import { logger } from '../../../lib/logger';
import type { ChatConfig, ChatContextData } from "../types";

export function useChatContext(config: ChatConfig) {
  const [context, setContext] = useState<ChatContextData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadContext = async () => {
      try {
        setIsLoading(true);
        const data = await config.api.contextLoader();
        if (isMounted) {
          setContext(data);
        }
      } catch (error) {
        logger.error('Failed to load context', { error });
        if (isMounted) {
          setContext({});
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadContext();

    return () => {
      isMounted = false;
    };
  }, [config.type]); // Reload when chat type changes

  return {
    context,
    isLoading,
  };
}
