import { useEffect, useRef, useState } from 'react';
import { cn } from '../../lib/utils';

interface RevealOnScrollProps {
  children: React.ReactNode;
  className?: string;
  animation?: 'fade-in-up' | 'fade-in-left' | 'fade-in-scale' | 'slide-up';
  delay?: number;
  threshold?: number;
  id?: string;
}

export function RevealOnScroll({
  children,
  className,
  animation = 'fade-in-up',
  delay = 0,
  threshold = 0.1,
  id
}: RevealOnScrollProps) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      {
        threshold,
        rootMargin: '0px 0px -50px 0px',
      }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, [threshold]);

  const animationClass = `animate-${animation}`;

  return (
    <div
      ref={ref}
      id={id}
      className={cn(
        'opacity-0 transition-opacity duration-300', // Start hidden
        isVisible && 'opacity-100',
        isVisible && animationClass,
        className
      )}
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: 'both',
      }}
    >
      {children}
    </div>
  );
}
