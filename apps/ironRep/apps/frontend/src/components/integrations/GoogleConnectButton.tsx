/**
 * GoogleConnectButton - OAuth connection for Google Calendar & YouTube
 */
import { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Check, X } from "lucide-react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";
 import { authToken } from "../../lib/authToken";
import { getApiUrl } from "../../config/api.config";

async function getGoogleAuthUrl(): Promise<{ authorization_url: string }> {
  const token = authToken.get();
  const response = await fetch(getApiUrl("/google/auth/url"), { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) throw new Error("Failed to get auth URL");
  return response.json();
}

async function getGoogleStatus(): Promise<{ connected: boolean; google_email?: string; scopes?: string[]; calendar_sync_enabled?: boolean }> {
  const token = authToken.get();
  const response = await fetch(getApiUrl("/google/auth/status"), { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) throw new Error("Failed to get status");
  return response.json();
}

async function exchangeCode(code: string): Promise<{ success: boolean; google_email?: string }> {
  const token = authToken.get();
  const response = await fetch(getApiUrl("/google/auth/callback"), {
    method: "POST", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!response.ok) throw new Error("Token exchange failed");
  return response.json();
}

async function disconnectGoogle(): Promise<void> {
  const token = authToken.get();
  const response = await fetch(getApiUrl("/google/auth/disconnect"), { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) throw new Error("Disconnect failed");
}

export function GoogleConnectButton() {
  const queryClient = useQueryClient();
  const [isConnecting, setIsConnecting] = useState(false);
  const { data: status, isLoading } = useQuery({ queryKey: ["google-status"], queryFn: getGoogleStatus, staleTime: 60_000 });

  const exchangeMutation = useMutation({
    mutationFn: exchangeCode,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["google-status"] }); setIsConnecting(false); hapticFeedback.notification("success"); },
    onError: () => { setIsConnecting(false); hapticFeedback.notification("error"); },
  });

  const disconnectMutation = useMutation({
    mutationFn: disconnectGoogle,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["google-status"] }); hapticFeedback.notification("success"); },
  });

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === "google-oauth-callback" && event.data?.code) exchangeMutation.mutate(event.data.code);
    };
    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [exchangeMutation]);

  const handleConnect = async () => {
    setIsConnecting(true);
    hapticFeedback.selection();
    try {
      const { authorization_url } = await getGoogleAuthUrl();
      const popup = window.open(authorization_url, "google-oauth", `width=500,height=600,left=${window.screenX + 200},top=${window.screenY + 100}`);
      if (!popup) { window.location.href = authorization_url; return; }
      const poll = setInterval(() => { if (popup.closed) { clearInterval(poll); setIsConnecting(false); } }, 500);
    } catch { setIsConnecting(false); }
  };

  if (isLoading) return <div className="flex items-center gap-2 p-4 bg-secondary/50 rounded-xl"><Loader2 className="w-5 h-5 animate-spin" /><span className="text-sm text-muted-foreground">Verifica...</span></div>;

  if (status?.connected) {
    return (
      <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-xl border border-green-200 dark:border-green-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center"><Check className="w-5 h-5 text-green-600" /></div>
            <div><div className="font-semibold text-green-800 dark:text-green-200">Google Collegato</div><div className="text-sm text-green-600 dark:text-green-400">{status.google_email}</div></div>
          </div>
          <button onClick={() => disconnectMutation.mutate()} disabled={disconnectMutation.isPending} className="p-2 rounded-lg text-red-600 hover:bg-red-100 touch-manipulation min-h-[44px] min-w-[44px]">
            {disconnectMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <X className="w-5 h-5" />}
          </button>
        </div>
      </div>
    );
  }

  return (
    <button onClick={handleConnect} disabled={isConnecting || exchangeMutation.isPending} className={cn("w-full flex items-center justify-center gap-3 p-4 rounded-xl font-semibold transition-all bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 hover:shadow-md active:scale-[0.98] touch-manipulation min-h-[56px]", (isConnecting || exchangeMutation.isPending) && "opacity-70 cursor-not-allowed")}>
      {isConnecting || exchangeMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : (
        <svg className="w-5 h-5" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
      )}
      <span>{isConnecting || exchangeMutation.isPending ? "Connessione..." : "Collega Google Account"}</span>
    </button>
  );
}

export default GoogleConnectButton;
