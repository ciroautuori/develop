/**
 * Export centralizzato delle costanti Marketing Hub
 *
 * Sistema POTENTE completo per marketing multi-piattaforma
 *
 * NOTE: Per evitare conflitti tra moduli che definiscono tipi simili,
 * importiamo direttamente dai moduli specifici quando necessario.
 *
 * @module constants
 */

// ============================================================================
// Re-export separati per tipi e valori
// ============================================================================

// Brand DNA - SOURCE OF TRUTH per identità brand
export * from './brand-dna';

// Platforms - SINGLE SOURCE OF TRUTH per piattaforme
export * from './platforms';

// Tones - SINGLE SOURCE OF TRUTH per toni
export * from './tones';

// Platform Rules
export * from './platform-format-rules';

// Media Sizes
export * from './image-sizes';
export * from './video-platforms';

// Other Constants
export * from './locations';
export * from './industries';
export * from './email-styles';

// ============================================================================
// NOTA: ai-prompts e quick-templates hanno tipi duplicati (PostType, SocialPlatform)
// Importa direttamente dal modulo specifico quando necessario:
//
// import { PostType, SYSTEM_PROMPT_BASE } from './constants/ai-prompts';
// import { SOCIAL_QUICK_TEMPLATES, QuickTemplate } from './constants/quick-templates';
// ============================================================================
