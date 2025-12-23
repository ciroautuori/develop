/**
 * useMobileViewport - Hook per ottimizzazione viewport mobile
 * Gestisce responsive design, touch detection, orientation
 */

import { useState, useEffect, useCallback } from 'react';

export interface ViewportInfo {
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isLandscape: boolean;
  isPortrait: boolean;
  devicePixelRatio: number;
  isTouchDevice: boolean;
  safeAreaInsets: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
}

export interface MobileCapabilities {
  supportsVibration: boolean;
  supportsServiceWorker: boolean;
  supportsWebShare: boolean;
  supportsMediaDevices: boolean;
  supportsFullscreen: boolean;
  supportsPushNotifications: boolean;
}

// Breakpoints mobile-first
export const BREAKPOINTS = {
  sm: 640,   // Small devices (phones)
  md: 768,   // Medium devices (tablets)
  lg: 1024,  // Large devices (desktops)
  xl: 1280,  // Extra large devices
  '2xl': 1536 // 2X large devices
} as const;

export function useMobileViewport() {
  const [viewport, setViewport] = useState<ViewportInfo>({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
    isMobile: false,
    isTablet: false,
    isDesktop: false,
    isLandscape: false,
    isPortrait: true,
    devicePixelRatio: typeof window !== 'undefined' ? window.devicePixelRatio : 1,
    isTouchDevice: false,
    safeAreaInsets: { top: 0, bottom: 0, left: 0, right: 0 }
  });

  const [capabilities, setCapabilities] = useState<MobileCapabilities>({
    supportsVibration: false,
    supportsServiceWorker: false,
    supportsWebShare: false,
    supportsMediaDevices: false,
    supportsFullscreen: false,
    supportsPushNotifications: false
  });

  // Detect device capabilities
  const detectCapabilities = useCallback((): MobileCapabilities => {
    if (typeof window === 'undefined') {
      return {
        supportsVibration: false,
        supportsServiceWorker: false,
        supportsWebShare: false,
        supportsMediaDevices: false,
        supportsFullscreen: false,
        supportsPushNotifications: false
      };
    }

    return {
      supportsVibration: 'vibrate' in navigator,
      supportsServiceWorker: 'serviceWorker' in navigator,
      supportsWebShare: 'share' in navigator,
      supportsMediaDevices: 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices,
      supportsFullscreen: 'requestFullscreen' in document.documentElement,
      supportsPushNotifications: 'PushManager' in window && 'serviceWorker' in navigator
    };
  }, []);

  // Calculate safe area insets (iOS notch support)
  const calculateSafeAreaInsets = useCallback(() => {
    if (typeof window === 'undefined') return { top: 0, bottom: 0, left: 0, right: 0 };

    const style = getComputedStyle(document.documentElement);
    return {
      top: parseInt(style.getPropertyValue('--sat') || '0', 10),
      bottom: parseInt(style.getPropertyValue('--sab') || '0', 10),
      left: parseInt(style.getPropertyValue('--sal') || '0', 10),
      right: parseInt(style.getPropertyValue('--sar') || '0', 10)
    };
  }, []);

  // Detect touch device
  const detectTouchDevice = useCallback((): boolean => {
    if (typeof window === 'undefined') return false;

    return (
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      // @ts-ignore
      navigator.msMaxTouchPoints > 0
    );
  }, []);

  // Update viewport info
  const updateViewport = useCallback(() => {
    if (typeof window === 'undefined') return;

    const width = window.innerWidth;
    const height = window.innerHeight;
    const isLandscape = width > height;
    const isPortrait = !isLandscape;

    // Mobile-first breakpoints
    const isMobile = width < BREAKPOINTS.md;
    const isTablet = width >= BREAKPOINTS.md && width < BREAKPOINTS.lg;
    const isDesktop = width >= BREAKPOINTS.lg;

    const devicePixelRatio = window.devicePixelRatio || 1;
    const isTouchDevice = detectTouchDevice();
    const safeAreaInsets = calculateSafeAreaInsets();

    setViewport({
      width,
      height,
      isMobile,
      isTablet,
      isDesktop,
      isLandscape,
      isPortrait,
      devicePixelRatio,
      isTouchDevice,
      safeAreaInsets
    });
  }, [detectTouchDevice, calculateSafeAreaInsets]);

  // Effect for viewport updates
  useEffect(() => {
    updateViewport();
    setCapabilities(detectCapabilities());

    const handleResize = () => updateViewport();
    const handleOrientationChange = () => {
      // Delay to get accurate dimensions after rotation
      setTimeout(updateViewport, 100);
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleOrientationChange);

    // Update CSS custom properties for safe area
    const updateSafeAreaCSS = () => {
      if (typeof window !== 'undefined' && 'CSS' in window && 'supports' in window.CSS) {
        if (window.CSS.supports('padding-top: env(safe-area-inset-top)')) {
          document.documentElement.style.setProperty('--sat', 'env(safe-area-inset-top)');
          document.documentElement.style.setProperty('--sab', 'env(safe-area-inset-bottom)');
          document.documentElement.style.setProperty('--sal', 'env(safe-area-inset-left)');
          document.documentElement.style.setProperty('--sar', 'env(safe-area-inset-right)');
        }
      }
    };

    updateSafeAreaCSS();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleOrientationChange);
    };
  }, [updateViewport, detectCapabilities]);

  // Utility functions
  const isBreakpoint = useCallback((breakpoint: keyof typeof BREAKPOINTS) => {
    return viewport.width >= BREAKPOINTS[breakpoint];
  }, [viewport.width]);

  const getBreakpoint = useCallback((): keyof typeof BREAKPOINTS => {
    const { width } = viewport;
    if (width >= BREAKPOINTS['2xl']) return '2xl';
    if (width >= BREAKPOINTS.xl) return 'xl';
    if (width >= BREAKPOINTS.lg) return 'lg';
    if (width >= BREAKPOINTS.md) return 'md';
    return 'sm';
  }, [viewport.width]);

  // Mobile-specific utilities
  const vibrate = useCallback((pattern: number | number[] = 200) => {
    if (capabilities.supportsVibration) {
      navigator.vibrate(pattern);
    }
  }, [capabilities.supportsVibration]);

  const requestFullscreen = useCallback(() => {
    if (capabilities.supportsFullscreen) {
      document.documentElement.requestFullscreen();
    }
  }, [capabilities.supportsFullscreen]);

  const shareContent = useCallback(async (data: ShareData) => {
    if (capabilities.supportsWebShare) {
      try {
        await navigator.share(data);
        return true;
      } catch (error) {
        console.error('Error sharing:', error);
        return false;
      }
    }
    return false;
  }, [capabilities.supportsWebShare]);

  // Responsive utilities
  const mobileFirst = useCallback((values: Record<keyof typeof BREAKPOINTS, any>) => {
    const breakpoint = getBreakpoint();

    // Return the largest applicable value (mobile-first approach)
    const orderedBreakpoints: Array<keyof typeof BREAKPOINTS> = ['sm', 'md', 'lg', 'xl', '2xl'];
    const currentIndex = orderedBreakpoints.indexOf(breakpoint);

    for (let i = currentIndex; i >= 0; i--) {
      const bp = orderedBreakpoints[i];
      if (values[bp] !== undefined) {
        return values[bp];
      }
    }

    return values.sm;
  }, [getBreakpoint]);

  return {
    viewport,
    capabilities,
    utils: {
      isBreakpoint,
      getBreakpoint,
      vibrate,
      requestFullscreen,
      shareContent,
      mobileFirst
    }
  };
}

