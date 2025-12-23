/**
 * Modal - Compound Component Pattern
 *
 * Production-ready modal with:
 * - Compound component pattern for flexible composition
 * - Swipe-down to dismiss on mobile
 * - Focus trap with keyboard navigation
 * - Backdrop click to close (configurable)
 * - Smooth slide-up animation from bottom on mobile
 * - Accessibility (ARIA, focus management)
 *
 * @example
 * ```tsx
 * <Modal open={isOpen} onOpenChange={setIsOpen}>
 *   <Modal.Header>
 *     <Modal.Title>Titolo Modal</Modal.Title>
 *     <Modal.Description>Descrizione opzionale</Modal.Description>
 *   </Modal.Header>
 *   <Modal.Body>
 *     <p>Contenuto del modal...</p>
 *   </Modal.Body>
 *   <Modal.Footer>
 *     <Button onClick={handleSave}>Salva</Button>
 *     <Button variant="outline" onClick={() => setIsOpen(false)}>Annulla</Button>
 *   </Modal.Footer>
 * </Modal>
 * ```
 */

import * as React from "react";
import { X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { PanInfo } from "framer-motion";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";

interface ModalContextValue {
  onClose: () => void;
}

const ModalContext = React.createContext<ModalContextValue | null>(null);

function useModalContext() {
  const context = React.useContext(ModalContext);
  if (!context) {
    throw new Error("Modal compound components must be used within <Modal>");
  }
  return context;
}

// ============================================================================
// ROOT MODAL
// ============================================================================

export interface ModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
  /** Allow closing via backdrop click */
  closeOnBackdrop?: boolean;
  /** Custom z-index */
  zIndex?: number;
}

export function Modal({
  open,
  onOpenChange,
  children,
  closeOnBackdrop = true,
  zIndex = 50,
}: ModalProps) {
  const modalRef = React.useRef<HTMLDivElement>(null);

  const handleClose = React.useCallback(() => {
    hapticFeedback.impact('light');
    onOpenChange(false);
  }, [onOpenChange]);

  // Keyboard navigation
  React.useEffect(() => {
    if (!open) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        handleClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, handleClose]);

  // Focus trap - capture focus when modal opens
  React.useEffect(() => {
    if (!open) return;

    const modalElement = modalRef.current;
    if (!modalElement) return;

    const focusableElements = modalElement.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus first element
    firstElement?.focus();

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          lastElement?.focus();
          e.preventDefault();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          firstElement?.focus();
          e.preventDefault();
        }
      }
    };

    document.addEventListener("keydown", handleTabKey);
    return () => document.removeEventListener("keydown", handleTabKey);
  }, [open]);

  // Prevent body scroll when modal is open
  React.useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  const contextValue = React.useMemo(() => ({ onClose: handleClose }), [handleClose]);

  return (
    <ModalContext.Provider value={contextValue}>
      <AnimatePresence>
        {open && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={closeOnBackdrop ? handleClose : undefined}
              className={cn("fixed inset-0 bg-black/50 backdrop-blur-sm")}
              style={{ zIndex }}
              aria-hidden="true"
            />

            {/* Modal Content */}
            <div
              className={cn(
                "fixed inset-0 flex items-end sm:items-center justify-center pointer-events-none"
              )}
              style={{ zIndex: zIndex + 1 }}
            >
              <ModalContent ref={modalRef} onClose={handleClose}>
                {children}
              </ModalContent>
            </div>
          </>
        )}
      </AnimatePresence>
    </ModalContext.Provider>
  );
}

// ============================================================================
// MODAL CONTENT (with swipe gesture)
// ============================================================================

interface ModalContentProps {
  children: React.ReactNode;
  onClose: () => void;
}

