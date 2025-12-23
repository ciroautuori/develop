/**
 * DIMENSIONI IMMAGINI SOCIAL - Sistema Completo Marketing Hub
 *
 * Tutte le dimensioni per ogni piattaforma social:
 * - Post (feed, portrait, landscape)
 * - Stories
 * - Reels/Shorts
 * - Cover/Banner
 * - Profile/Avatar
 * - Ads
 *
 * Integrazione Brand DNA StudioCentOS
 *
 * @module constants/image-sizes
 */

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface ImageSizeConfig {
  width: number;
  height: number;
  label: string;
  aspectRatio: string;
  category: ImageCategory;
  platform: SocialPlatformKey;
  description?: string;
  recommended?: boolean;
  maxFileSize?: string;
  supportedFormats?: string[];
}

export type ImageCategory =
  | 'post'
  | 'story'
  | 'reel'
  | 'cover'
  | 'profile'
  | 'ad'
  | 'thumbnail'
  | 'carousel'
  | 'pin';

export type SocialPlatformKey =
  | 'instagram'
  | 'facebook'
  | 'linkedin'
  | 'twitter'
  | 'tiktok'
  | 'youtube'
  | 'pinterest'
  | 'threads'
  | 'google_business'
  | 'whatsapp';

// ============================================================================
// BRAND COLORS FOR IMAGE GENERATION
// ============================================================================

export const BRAND_IMAGE_STYLE = {
  colors: {
    primary: '#D4AF37',      // Oro
    secondary: '#0A0A0A',    // Nero
    accent: '#FAFAFA',       // Bianco
    gradient: {
      gold: 'linear-gradient(135deg, #D4AF37 0%, #B8960C 100%)',
      dark: 'linear-gradient(180deg, #0A0A0A 0%, #1A1A1A 100%)',
      premium: 'linear-gradient(135deg, #D4AF37 0%, #0A0A0A 100%)',
    },
  },
  fonts: {
    heading: 'Montserrat, sans-serif',
    body: 'Inter, sans-serif',
  },
  style: {
    professional: 'clean, modern, minimal, premium',
    creative: 'bold, vibrant, dynamic, engaging',
    elegant: 'luxurious, sophisticated, refined',
  },
  watermark: {
    logo: 'StudioCentOS',
    position: 'bottom-right',
    opacity: 0.8,
  },
} as const;

// ============================================================================
// INSTAGRAM SIZES (Complete)
// ============================================================================

