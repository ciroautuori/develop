/**
 * Costanti settori business centralizzate per Marketing Hub
 * @module constants/industries
 */

export const BUSINESS_SECTORS = [
  'Ristorazione',
  'Hotel & Turismo',
  'Retail & Commercio',
  'Servizi Professionali',
  'Sanità & Wellness',
  'Beauty & Estetica',
  'Automotive',
  'Immobiliare',
  'Tecnologia & IT',
  'Consulenza',
  'Formazione',
  'E-commerce',
  'Artigianato',
  'Agricoltura',
  'Manifattura',
] as const;

export const TARGET_INDUSTRIES = [
  'Software & IT',
  'E-commerce',
  'Fintech',
  'Healthcare',
  'Real Estate',
  'Manufacturing',
  'Retail',
  'Professional Services',
  'Ristorazione',
  'Hotel & Turismo',
  'Beauty & Wellness',
  'Automotive',
] as const;

export type BusinessSector = typeof BUSINESS_SECTORS[number];
export type TargetIndustry = typeof TARGET_INDUSTRIES[number];
