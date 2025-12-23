/**
 * MARKETTINA v2.0 - CENTRALIZED CONFIGURATION
 * Single source of truth for all constants
 * ZERO hardcoded values in components
 */

// ============================================================================
// API ENDPOINTS
// ============================================================================

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://markettina.it/api/v1';

export const API_ENDPOINTS = {
  // Admin endpoints
  admin: {
    bookings: '/api/v1/admin/bookings',
    analytics: '/api/v1/admin/analytics',
    users: '/api/v1/admin/users',
    portfolio: '/api/v1/admin/portfolio',
    projects: '/api/v1/admin/projects',
    services: '/api/v1/admin/services',
    finance: '/api/v1/admin/finance',
    expenses: '/api/v1/admin/expenses',
  },

  // Public endpoints
  public: {
    portfolio: '/api/v1/portfolio',
    projects: '/api/v1/projects',
    services: '/api/v1/services',
    contact: '/api/v1/contact',
  },

  // AI endpoints
  ai: {
    chat: 'https://markettina.it/ai/api/v1/demo/ask',
  },
} as const;

// ============================================================================
// EXTERNAL URLS
// ============================================================================

export const EXTERNAL_URLS = {
  site: 'https://markettina.it',
  calendly: {
    base: 'https://calendly.com/markettina',
    consultation: 'https://calendly.com/markettina/demo',
    widget: 'https://assets.calendly.com/assets/external/widget.js',
  },
  social: {
    github: 'https://github.com/markettina',
    linkedin: 'https://linkedin.com/company/markettina',
    instagram: 'https://instagram.com/markettina_ai',
    twitter: 'https://twitter.com/markettina_ai',
  },
  images: {
    og: 'https://markettina.it/og-image.jpg',
    twitter: 'https://markettina.it/twitter-image.png',
  },
} as const;

// ============================================================================
// BREAKPOINTS (Mobile-First)
// ============================================================================

export const BREAKPOINTS = {
  sm: 640,   // Small devices (large phones)
  md: 768,   // Medium devices (tablets)
  lg: 1024,  // Large devices (desktops)
  xl: 1280,  // Extra large devices
  '2xl': 1536, // 2X large devices
} as const;

export type Breakpoint = keyof typeof BREAKPOINTS;

// ============================================================================
// LAYOUT DIMENSIONS
// ============================================================================

export const LAYOUT = {
  // Header
  header: {
    height: 64,        // 4rem = 16 * 4 = 64px
    heightClass: 'h-16',
  },

  // Sidebar (Desktop)
  sidebar: {
    widthExpanded: 260,
    widthCollapsed: 72,
    widthExpandedClass: 'w-[260px]',
    widthCollapsedClass: 'w-[72px]',
  },

  // Bottom Navigation (Mobile)
  bottomNav: {
    height: 64,
    heightClass: 'h-16',
  },

  // Safe areas (iOS notch support)
  safeArea: {
    top: 'env(safe-area-inset-top)',
    bottom: 'env(safe-area-inset-bottom)',
    left: 'env(safe-area-inset-left)',
    right: 'env(safe-area-inset-right)',
  },

  // Touch targets (iOS/Android minimum)
  touchTarget: {
    minSize: 44,       // 44x44px minimum for accessibility
    minSizeClass: 'min-h-11 min-w-11', // 44px = 11 * 4
  },
} as const;

// ============================================================================
// SPACING SCALE (Mobile-First)
// ============================================================================

export const SPACING = {
  xs: 'space-y-2',    // 8px
  sm: 'space-y-3',    // 12px
  md: 'space-y-4',    // 16px
  lg: 'space-y-6',    // 24px
  xl: 'space-y-8',    // 32px
  '2xl': 'space-y-12', // 48px

  // Padding mobile-first presets
  padding: {
    mobile: 'p-3',              // 12px
    tablet: 'sm:p-4 md:p-6',    // 16px → 24px
    desktop: 'lg:p-8',          // 32px
    full: 'p-3 sm:p-4 md:p-6 lg:p-8', // Complete mobile-first scale
  },

  // Gap mobile-first presets
  gap: {
    mobile: 'gap-3',            // 12px
    tablet: 'sm:gap-4 md:gap-6', // 16px → 24px
    desktop: 'lg:gap-8',        // 32px
    full: 'gap-3 sm:gap-4 md:gap-6 lg:gap-8',
  },
} as const;

// ============================================================================
// BRAND COLORS
// ============================================================================

export const COLORS = {
  gold: {
    DEFAULT: '#D4AF37',
    light: '#F4E5B8',
    dark: '#AA8C2C',
    50: '#FBF8EC',
    100: '#F4EBCE',
    200: '#EBD9A0',
    300: '#E2C772',
    400: '#D4AF37',
    500: '#C49A2C',
    600: '#A47D24',
    700: '#7D5F1B',
    800: '#574213',
    900: '#31250B',
  },
} as const;

// ============================================================================
// TYPOGRAPHY SCALE (Mobile-First)
// ============================================================================

export const TYPOGRAPHY = {
  // Headings - mobile-first classes
  h1: 'text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-semibold tracking-tight',
  h2: 'text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-semibold tracking-tight',
  h3: 'text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-semibold tracking-tight',
  h4: 'text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl font-semibold tracking-tight',
  h5: 'text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl font-semibold tracking-tight',
  h6: 'text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl font-semibold tracking-tight',

  // Body text
  body: {
    large: 'text-lg sm:text-xl',
    base: 'text-base sm:text-lg',
    small: 'text-sm sm:text-base',
    xs: 'text-xs sm:text-sm',
  },
} as const;

// ============================================================================
// ANIMATION DURATIONS
// ============================================================================

export const ANIMATION = {
  fast: 150,
  normal: 200,
  slow: 300,
  slower: 500,
} as const;

// ============================================================================
// Z-INDEX SCALE
// ============================================================================

export const Z_INDEX = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
} as const;

// ============================================================================
// FORM VALIDATION
// ============================================================================

export const VALIDATION = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,9}$/,
  url: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$/,
} as const;

// ============================================================================
// PAGINATION
// ============================================================================

export const PAGINATION = {
  defaultPageSize: 10,
  pageSizeOptions: [10, 25, 50, 100],
} as const;

// ============================================================================
// LOCAL STORAGE KEYS
// ============================================================================

export const STORAGE_KEYS = {
  adminToken: 'admin_token',
  adminRefreshToken: 'admin_refresh_token',
  adminEmail: 'admin_email',
  theme: 'theme',
  language: 'i18nextLng',
} as const;

// ============================================================================
// QUERY KEYS (React Query)
// ============================================================================

export const QUERY_KEYS = {
  bookings: ['bookings'],
  booking: (id: string) => ['bookings', id],
  analytics: ['analytics'],
  users: ['users'],
  user: (id: string) => ['users', id],
  portfolio: ['portfolio'],
  projects: ['projects'],
  project: (id: string) => ['projects', id],
  services: ['services'],
  service: (id: string) => ['services', id],
  finance: ['finance'],
  expenses: ['expenses'],
} as const;

// ============================================================================
// FEATURE FLAGS
// ============================================================================

export const FEATURES = {
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS !== 'false',
  enableChat: import.meta.env.VITE_ENABLE_CHAT !== 'false',
  enableDarkMode: true,
  enablePWA: import.meta.env.VITE_ENABLE_PWA === 'true',
} as const;
