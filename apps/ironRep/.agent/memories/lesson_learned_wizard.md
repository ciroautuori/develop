# Lesson Learned: Visual Hybrid Wizard vs Pure Chat

## Context
Initial attempts to build a "Pure Chat" wizard for complex attributes (Injuries, Nutrition Preferences) failed to provide a robust user experience. Users found it tedious to type out details, and the agent struggled to structure this data consistently.

## Solution: Visual Smart Hybrid
We moved to a hybrid model:
1.  **Orchestrator**: Manages the flow.
2.  **Conditional Visual Components**: `InjuryDetailsStep` and `FoodPreferencesStep` are standard React forms. They appear only when needed (based on intake flags).
3.  **Agent Trust**: The backend agent is configured to "trust" this pre-collected data and skip redundant interview phases (`PAIN_ASSESSMENT`, `NUTRITION_DETAILS`).

## Key Takeaway
For structured, high-stakes data (Medical, Diet Constraints), **Visual UI > Chat**.
Use Chat only for refinement, motivation, and open-ended queries ("What is your goal?").
