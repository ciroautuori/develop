/**
 * Types per Lead Finder centralizzati
 * @module types/lead
 */

export interface PlaceResult {
  place_id: string;
  name: string;
  formatted_address: string;
  formatted_phone_number?: string;
  website?: string;
  rating?: number;
  user_ratings_total?: number;
  business_status?: string;
  types?: string[];
  opening_hours?: {
    open_now?: boolean;
    weekday_text?: string[];
  };
  geometry?: {
    location: {
      lat: number;
      lng: number;
    };
  };
}

export interface LeadWithScore extends PlaceResult {
  score: number;
  scoreDetails?: LeadScoreDetails;
  enriched?: boolean;
  enrichedData?: EnrichedLeadData;
  savedToCRM?: boolean;
}

export interface LeadScoreDetails {
  hasWebsite: boolean;
  hasPhone: boolean;
  hasRating: boolean;
  ratingScore: number;
  reviewsScore: number;
  isOpen: boolean;
}

export interface EnrichedLeadData {
  email?: string;
  social_links?: {
    facebook?: string;
    instagram?: string;
    linkedin?: string;
    twitter?: string;
  };
  description?: string;
  employees_count?: string;
  founded_year?: string;
  industry?: string;
  technologies?: string[];
  enriched_at: string;
}

export interface LeadSearchFilters {
  city: string;
  sector: string;
  radius?: number;
  minRating?: number;
  hasWebsite?: boolean;
  hasPhone?: boolean;
}

export interface AutoPilotConfig {
  enabled: boolean;
  targetCity: string;
  targetSector: string;
  dailyLimit: number;
  autoEnrich: boolean;
  autoSaveToCRM: boolean;
}

export interface LeadCampaignStats {
  total_leads: number;
  enriched: number;
  saved_to_crm: number;
  emails_sent: number;
  responses: number;
  conversion_rate: number;
}

/**
 * Calcola lo score di un lead basato sui suoi dati
 */
export function calculateLeadScore(place: PlaceResult): LeadWithScore {
  let score = 0;
  const details: LeadScoreDetails = {
    hasWebsite: false,
    hasPhone: false,
    hasRating: false,
    ratingScore: 0,
    reviewsScore: 0,
    isOpen: false,
  };

  // Website: +25 punti
  if (place.website) {
    score += 25;
    details.hasWebsite = true;
  }

  // Phone: +20 punti
  if (place.formatted_phone_number) {
    score += 20;
    details.hasPhone = true;
  }

  // Rating: fino a +30 punti
  if (place.rating) {
    details.hasRating = true;
    const ratingPoints = Math.round((place.rating / 5) * 30);
    score += ratingPoints;
    details.ratingScore = ratingPoints;
  }

  // Reviews: fino a +15 punti
  if (place.user_ratings_total) {
    const reviewPoints = Math.min(Math.round(place.user_ratings_total / 10), 15);
    score += reviewPoints;
    details.reviewsScore = reviewPoints;
  }

  // Open now: +10 punti
  if (place.opening_hours?.open_now) {
    score += 10;
    details.isOpen = true;
  }

  return {
    ...place,
    score: Math.min(score, 100),
    scoreDetails: details,
  };
}
