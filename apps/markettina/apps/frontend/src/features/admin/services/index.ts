/**
 * Marketing Services
 * Centralized exports for all marketing-related API services
 */

export { MarketingApiService } from './marketing-api.service';
export type {
  ContentParams,
  ContentResult,
  ImageParams,
  ImageResult,
  PublishParams,
  PublishResult,
  ScheduledPost,
  PostFilters,
  CreatePostDto,
  UpdatePostDto,
} from './marketing-api.service';

export { LeadApiService } from './lead-api.service';
export type { Lead, LeadSearchParams, Customer } from './lead-api.service';

export { AIChatService } from './ai-chat.service';
export type { ChatMessage, ChatResponse } from './ai-chat.service';
