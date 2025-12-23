import { useEffect, useRef } from "react";
import { X } from "lucide-react";
import { cn } from "../../../lib/utils";

interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  side?: "bottom" | "right" | "left";
  title?: string;
  showHandle?: boolean;
}

export function Sheet({
  isOpen,
  onClose,
  children,
  side = "bottom",
  title,
  showHandle = true,
}: SheetProps) {
  const sheetRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);
  const currentY = useRef(0);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  // Handle swipe to close for bottom sheet
  const handleTouchStart = (e: React.TouchEvent) => {
    if (side !== "bottom") return;
    startY.current = e.touches[0].clientY;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (side !== "bottom" || !sheetRef.current) return;
    currentY.current = e.touches[0].clientY;
    const diff = currentY.current - startY.current;
    if (diff > 0) {
      sheetRef.current.style.transform = `translateY(${diff}px)`;
    }
  };

  const handleTouchEnd = () => {
    if (side !== "bottom" || !sheetRef.current) return;
    const diff = currentY.current - startY.current;
    if (diff > 100) {
      onClose();
    }
    sheetRef.current.style.transform = "";
    startY.current = 0;
    currentY.current = 0;
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-50 animate-fade-in"
        onClick={onClose}
      />

      {/* Sheet */}
      <div
        ref={sheetRef}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        className={cn(
          "fixed z-50 bg-background border-border shadow-2xl animate-slide-up",
          {
            "inset-x-0 bottom-0 rounded-t-3xl border-t max-h-[90vh]": side === "bottom",
            "inset-y-0 right-0 w-80 border-l": side === "right",
            "inset-y-0 left-0 w-80 border-r": side === "left",
          }
        )}
      >
        {/* Handle for bottom sheet */}
        {side === "bottom" && showHandle && (
          <div className="flex justify-center pt-3 pb-2">
            <div className="w-10 h-1 bg-muted-foreground/30 rounded-full" />
          </div>
        )}

        {/* Header */}
        {title && (
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <h2 className="text-lg font-semibold">{title}</h2>
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-accent transition-colors"
            >
              <X size={20} />
            </button>
          </div>
        )}

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-60px)] overscroll-contain">
          {children}
        </div>
      </div>
    </>
  );
}
