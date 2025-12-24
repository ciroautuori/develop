# Wizard Refactoring Proposals

## Problem Analysis
The current Wizard flow is disjointed: `Forms (Biometrics, Goals, Lifestyle)` → `Chat (Agent)` → `Forms (Injury, Food, Strength)`.
This causes:
1.  **Redundancy**: User fills forms, then Agent might cover overlap, then more forms appear.
2.  **Friction**: The "Injury Report" appearing at the end feels forced, even if discussed or irrelevant.
3.  **Duplication**: Frontend Orchestrator logic and Backend Agent logic compete for control of the flow.

## Proposal 1: "Chat-First" (Agentic Native)
**Philosophy**: The Agent is the ONLY interface. Forms are injected *inside* the chat only when needed (Generative UI).
**Flow**:
1.  **Greeting**: Agent starts immediately. "Hi [Name], welcome back. Do you have any injuries today?"
2.  **Dynamic Collection**:
    *   Agent asks questions based on missing data.
    *   *Constraint*: If structured data is crucial (e.g. detailed strength stats), the Agent renders a "Mini-Form Widget" in the chat stream, not a separate page step.
3.  **Completion**: Once the Agent is satisfied, it calls `complete_onboarding` directly.
**Pros**: Maximum flexibility, natural conversation, zero "step" fatigue.
**Cons**: Requires robust Generative UI (rendering React components from Agent tool calls).

## Proposal 2: "Smart Hybrid" (Context-Aware Pre-fill)
**Philosophy**: Keep the robust steps but strictly deduplicate using shared state. The "Injury" step at the end is REMOVED and integrated into the Chat or the initial Goals step.
**Flow**:
1.  **Unified Intake Form (Page 1)**: Syncs everything available (Google Fit, previous data). Asks *only* the absolute basics: Biometrics + "Do you have an injury?" toggle.
    *   *If Injury=Yes*: Expands "Injury Details" right there (Dynamic Form).
2.  **Agent Interview (Page 2)**: The Agent receives the *full* context from Page 1.
    *   Agent validates/refines plans. "I see you have a back injury. I've adjusted the plan. Any food preferences?"
3.  **Completion**: No post-chat steps. The Chat *is* the final step.
**Pros**: Removes the "End of Wizard" friction. Captures critical structured data (Medical) early and reliably via UI.

## Proposal 3: "Invisible Wizard" (Data-Driven)
**Philosophy**: "Don't ask, just generate." Rely heavily on default assumptions and APIs, minimize questions.
**Flow**:
1.  **One-Click Start**: User lands, we pull Google Fit/Apple Health.
2.  **Dashboard First**: User is dropped immediately into the Dashboard with a "Draft Plan".
3.  **Refinement Mode**: The Agent lives in the Dashboard sidebar. "I created a standard plan. Want to customize it? Tell me about injuries or goals."
**Pros**: Fastest time-to-value. Zero friction.
**Cons**: Initial plan might be generic/wrong if user has critical unchecked constraints (e.g., injury).

## Recommendation
**Proposal 2 (Smart Hybrid)** is the safest and most robust immediate fix for the "Injury Report at the end" complaint. It moves the critical structured health data to the *start* (where it belongs contextually) or handles it entirely within the chat, ensuring the end of the chat = end of process.
