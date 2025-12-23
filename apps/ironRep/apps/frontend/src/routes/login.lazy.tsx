import { createLazyFileRoute } from "@tanstack/react-router";
import { LoginForm } from "../features/auth/LoginForm";
import { OptimizedAvatar } from "../components/ui/OptimizedImage";

export const Route = createLazyFileRoute("/login")({
  component: LoginPage,
});

function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4 safe-all">
      <div className="w-full max-w-md">
        <div className="flex justify-center mb-8">
          <OptimizedAvatar
            src="/pwa-192x192.png"
            alt="IronRep Logo"
            size="xl"
            priority
            className="shadow-lg"
          />
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
