import { useState, useEffect } from "react";

export type Breakpoint = "mobile" | "tablet" | "desktop";

export interface ResponsiveState {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  breakpoint: Breakpoint;
  width: number;
}

const BREAKPOINTS = {
  mobile: 768,
  tablet: 1024,
} as const;

export function useResponsive(): ResponsiveState {
  const [state, setState] = useState<ResponsiveState>(() => {
    if (typeof window === "undefined") {
      return {
        isMobile: true,
        isTablet: false,
        isDesktop: false,
        breakpoint: "mobile",
        width: 0,
      };
    }

    const width = window.innerWidth;
    const breakpoint: Breakpoint =
      width < BREAKPOINTS.mobile
        ? "mobile"
        : width < BREAKPOINTS.tablet
          ? "tablet"
          : "desktop";

    return {
      isMobile: breakpoint === "mobile",
      isTablet: breakpoint === "tablet",
      isDesktop: breakpoint === "desktop",
      breakpoint,
      width,
    };
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const breakpoint: Breakpoint =
        width < BREAKPOINTS.mobile
          ? "mobile"
          : width < BREAKPOINTS.tablet
            ? "tablet"
            : "desktop";

      setState({
        isMobile: breakpoint === "mobile",
        isTablet: breakpoint === "tablet",
        isDesktop: breakpoint === "desktop",
        breakpoint,
        width,
      });
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return state;
}

// Utility hook per media queries custom
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    if (typeof window === "undefined") return;

    const mediaQuery = window.matchMedia(query);
    const handler = (event: MediaQueryListEvent) => setMatches(event.matches);

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handler);
      return () => mediaQuery.removeEventListener("change", handler);
    }
    // Legacy browsers
    else {
      mediaQuery.addListener(handler);
      return () => mediaQuery.removeListener(handler);
    }
  }, [query]);

  return matches;
}
