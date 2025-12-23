# Implementation Plan: Courses Section (Corso Tool AI)

## Goal
Integrate a new high-impact section on the Landing Page to showcase the "Corso Tool AI".
This section will serve as a catalog for the educational modules, driving traffic to external purchasing pages (e.g., Gumroad, Stripe Payment Links) to avoid implementing internal payment logic.

## Design Concept
- **Visual Style**: "Netlfix-style" horizontal scroll or Grid Layout. Premium, dark mode aesthetics (Gold/Black).
- **Card Content**:
    - Module Identification (e.g., "01_META_GAME").
    - Title & Subtitle.
    - Dynamic "AI-Generated" badge (since lessons are AI-orchestrated).
    - Call to Action: "Inizia Ora" / "Scopri" (External Link).

## Component Architecture

### 1. Data Structure (`courses.data.ts`)
Define the course modules based on the analyzed file structure:
```typescript
export const COURSE_MODULES = [
  {
    id: 'meta-game',
    code: '01',
    title: 'META GAME',
    description: 'La Genesi. Come l\'AI ha costruito questo corso. Mindset e Orchestrazione.',
    icon: 'Brain', // Lucide icon
    link: 'https://...', // External placeholder
  },
  {
    id: 'fondamenta',
    code: '02',
    title: 'FONDAMENTA DIGITALI',
    description: 'Workspace ISO 8601, Obsidian, Notion. La base del tuo Secondo Cervello.',
    icon: 'Database',
    link: 'https://...',
  },
  // ... others (Visual Wow, Google Eco, Automazione, LLM Brains, Metodo)
];
```

### 2. UI Component (`CoursesSection.tsx`)
- **Location**: `apps/frontend/src/features/landing/components/CoursesSection.tsx`
- **Animation**: Use `framer-motion` for reveal effects.
- **Layout**: 
    - Section Title: "Corso Tool AI"
    - Subtitle: "L'unico corso aggiornato in tempo reale da Agenti AI."
    - Grid of Cards.

### 3. Integration ([StudiocentosLanding.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/landing/StudiocentosLanding.tsx))
- Add `<CoursesSection />` between `Services` and `Projects` (or [ToolAI](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/landing/components/ToolAISection.tsx#41-188)).
- Ensure navigation anchor `#corsi` works.

## Step-by-Step Implementation

1.  **Create Data File**: `apps/frontend/src/features/landing/data/courses.ts`
2.  **Create Component**: `apps/frontend/src/features/landing/components/CoursesSection.tsx`
3.  **Update Landing Page**: Import and place the section in [StudiocentosLanding.tsx](file:///home/autcir_gmail_com/studiocentos_ws/apps/frontend/src/features/landing/StudiocentosLanding.tsx).
4.  **Update Header**: Add "Corsi" link in navigation (optional, or just part of Services).

## Verification
- Check responsiveness (Mobile/Desktop).
- Verify external links open in new tabs.
- Verify design consistency with "Gold/Black" theme.
