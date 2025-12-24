import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { useAuth } from "./AuthContext";
import { authApi } from "../../lib/api";
import { Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";

export function LoginForm() {
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("google_code");
    const state = params.get("state");
    if (!code) return;

    setError("");
    setIsLoading(true);
    authApi
      .googleExchangeCode({ code, state })
      .then((token) => {
        login(token.access_token);
        hapticFeedback.notification("success");
        window.location.href = "/";
      })
      .catch(() => {
        setError("Login Google non riuscito. Riprova.");
        hapticFeedback.notification("error");
      })
      .finally(() => {
        setIsLoading(false);
        setIsConnecting(false);
      });
  }, [login, navigate]);

  useEffect(() => {
    const handleMessage = async (event: MessageEvent) => {
      if (event.data?.type !== "google-oauth-callback" || !event.data?.code) return;

      setError("");
      setIsLoading(true);
      try {
        const token = await authApi.googleExchangeCode({
          code: String(event.data.code),
          state: event.data.state ? String(event.data.state) : undefined,
        });
        login(token.access_token);
        hapticFeedback.notification("success");
        window.location.href = "/";
      } catch {
        setError("Login Google non riuscito. Riprova.");
        hapticFeedback.notification("error");
      } finally {
        setIsLoading(false);
        setIsConnecting(false);
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [login, navigate]);

  const handleGoogleLogin = async () => {
    setError("");
    setIsConnecting(true);
    hapticFeedback.selection();
    try {
      const { authorization_url } = await authApi.googleAuthUrl();
      const popup = window.open(
        authorization_url,
        "google-oauth",
        `width=500,height=600,left=${window.screenX + 200},top=${window.screenY + 100}`
      );
      if (!popup) {
        window.location.href = authorization_url;
        return;
      }
      const poll = setInterval(() => {
        if (popup.closed) {
          clearInterval(poll);
          setIsConnecting(false);
        }
      }, 500);
    } catch {
      setIsConnecting(false);
      setError("Impossibile avviare login Google.");
      hapticFeedback.notification("error");
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 space-y-6 bg-card rounded-2xl shadow-xl border">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Bentornato</h2>
        <p className="text-base text-muted-foreground">
          Accedi con Google
        </p>
      </div>

      {error && (
        <div className="p-4 text-base text-destructive bg-destructive/10 rounded-xl border border-destructive/20">
          {error}
        </div>
      )}

      <button
        type="button"
        onClick={handleGoogleLogin}
        disabled={isConnecting || isLoading}
        className={cn(
          "w-full h-12 flex items-center justify-center bg-primary text-primary-foreground rounded-xl font-semibold transition-transform active:scale-[0.98] touch-manipulation shadow-lg",
          (isConnecting || isLoading) && "opacity-50 pointer-events-none"
        )}
      >
        {isConnecting || isLoading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Connessione...
          </>
        ) : (
          "Accedi con Google"
        )}
      </button>
    </div>
  );
}
