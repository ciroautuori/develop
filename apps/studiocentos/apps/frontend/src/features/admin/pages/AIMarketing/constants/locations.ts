/**
 * Costanti geografiche centralizzate per Marketing Hub
 * @module constants/locations
 */

export const ITALIAN_CITIES = [
  'Roma', 'Milano', 'Napoli', 'Torino', 'Palermo',
  'Genova', 'Bologna', 'Firenze', 'Bari', 'Catania',
  'Venezia', 'Verona', 'Messina', 'Padova', 'Trieste',
  'Taranto', 'Brescia', 'Prato', 'Reggio Calabria', 'Modena',
  'Salerno', 'Benevento', 'Caserta', 'Avellino'
] as const;

export const ITALIAN_REGIONS = [
  'Campania', 'Lazio', 'Lombardia', 'Piemonte', 'Veneto',
  'Emilia-Romagna', 'Toscana', 'Sicilia', 'Puglia', 'Calabria',
  'Sardegna', 'Liguria', 'Marche', 'Abruzzo', 'Friuli-Venezia Giulia',
  'Trentino-Alto Adige', 'Umbria', 'Basilicata', 'Molise', "Valle d'Aosta"
] as const;

export const TARGET_REGIONS = [
  'Salerno', 'Napoli', 'Campania', 'Roma', 'Milano', 'Italia'
] as const;

export type ItalianCity = typeof ITALIAN_CITIES[number];
export type ItalianRegion = typeof ITALIAN_REGIONS[number];
export type TargetRegion = typeof TARGET_REGIONS[number];
