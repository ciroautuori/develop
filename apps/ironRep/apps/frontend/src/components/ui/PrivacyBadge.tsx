import { ShieldCheck } from "lucide-react";
import { cn } from "../../lib/utils";

export function PrivacyBadge({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-1.5 text-[10px] text-muted-foreground/60 px-2 py-1 bg-secondary/20 rounded-full", className)}>
      <ShieldCheck className="h-3 w-3" />
      <span className="uppercase tracking-widest font-semibold">HIPAA Compliant & Secure</span>
    </div>
  );
}