const ModalContent = React.forwardRef<HTMLDivElement, ModalContentProps>(
  ({ children, onClose }, ref) => {
    const [isDragging, setIsDragging] = React.useState(false);

    function handleDragEnd(_: unknown, info: PanInfo) {
      setIsDragging(false);

      // Swipe down threshold for mobile
      if (info.offset.y > 100) {
        hapticFeedback.impact('medium');
        onClose();
      }
    }

    return (
      <motion.div
        ref={ref}
        drag="y"
        dragConstraints={{ top: 0, bottom: 0 }}
        dragElastic={{ top: 0, bottom: 0.2 }}
        onDragStart={() => setIsDragging(true)}
        onDragEnd={handleDragEnd}
        initial={{ opacity: 0, y: 100, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 100, scale: 0.95 }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
        className={cn(
          "relative w-full max-w-lg bg-background rounded-t-3xl sm:rounded-2xl shadow-2xl pointer-events-auto mx-4 sm:mx-auto",
          "max-h-[90vh] sm:max-h-[85vh] flex flex-col",
          isDragging && "cursor-grabbing"
        )}
        role="dialog"
        aria-modal="true"
      >
        {/* Swipe indicator (mobile only) */}
        <div className="sm:hidden flex justify-center pt-3 pb-2">
          <div className="w-12 h-1 bg-muted-foreground/30 rounded-full" />
        </div>

        {children}
      </motion.div>
    );
  }
);

ModalContent.displayName = "ModalContent";

// ============================================================================
// MODAL HEADER
// ============================================================================

export interface ModalHeaderProps {
  children: React.ReactNode;
  showCloseButton?: boolean;
  className?: string;
}

function ModalHeader({
  children,
  showCloseButton = true,
  className,
}: ModalHeaderProps) {
  const { onClose } = useModalContext();

  return (
    <div
      className={cn(
        "relative flex items-start justify-between px-6 pt-4 pb-3 border-b shrink-0",
        className
      )}
    >
      <div className="flex-1 pr-8">{children}</div>
      {showCloseButton && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-accent transition-colors active:scale-90 touch-manipulation"
          aria-label="Chiudi"
        >
          <X className="w-5 h-5 text-muted-foreground" />
        </button>
      )}
    </div>
  );
}

Modal.Header = ModalHeader;

// ============================================================================
// MODAL TITLE
// ============================================================================

export interface ModalTitleProps {
  children: React.ReactNode;
  className?: string;
}

function ModalTitle({ children, className }: ModalTitleProps) {
  return (
    <h2
      className={cn("text-xl font-bold text-foreground leading-tight", className)}
      id="modal-title"
    >
      {children}
    </h2>
  );
}

Modal.Title = ModalTitle;

// ============================================================================
// MODAL DESCRIPTION
// ============================================================================

export interface ModalDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

function ModalDescription({ children, className }: ModalDescriptionProps) {
  return (
    <p
      className={cn("text-sm text-muted-foreground mt-1", className)}
      id="modal-description"
    >
      {children}
    </p>
  );
}

Modal.Description = ModalDescription;

// ============================================================================
// MODAL BODY
// ============================================================================

export interface ModalBodyProps {
  children: React.ReactNode;
  className?: string;
}

function ModalBody({ children, className }: ModalBodyProps) {
  return (
    <div
      className={cn(
        "flex-1 overflow-y-auto overscroll-contain px-6 py-4",
        className
      )}
    >
      {children}
    </div>
  );
}

Modal.Body = ModalBody;

// ============================================================================
// MODAL FOOTER
// ============================================================================

export interface ModalFooterProps {
  children: React.ReactNode;
  className?: string;
}

function ModalFooter({ children, className }: ModalFooterProps) {
  return (
    <div
      className={cn(
        "flex items-center justify-end gap-3 px-6 py-4 border-t bg-muted/30 shrink-0",
        "rounded-b-3xl sm:rounded-b-2xl",
        className
      )}
    >
      {children}
    </div>
  );
}

Modal.Footer = ModalFooter;

// ============================================================================
// Export
// ============================================================================

export default Modal;