// Hook per detection delle gesture touch
export function useTouchGestures() {
  const [gestureState, setGestureState] = useState({
    isSwiping: false,
    swipeDirection: null as 'up' | 'down' | 'left' | 'right' | null,
    touchCount: 0,
    lastTap: 0
  });

  const handleTouchStart = useCallback((event: TouchEvent) => {
    setGestureState(prev => ({
      ...prev,
      touchCount: event.touches.length,
      isSwiping: false,
      swipeDirection: null
    }));
  }, []);

  const handleTouchEnd = useCallback((event: TouchEvent) => {
    const now = Date.now();
    const timeDiff = now - gestureState.lastTap;

    // Double tap detection
    if (timeDiff < 300 && timeDiff > 0) {
      // Double tap detected
      const customEvent = new CustomEvent('doubleTap', {
        detail: { event, timeDiff }
      });
      event.target?.dispatchEvent(customEvent);
    }

    setGestureState(prev => ({
      ...prev,
      lastTap: now,
      touchCount: 0,
      isSwiping: false,
      swipeDirection: null
    }));
  }, [gestureState.lastTap]);

  useEffect(() => {
    document.addEventListener('touchstart', handleTouchStart, { passive: true });
    document.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, [handleTouchStart, handleTouchEnd]);

  return gestureState;
}

// Hook per performance monitoring mobile
export function useMobilePerformance() {
  const [metrics, setMetrics] = useState({
    renderTime: 0,
    interactionDelay: 0,
    memoryUsage: 0,
    batteryLevel: null as number | null,
    connectionType: 'unknown' as string
  });

  useEffect(() => {
    // Performance monitoring
    const measurePerformance = () => {
      if ('performance' in window) {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navigation) {
          setMetrics(prev => ({
            ...prev,
            renderTime: navigation.loadEventEnd - navigation.fetchStart
          }));
        }
      }

      // Memory usage (if available)
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        if (memory?.usedJSHeapSize && memory?.totalJSHeapSize) {
          setMetrics(prev => ({
            ...prev,
            memoryUsage: memory.usedJSHeapSize / memory.totalJSHeapSize
          }));
        }
      }

      // Battery API
      if ('getBattery' in navigator) {
        (navigator as any).getBattery().then((battery: any) => {
          setMetrics(prev => ({
            ...prev,
            batteryLevel: battery.level
          }));
        });
      }

      // Connection type
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        if (connection?.effectiveType) {
          setMetrics(prev => ({
            ...prev,
            connectionType: connection.effectiveType || 'unknown'
          }));
        }
      }
    };

    measurePerformance();

    const interval = setInterval(measurePerformance, 5000); // Update every 5s

    return () => clearInterval(interval);
  }, []);

  return metrics;
}
