import { useState, useEffect, ImgHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

interface OptimizedImageProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'placeholder'> {
  src: string;
  alt: string;
  aspectRatio?: string;
  placeholder?: "blur" | "none";
  sizes?: string;
  priority?: boolean;
}

export function OptimizedImage({
  src,
  alt,
  aspectRatio,
  placeholder = "none",
  sizes,
  priority = false,
  className,
  ...props
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(priority);

  useEffect(() => {
    if (priority) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { rootMargin: "50px" }
    );

    const element = document.getElementById(`img-${src}`);
    if (element) observer.observe(element);

    return () => observer.disconnect();
  }, [src, priority]);

  return (
    <div
      id={`img-${src}`}
      className={cn("relative overflow-hidden bg-secondary", className)}
      style={aspectRatio ? { aspectRatio } : undefined}
    >
      {isInView && (
        <img
          src={src}
          alt={alt}
          sizes={sizes}
          loading={priority ? "eager" : "lazy"}
          onLoad={() => setIsLoaded(true)}
          className={cn(
            "w-full h-full object-cover transition-opacity duration-300",
            isLoaded ? "opacity-100" : "opacity-0"
          )}
          {...props}
        />
      )}
      {placeholder === "blur" && !isLoaded && (
        <div className="absolute inset-0 bg-secondary animate-pulse" />
      )}
    </div>
  );
}

interface OptimizedAvatarProps {
  src: string;
  alt: string;
  size?: "sm" | "md" | "lg" | "xl";
  priority?: boolean;
  className?: string;
}

export function OptimizedAvatar({
  src,
  alt,
  size = "md",
  priority = false,
  className,
}: OptimizedAvatarProps) {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-12 h-12",
    lg: "w-16 h-16",
    xl: "w-24 h-24",
  };

  return (
    <div className={cn("rounded-2xl overflow-hidden", sizeClasses[size], className)}>
      <OptimizedImage
        src={src}
        alt={alt}
        priority={priority}
        className="w-full h-full"
      />
    </div>
  );
}
