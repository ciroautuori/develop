import { useState } from "react";
import { useNavigate, Link } from "@tanstack/react-router";
import { authApi } from "../../lib/api";
import { Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";

export function RegisterForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    hapticFeedback.impact("medium");

    try {
      await authApi.register({
        email,
        password,
        name,
      });
      hapticFeedback.notification("success");
      navigate({ to: "/login" });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(
        error.response?.data?.detail || "Errore durante la registrazione. Riprova."
      );
      hapticFeedback.notification("error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 space-y-6 bg-card rounded-2xl shadow-xl border">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Crea Account</h2>
        <p className="text-base text-muted-foreground">
          Inizia il tuo percorso di recupero
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="name" className="text-base font-medium">
            Nome Completo
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={cn(
              "w-full min-h-[48px] px-4 py-3 text-[16px] bg-secondary/50 border rounded-xl",
              "focus:ring-2 focus:ring-primary/20 focus:outline-none focus:border-primary",
              "disabled:opacity-50 transition-all placeholder:text-muted-foreground"
            )}
            placeholder="Mario Rossi"
            required
            autoComplete="name"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="text-base font-medium">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={cn(
              "w-full min-h-[48px] px-4 py-3 text-[16px] bg-secondary/50 border rounded-xl",
              "focus:ring-2 focus:ring-primary/20 focus:outline-none focus:border-primary",
              "disabled:opacity-50 transition-all placeholder:text-muted-foreground"
            )}
            placeholder="tua@email.com"
            required
            autoComplete="email"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="text-base font-medium">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={cn(
              "w-full min-h-[48px] px-4 py-3 text-[16px] bg-secondary/50 border rounded-xl",
              "focus:ring-2 focus:ring-primary/20 focus:outline-none focus:border-primary",
              "disabled:opacity-50 transition-all placeholder:text-muted-foreground"
            )}
            placeholder="Minimo 6 caratteri"
            required
            minLength={6}
            autoComplete="new-password"
          />
        </div>

        {error && (
          <div className="p-4 text-base text-destructive bg-destructive/10 rounded-xl border border-destructive/20">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full h-12 flex items-center justify-center bg-primary text-primary-foreground rounded-xl font-semibold transition-transform active:scale-[0.98] touch-manipulation disabled:opacity-50 disabled:pointer-events-none shadow-lg"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Registrazione...
            </>
          ) : (
            "Registrati"
          )}
        </button>
      </form>

      <div className="text-center">
        <span className="text-muted-foreground">Hai già un account? </span>
        <Link
          to="/login"
          className="font-semibold text-primary active:text-primary/80 transition-colors touch-manipulation"
        >
          Accedi
        </Link>
      </div>
    </div>
  );
}