export const INSTAGRAM_SIZES: Record<string, ImageSizeConfig> = {
  // Feed Posts
  post_square: {
    width: 1080,
    height: 1080,
    label: 'Instagram Post Quadrato',
    aspectRatio: '1:1',
    category: 'post',
    platform: 'instagram',
    description: 'Post standard quadrato per il feed',
    recommended: true,
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  post_portrait: {
    width: 1080,
    height: 1350,
    label: 'Instagram Post Verticale',
    aspectRatio: '4:5',
    category: 'post',
    platform: 'instagram',
    description: 'Post verticale per maggiore visibilità nel feed',
    recommended: true,
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  post_landscape: {
    width: 1080,
    height: 566,
    label: 'Instagram Post Orizzontale',
    aspectRatio: '1.91:1',
    category: 'post',
    platform: 'instagram',
    description: 'Post orizzontale (meno comune)',
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Stories & Reels
  story: {
    width: 1080,
    height: 1920,
    label: 'Instagram Story',
    aspectRatio: '9:16',
    category: 'story',
    platform: 'instagram',
    description: 'Story a schermo intero',
    recommended: true,
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png', 'mp4'],
  },
  reel: {
    width: 1080,
    height: 1920,
    label: 'Instagram Reel',
    aspectRatio: '9:16',
    category: 'reel',
    platform: 'instagram',
    description: 'Video verticale per Reels',
    recommended: true,
    maxFileSize: '4GB',
    supportedFormats: ['mp4', 'mov'],
  },
  // Carousel
  carousel: {
    width: 1080,
    height: 1080,
    label: 'Instagram Carousel',
    aspectRatio: '1:1',
    category: 'carousel',
    platform: 'instagram',
    description: 'Slide per carousel (fino a 10)',
    recommended: true,
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  carousel_portrait: {
    width: 1080,
    height: 1350,
    label: 'Instagram Carousel Verticale',
    aspectRatio: '4:5',
    category: 'carousel',
    platform: 'instagram',
    description: 'Carousel verticale per più impatto',
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Profile
  profile: {
    width: 320,
    height: 320,
    label: 'Instagram Profilo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'instagram',
    description: 'Immagine profilo (visualizzata 110x110)',
    maxFileSize: '10MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Ads
  ad_story: {
    width: 1080,
    height: 1920,
    label: 'Instagram Story Ads',
    aspectRatio: '9:16',
    category: 'ad',
    platform: 'instagram',
    description: 'Pubblicità story',
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png', 'mp4'],
  },
  ad_feed: {
    width: 1080,
    height: 1080,
    label: 'Instagram Feed Ads',
    aspectRatio: '1:1',
    category: 'ad',
    platform: 'instagram',
    description: 'Pubblicità feed',
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
};

// ============================================================================
// FACEBOOK SIZES (Complete)
// ============================================================================

export const FACEBOOK_SIZES: Record<string, ImageSizeConfig> = {
  // Feed Posts
  post: {
    width: 1200,
    height: 630,
    label: 'Facebook Post',
    aspectRatio: '1.91:1',
    category: 'post',
    platform: 'facebook',
    description: 'Post standard per il feed',
    recommended: true,
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  post_square: {
    width: 1200,
    height: 1200,
    label: 'Facebook Post Quadrato',
    aspectRatio: '1:1',
    category: 'post',
    platform: 'facebook',
    description: 'Post quadrato',
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  post_vertical: {
    width: 1080,
    height: 1350,
    label: 'Facebook Post Verticale',
    aspectRatio: '4:5',
    category: 'post',
    platform: 'facebook',
    description: 'Post verticale',
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Stories & Reels
  story: {
    width: 1080,
    height: 1920,
    label: 'Facebook Story',
    aspectRatio: '9:16',
    category: 'story',
    platform: 'facebook',
    description: 'Story a schermo intero',
    recommended: true,
    maxFileSize: '4GB',
    supportedFormats: ['jpg', 'png', 'mp4'],
  },
  reel: {
    width: 1080,
    height: 1920,
    label: 'Facebook Reel',
    aspectRatio: '9:16',
    category: 'reel',
    platform: 'facebook',
    description: 'Video verticale per Reels',
    recommended: true,
    maxFileSize: '4GB',
    supportedFormats: ['mp4', 'mov'],
  },
  // Cover & Profile
  cover: {
    width: 820,
    height: 312,
    label: 'Facebook Cover',
    aspectRatio: '2.63:1',
    category: 'cover',
    platform: 'facebook',
    description: 'Immagine copertina pagina',
    recommended: true,
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
  cover_mobile: {
    width: 640,
    height: 360,
    label: 'Facebook Cover Mobile',
    aspectRatio: '16:9',
    category: 'cover',
    platform: 'facebook',
    description: 'Copertina ottimizzata mobile',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
  profile: {
    width: 170,
    height: 170,
    label: 'Facebook Profilo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'facebook',
    description: 'Immagine profilo pagina',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Event & Group
  event_cover: {
    width: 1920,
    height: 1080,
    label: 'Facebook Evento Cover',
    aspectRatio: '16:9',
    category: 'cover',
    platform: 'facebook',
    description: 'Copertina evento',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
  group_cover: {
    width: 1640,
    height: 856,
    label: 'Facebook Gruppo Cover',
    aspectRatio: '1.91:1',
    category: 'cover',
    platform: 'facebook',
    description: 'Copertina gruppo',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Ads
  ad_feed: {
    width: 1200,
    height: 628,
    label: 'Facebook Feed Ads',
    aspectRatio: '1.91:1',
    category: 'ad',
    platform: 'facebook',
    description: 'Pubblicità feed',
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  ad_carousel: {
    width: 1080,
    height: 1080,
    label: 'Facebook Carousel Ads',
    aspectRatio: '1:1',
    category: 'ad',
    platform: 'facebook',
    description: 'Pubblicità carousel',
    maxFileSize: '30MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Link Preview
  link_preview: {
    width: 1200,
    height: 630,
    label: 'Facebook Link Preview',
    aspectRatio: '1.91:1',
    category: 'post',
    platform: 'facebook',
    description: 'Anteprima link condiviso',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
};

// ============================================================================
// LINKEDIN SIZES (Complete)
// ============================================================================

export const LINKEDIN_SIZES: Record<string, ImageSizeConfig> = {
  // Feed Posts
  post: {
    width: 1200,
    height: 627,
    label: 'LinkedIn Post',
    aspectRatio: '1.91:1',
    category: 'post',
    platform: 'linkedin',
    description: 'Post standard per il feed',
    recommended: true,
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png', 'gif'],
  },
  post_square: {
    width: 1200,
    height: 1200,
    label: 'LinkedIn Post Quadrato',
    aspectRatio: '1:1',
    category: 'post',
    platform: 'linkedin',
    description: 'Post quadrato',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png', 'gif'],
  },
  post_vertical: {
    width: 1080,
    height: 1350,
    label: 'LinkedIn Post Verticale',
    aspectRatio: '4:5',
    category: 'post',
    platform: 'linkedin',
    description: 'Post verticale',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png', 'gif'],
  },
  // Carousel/Document
  carousel: {
    width: 1080,
    height: 1080,
    label: 'LinkedIn Carousel/PDF',
    aspectRatio: '1:1',
    category: 'carousel',
    platform: 'linkedin',
    description: 'Slide per documento carousel',
    recommended: true,
    maxFileSize: '100MB',
    supportedFormats: ['pdf', 'ppt', 'pptx'],
  },
  carousel_portrait: {
    width: 1080,
    height: 1350,
    label: 'LinkedIn Carousel Verticale',
    aspectRatio: '4:5',
    category: 'carousel',
    platform: 'linkedin',
    description: 'Slide verticale per documento',
    maxFileSize: '100MB',
    supportedFormats: ['pdf', 'ppt', 'pptx'],
  },
  // Cover & Profile
  cover_personal: {
    width: 1584,
    height: 396,
    label: 'LinkedIn Cover Personale',
    aspectRatio: '4:1',
    category: 'cover',
    platform: 'linkedin',
    description: 'Copertina profilo personale',
    recommended: true,
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
  cover_company: {
    width: 1128,
    height: 191,
    label: 'LinkedIn Cover Azienda',
    aspectRatio: '5.9:1',
    category: 'cover',
    platform: 'linkedin',
    description: 'Copertina pagina aziendale',
    recommended: true,
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
  profile: {
    width: 400,
    height: 400,
    label: 'LinkedIn Profilo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'linkedin',
    description: 'Immagine profilo',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
  company_logo: {
    width: 300,
    height: 300,
    label: 'LinkedIn Logo Azienda',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'linkedin',
    description: 'Logo pagina aziendale',
    maxFileSize: '4MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Ads
  ad_single: {
    width: 1200,
    height: 627,
    label: 'LinkedIn Sponsored Content',
    aspectRatio: '1.91:1',
    category: 'ad',
    platform: 'linkedin',
    description: 'Contenuto sponsorizzato',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
  ad_carousel: {
    width: 1080,
    height: 1080,
    label: 'LinkedIn Carousel Ads',
    aspectRatio: '1:1',
    category: 'ad',
    platform: 'linkedin',
    description: 'Carousel sponsorizzato',
    maxFileSize: '10MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Article
  article_cover: {
    width: 1200,
    height: 644,
    label: 'LinkedIn Articolo Cover',
    aspectRatio: '1.86:1',
    category: 'cover',
    platform: 'linkedin',
    description: 'Immagine copertina articolo',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
};

// ============================================================================
// TWITTER/X SIZES (Complete)
// ============================================================================

export const TWITTER_SIZES: Record<string, ImageSizeConfig> = {
  // Feed Posts
  post: {
    width: 1600,
    height: 900,
    label: 'X/Twitter Post',
    aspectRatio: '16:9',
    category: 'post',
    platform: 'twitter',
    description: 'Immagine per tweet',
    recommended: true,
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png', 'gif'],
  },
  post_square: {
    width: 1200,
    height: 1200,
    label: 'X/Twitter Post Quadrato',
    aspectRatio: '1:1',
    category: 'post',
    platform: 'twitter',
    description: 'Tweet quadrato',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png', 'gif'],
  },
  post_vertical: {
    width: 1080,
    height: 1350,
    label: 'X/Twitter Post Verticale',
    aspectRatio: '4:5',
    category: 'post',
    platform: 'twitter',
    description: 'Tweet verticale',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png', 'gif'],
  },
  // Cover & Profile
  header: {
    width: 1500,
    height: 500,
    label: 'X/Twitter Header',
    aspectRatio: '3:1',
    category: 'cover',
    platform: 'twitter',
    description: 'Immagine header profilo',
    recommended: true,
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
  profile: {
    width: 400,
    height: 400,
    label: 'X/Twitter Profilo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'twitter',
    description: 'Immagine profilo',
    maxFileSize: '2MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Card Preview
  card_summary: {
    width: 800,
    height: 418,
    label: 'X/Twitter Card Summary',
    aspectRatio: '1.91:1',
    category: 'post',
    platform: 'twitter',
    description: 'Card anteprima link',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
  card_large: {
    width: 1200,
    height: 628,
    label: 'X/Twitter Card Large',
    aspectRatio: '1.91:1',
    category: 'post',
    platform: 'twitter',
    description: 'Card grande anteprima',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Ads
  ad_image: {
    width: 1200,
    height: 675,
    label: 'X/Twitter Image Ads',
    aspectRatio: '16:9',
    category: 'ad',
    platform: 'twitter',
    description: 'Pubblicità immagine',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
};

// ============================================================================
// TIKTOK SIZES (Complete)
// ============================================================================

export const TIKTOK_SIZES: Record<string, ImageSizeConfig> = {
  // Video
  video: {
    width: 1080,
    height: 1920,
    label: 'TikTok Video',
    aspectRatio: '9:16',
    category: 'reel',
    platform: 'tiktok',
    description: 'Video standard TikTok',
    recommended: true,
    maxFileSize: '287MB',
    supportedFormats: ['mp4', 'mov'],
  },
  // Cover
  video_cover: {
    width: 1080,
    height: 1920,
    label: 'TikTok Cover Video',
    aspectRatio: '9:16',
    category: 'thumbnail',
    platform: 'tiktok',
    description: 'Copertina video personalizzata',
    maxFileSize: '10MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Profile
  profile: {
    width: 200,
    height: 200,
    label: 'TikTok Profilo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'tiktok',
    description: 'Immagine profilo',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Ads
  ad_video: {
    width: 1080,
    height: 1920,
    label: 'TikTok Video Ads',
    aspectRatio: '9:16',
    category: 'ad',
    platform: 'tiktok',
    description: 'Pubblicità video',
    maxFileSize: '500MB',
    supportedFormats: ['mp4', 'mov'],
  },
  ad_spark: {
    width: 1080,
    height: 1920,
    label: 'TikTok Spark Ads',
    aspectRatio: '9:16',
    category: 'ad',
    platform: 'tiktok',
    description: 'Spark Ads (post organico sponsorizzato)',
    maxFileSize: '287MB',
    supportedFormats: ['mp4', 'mov'],
  },
};

// ============================================================================
// YOUTUBE SIZES (Complete)
// ============================================================================

export const YOUTUBE_SIZES: Record<string, ImageSizeConfig> = {
  // Thumbnails
  thumbnail: {
    width: 1280,
    height: 720,
    label: 'YouTube Thumbnail',
    aspectRatio: '16:9',
    category: 'thumbnail',
    platform: 'youtube',
    description: 'Miniatura video',
    recommended: true,
    maxFileSize: '2MB',
    supportedFormats: ['jpg', 'png'],
  },
  shorts_thumbnail: {
    width: 1080,
    height: 1920,
    label: 'YouTube Shorts Thumbnail',
    aspectRatio: '9:16',
    category: 'thumbnail',
    platform: 'youtube',
    description: 'Miniatura Shorts',
    maxFileSize: '2MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Video
  video_hd: {
    width: 1920,
    height: 1080,
    label: 'YouTube Video HD',
    aspectRatio: '16:9',
    category: 'reel',
    platform: 'youtube',
    description: 'Video Full HD',
    recommended: true,
    maxFileSize: '256GB',
    supportedFormats: ['mp4', 'mov', 'avi'],
  },
  video_4k: {
    width: 3840,
    height: 2160,
    label: 'YouTube Video 4K',
    aspectRatio: '16:9',
    category: 'reel',
    platform: 'youtube',
    description: 'Video 4K UHD',
    maxFileSize: '256GB',
    supportedFormats: ['mp4', 'mov', 'avi'],
  },
  shorts: {
    width: 1080,
    height: 1920,
    label: 'YouTube Shorts',
    aspectRatio: '9:16',
    category: 'reel',
    platform: 'youtube',
    description: 'Video verticale Shorts',
    recommended: true,
    maxFileSize: '256GB',
    supportedFormats: ['mp4', 'mov'],
  },
  // Channel Art
  banner: {
    width: 2560,
    height: 1440,
    label: 'YouTube Banner',
    aspectRatio: '16:9',
    category: 'cover',
    platform: 'youtube',
    description: 'Banner canale (safe area: 1546x423)',
    recommended: true,
    maxFileSize: '6MB',
    supportedFormats: ['jpg', 'png'],
  },
  banner_safe: {
    width: 1546,
    height: 423,
    label: 'YouTube Banner Safe Area',
    aspectRatio: '3.65:1',
    category: 'cover',
    platform: 'youtube',
    description: 'Area sicura banner (visibile su tutti i device)',
    maxFileSize: '6MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Profile
  profile: {
    width: 800,
    height: 800,
    label: 'YouTube Profilo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'youtube',
    description: 'Immagine profilo canale',
    maxFileSize: '2MB',
    supportedFormats: ['jpg', 'png'],
  },
  // End Screen
  end_screen: {
    width: 1920,
    height: 1080,
    label: 'YouTube End Screen',
    aspectRatio: '16:9',
    category: 'post',
    platform: 'youtube',
    description: 'Schermata finale video',
    maxFileSize: '2MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Watermark
  watermark: {
    width: 150,
    height: 150,
    label: 'YouTube Watermark',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'youtube',
    description: 'Watermark canale (branding)',
    maxFileSize: '1MB',
    supportedFormats: ['png'],
  },
};

// ============================================================================
// PINTEREST SIZES (Complete)
// ============================================================================

export const PINTEREST_SIZES: Record<string, ImageSizeConfig> = {
  // Pins
  pin_standard: {
    width: 1000,
    height: 1500,
    label: 'Pinterest Pin Standard',
    aspectRatio: '2:3',
    category: 'pin',
    platform: 'pinterest',
    description: 'Pin standard verticale',
    recommended: true,
    maxFileSize: '32MB',
    supportedFormats: ['jpg', 'png'],
  },
  pin_long: {
    width: 1000,
    height: 2100,
    label: 'Pinterest Pin Lungo',
    aspectRatio: '1:2.1',
    category: 'pin',
    platform: 'pinterest',
    description: 'Pin lungo (infografica)',
    maxFileSize: '32MB',
    supportedFormats: ['jpg', 'png'],
  },
  pin_square: {
    width: 1000,
    height: 1000,
    label: 'Pinterest Pin Quadrato',
    aspectRatio: '1:1',
    category: 'pin',
    platform: 'pinterest',
    description: 'Pin quadrato',
    maxFileSize: '32MB',
    supportedFormats: ['jpg', 'png'],
  },
  // Video Pin
  video_pin: {
    width: 1000,
    height: 1500,
    label: 'Pinterest Video Pin',
    aspectRatio: '2:3',
    category: 'reel',
    platform: 'pinterest',
    description: 'Video pin verticale',
    maxFileSize: '2GB',
    supportedFormats: ['mp4', 'mov'],
  },
  // Idea Pin
  idea_pin: {
    width: 1080,
    height: 1920,
    label: 'Pinterest Idea Pin',
    aspectRatio: '9:16',
    category: 'story',
    platform: 'pinterest',
    description: 'Idea Pin (story-like)',
    recommended: true,
    maxFileSize: '32MB',
    supportedFormats: ['jpg', 'png', 'mp4'],
  },
  // Profile & Board
  profile: {
    width: 165,
    height: 165,
    label: 'Pinterest Profilo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'pinterest',
    description: 'Immagine profilo',
    maxFileSize: '10MB',
    supportedFormats: ['jpg', 'png'],
  },
  board_cover: {
    width: 600,
    height: 600,
    label: 'Pinterest Board Cover',
    aspectRatio: '1:1',
    category: 'cover',
    platform: 'pinterest',
    description: 'Copertina bacheca',
    maxFileSize: '10MB',
    supportedFormats: ['jpg', 'png'],
  },
};

// ============================================================================
// THREADS SIZES (Complete)
// ============================================================================

export const THREADS_SIZES: Record<string, ImageSizeConfig> = {
  post: {
    width: 1080,
    height: 1080,
    label: 'Threads Post',
    aspectRatio: '1:1',
    category: 'post',
    platform: 'threads',
    description: 'Post quadrato standard',
    recommended: true,
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png', 'gif'],
  },
  post_portrait: {
    width: 1080,
    height: 1350,
    label: 'Threads Post Verticale',
    aspectRatio: '4:5',
    category: 'post',
    platform: 'threads',
    description: 'Post verticale',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png', 'gif'],
  },
  post_landscape: {
    width: 1080,
    height: 566,
    label: 'Threads Post Orizzontale',
    aspectRatio: '1.91:1',
    category: 'post',
    platform: 'threads',
    description: 'Post orizzontale',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png', 'gif'],
  },
  profile: {
    width: 400,
    height: 400,
    label: 'Threads Profilo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'threads',
    description: 'Immagine profilo (usa quella Instagram)',
    maxFileSize: '8MB',
    supportedFormats: ['jpg', 'png'],
  },
};

// ============================================================================
// GOOGLE BUSINESS SIZES (Complete)
// ============================================================================

export const GOOGLE_BUSINESS_SIZES: Record<string, ImageSizeConfig> = {
  post: {
    width: 1200,
    height: 900,
    label: 'Google Business Post',
    aspectRatio: '4:3',
    category: 'post',
    platform: 'google_business',
    description: 'Post per Google Business Profile',
    recommended: true,
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
  cover: {
    width: 1080,
    height: 608,
    label: 'Google Business Cover',
    aspectRatio: '16:9',
    category: 'cover',
    platform: 'google_business',
    description: 'Foto copertina profilo',
    recommended: true,
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
  logo: {
    width: 720,
    height: 720,
    label: 'Google Business Logo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'google_business',
    description: 'Logo aziendale',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
  photo: {
    width: 720,
    height: 720,
    label: 'Google Business Photo',
    aspectRatio: '1:1',
    category: 'post',
    platform: 'google_business',
    description: 'Foto prodotto/servizio',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
};

// ============================================================================
// WHATSAPP SIZES (Complete)
// ============================================================================

export const WHATSAPP_SIZES: Record<string, ImageSizeConfig> = {
  status: {
    width: 1080,
    height: 1920,
    label: 'WhatsApp Status',
    aspectRatio: '9:16',
    category: 'story',
    platform: 'whatsapp',
    description: 'Stato WhatsApp',
    recommended: true,
    maxFileSize: '16MB',
    supportedFormats: ['jpg', 'png', 'mp4'],
  },
  profile: {
    width: 500,
    height: 500,
    label: 'WhatsApp Profilo',
    aspectRatio: '1:1',
    category: 'profile',
    platform: 'whatsapp',
    description: 'Immagine profilo',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
  catalog: {
    width: 1080,
    height: 1080,
    label: 'WhatsApp Catalogo',
    aspectRatio: '1:1',
    category: 'post',
    platform: 'whatsapp',
    description: 'Immagine prodotto catalogo',
    maxFileSize: '5MB',
    supportedFormats: ['jpg', 'png'],
  },
};

// ============================================================================
// UNIFIED SOCIAL IMAGE SIZES (Legacy compatibility)
// ============================================================================

export const SOCIAL_IMAGE_SIZES: Record<string, ImageSizeConfig> = {
  // Meta Platforms
  facebook: FACEBOOK_SIZES.post,
  facebook_story: FACEBOOK_SIZES.story,
  instagram: INSTAGRAM_SIZES.post_square,
  instagram_portrait: INSTAGRAM_SIZES.post_portrait,
  instagram_story: INSTAGRAM_SIZES.story,
  threads: THREADS_SIZES.post,
  // Professional
  linkedin: LINKEDIN_SIZES.post,
  twitter: TWITTER_SIZES.post,
  // Video Platforms
  tiktok: TIKTOK_SIZES.video,
  youtube_thumbnail: YOUTUBE_SIZES.thumbnail,
  // Visual Discovery
  pinterest: PINTEREST_SIZES.pin_standard,
  // Local Business
  google_business: GOOGLE_BUSINESS_SIZES.post,
  // WhatsApp
  whatsapp_status: WHATSAPP_SIZES.status,
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Ottiene le dimensioni corrette per una piattaforma
 */
export function getImageSize(platform: string): ImageSizeConfig {
  return SOCIAL_IMAGE_SIZES[platform] || INSTAGRAM_SIZES.post_square;
}

/**
 * Ottiene tutte le dimensioni per una piattaforma specifica
 */
export function getAllSizesForPlatform(platform: SocialPlatformKey): Record<string, ImageSizeConfig> {
  const platformSizes: Record<SocialPlatformKey, Record<string, ImageSizeConfig>> = {
    instagram: INSTAGRAM_SIZES,
    facebook: FACEBOOK_SIZES,
    linkedin: LINKEDIN_SIZES,
    twitter: TWITTER_SIZES,
    tiktok: TIKTOK_SIZES,
    youtube: YOUTUBE_SIZES,
    pinterest: PINTEREST_SIZES,
    threads: THREADS_SIZES,
    google_business: GOOGLE_BUSINESS_SIZES,
    whatsapp: WHATSAPP_SIZES,
  };
  return platformSizes[platform] || INSTAGRAM_SIZES;
}

/**
 * Ottiene le dimensioni per categoria
 */
export function getSizesByCategory(category: ImageCategory): ImageSizeConfig[] {
  const allSizes = [
    ...Object.values(INSTAGRAM_SIZES),
    ...Object.values(FACEBOOK_SIZES),
    ...Object.values(LINKEDIN_SIZES),
    ...Object.values(TWITTER_SIZES),
    ...Object.values(TIKTOK_SIZES),
    ...Object.values(YOUTUBE_SIZES),
    ...Object.values(PINTEREST_SIZES),
    ...Object.values(THREADS_SIZES),
    ...Object.values(GOOGLE_BUSINESS_SIZES),
    ...Object.values(WHATSAPP_SIZES),
  ];
  return allSizes.filter(size => size.category === category);
}

/**
 * Ottiene le dimensioni raccomandate per tutte le piattaforme
 */
export function getRecommendedSizes(): ImageSizeConfig[] {
  const allSizes = [
    ...Object.values(INSTAGRAM_SIZES),
    ...Object.values(FACEBOOK_SIZES),
    ...Object.values(LINKEDIN_SIZES),
    ...Object.values(TWITTER_SIZES),
    ...Object.values(TIKTOK_SIZES),
    ...Object.values(YOUTUBE_SIZES),
    ...Object.values(PINTEREST_SIZES),
    ...Object.values(THREADS_SIZES),
    ...Object.values(GOOGLE_BUSINESS_SIZES),
    ...Object.values(WHATSAPP_SIZES),
  ];
  return allSizes.filter(size => size.recommended === true);
}

/**
 * Calcola le dimensioni mantenendo l'aspect ratio
 */
export function calculateDimensions(
  targetWidth: number,
  aspectRatio: string
): { width: number; height: number } {
  const [ratioW, ratioH] = aspectRatio.split(':').map(Number);
  const height = Math.round(targetWidth / (ratioW / ratioH));
  return { width: targetWidth, height };
}

/**
 * Genera il prompt per la generazione immagine con stile brand
 */
export function getBrandImagePrompt(
  basePrompt: string,
  platform: SocialPlatformKey,
  style: 'professional' | 'creative' | 'elegant' = 'professional'
): string {
  const size = SOCIAL_IMAGE_SIZES[platform] || INSTAGRAM_SIZES.post_square;
  const styleDesc = BRAND_IMAGE_STYLE.style[style];

  return `
${basePrompt}

SPECIFICHE IMMAGINE:
- Dimensioni: ${size.width}x${size.height} (${size.aspectRatio})
- Piattaforma: ${size.label}
- Stile: ${styleDesc}

BRAND STUDIOCENTOS:
- Colori primari: Oro #D4AF37, Nero #0A0A0A
- Stile: professionale, moderno, premium
- Evitare: colori troppo brillanti, immagini generiche stock
- Preferire: composizioni pulite, focus sul soggetto, qualità premium
`.trim();
}
