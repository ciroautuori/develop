import React, { useEffect, useRef, useState, createContext, useContext } from 'react';
import { cn } from '@/utils/cn';
import { X } from 'lucide-react';

// Context per gestire stato dialog
interface DialogContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const DialogContext = createContext<DialogContextType | undefined>(undefined);

const useDialogContext = () => {
  const context = useContext(DialogContext);
  if (!context) {
    throw new Error('Dialog components must be used within Dialog');
  }
  return context;
};

// Hook per gestire focus trap
const useFocusTrap = (isOpen: boolean, containerRef: React.RefObject<HTMLElement>) => {
  useEffect(() => {
    if (!isOpen || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const trapFocus = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement?.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement?.focus();
          }
        }
      }
    };

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    container.addEventListener('keydown', trapFocus);
    document.addEventListener('keydown', handleEscape);

    // Focus primo elemento al mount
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', trapFocus);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, containerRef]);
};

// Hook per prevenire scroll del body
const useBodyScrollLock = (isLocked: boolean) => {
  useEffect(() => {
    if (isLocked) {
      const originalStyle = window.getComputedStyle(document.body).overflow;
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = originalStyle;
      };
    }
  }, [isLocked]);
};

// Main Dialog component
interface DialogProps {
  children: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export const Dialog: React.FC<DialogProps> = ({
  children,
  open: controlledOpen,
  onOpenChange
}) => {
  const [internalOpen, setInternalOpen] = useState(false);
  
  const isControlled = controlledOpen !== undefined;
  const isOpen = isControlled ? controlledOpen : internalOpen;
  
  const setIsOpen = (open: boolean) => {
    if (isControlled) {
      onOpenChange?.(open);
    } else {
      setInternalOpen(open);
    }
  };

  return (
    <DialogContext.Provider value={{ isOpen, setIsOpen }}>
      {children}
    </DialogContext.Provider>
  );
};

// Trigger component
interface DialogTriggerProps {
  children: React.ReactNode;
  asChild?: boolean;
  className?: string;
}

export const DialogTrigger: React.FC<DialogTriggerProps> = ({
  children,
  asChild = false,
  className
}) => {
  const { setIsOpen } = useDialogContext();

  const handleClick = () => {
    setIsOpen(true);
  };

  if (asChild) {
    return React.cloneElement(children as React.ReactElement, {
      onClick: handleClick,
    });
  }

  return (
    <button
      onClick={handleClick}
      className={cn(
        'inline-flex items-center justify-center px-4 py-2 text-sm font-medium',
        'bg-iss-bordeaux-600 text-white rounded-md',
        'hover:bg-iss-bordeaux-700 focus:outline-none focus:ring-2 focus:ring-iss-bordeaux-500 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
    >
      {children}
    </button>
  );
};

// Portal component per renderizzare fuori dal DOM tree
interface PortalProps {
  children: React.ReactNode;
  container?: HTMLElement;
}

const Portal: React.FC<PortalProps> = ({ children, container = document.body }) => {
  const [mountNode, setMountNode] = useState<HTMLElement | null>(null);

  useEffect(() => {
    const node = document.createElement('div');
    node.setAttribute('data-dialog-portal', '');
    container.appendChild(node);
    setMountNode(node);

    return () => {
      if (container.contains(node)) {
        container.removeChild(node);
      }
    };
  }, [container]);

  if (!mountNode) return null;

  return React.createPortal(children, mountNode);
};

// Overlay component
interface DialogOverlayProps {
  className?: string;
}

export const DialogOverlay: React.FC<DialogOverlayProps> = ({ className }) => {
  const { setIsOpen } = useDialogContext();

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 bg-black/50 backdrop-blur-sm',
        'animate-in fade-in-0 duration-150',
        className
      )}
      onClick={() => setIsOpen(false)}
      aria-hidden="true"
    />
  );
};

// Content component
interface DialogContentProps {
  children: React.ReactNode;
  className?: string;
  showCloseButton?: boolean;
  onEscapeKeyDown?: (e: KeyboardEvent) => void;
  onPointerDownOutside?: (e: PointerEvent) => void;
}

export const DialogContent: React.FC<DialogContentProps> = ({
  children,
  className,
  showCloseButton = true,
  onEscapeKeyDown,
  onPointerDownOutside
}) => {
  const { isOpen, setIsOpen } = useDialogContext();
  const contentRef = useRef<HTMLDivElement>(null);
  
  useFocusTrap(isOpen, contentRef);
  useBodyScrollLock(isOpen);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onEscapeKeyDown?.(e);
        if (!e.defaultPrevented) {
          setIsOpen(false);
        }
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onEscapeKeyDown, setIsOpen]);

  if (!isOpen) return null;

  return (
    <Portal>
      <DialogOverlay />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          ref={contentRef}
          className={cn(
            'relative bg-white rounded-lg shadow-xl',
            'w-full max-w-md max-h-[85vh] overflow-hidden',
            'animate-in fade-in-0 zoom-in-95 duration-150',
            className
          )}
          role="dialog"
          aria-modal="true"
          onClick={(e) => e.stopPropagation()}
        >
          {showCloseButton && (
            <button
              onClick={() => setIsOpen(false)}
              className={cn(
                'absolute right-4 top-4 rounded-sm opacity-70',
                'ring-offset-white transition-opacity',
                'hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-iss-bordeaux-500 focus:ring-offset-2',
                'disabled:pointer-events-none'
              )}
              aria-label="Chiudi dialog"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Chiudi</span>
            </button>
          )}
          {children}
        </div>
      </div>
    </Portal>
  );
};

// Header component
interface DialogHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const DialogHeader: React.FC<DialogHeaderProps> = ({
  children,
  className
}) => (
  <div className={cn('flex flex-col space-y-1.5 text-center sm:text-left p-6 pb-0', className)}>
    {children}
  </div>
);

// Footer component
interface DialogFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const DialogFooter: React.FC<DialogFooterProps> = ({
  children,
  className
}) => (
  <div className={cn('flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 p-6 pt-0', className)}>
    {children}
  </div>
);

// Title component
interface DialogTitleProps {
  children: React.ReactNode;
  className?: string;
}

export const DialogTitle: React.FC<DialogTitleProps> = ({
  children,
  className
}) => (
  <h2 className={cn('text-lg font-semibold leading-none tracking-tight', className)}>
    {children}
  </h2>
);

// Description component
interface DialogDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

export const DialogDescription: React.FC<DialogDescriptionProps> = ({
  children,
  className
}) => (
  <p className={cn('text-sm text-gray-500', className)}>
    {children}
  </p>
);
