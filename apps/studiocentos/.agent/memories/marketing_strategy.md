# Marketing & Design Strategy

## 1. The "Premium" Aesthetic
StudioCentOS is a **luxury digital agency**. Our design language reflects this.
- **Palette**:
    - **Black**: The canvas. Use deep, rich blacks (`#0A0A0A`, `#000000`) instead of generic gray.
    - **Gold**: The accent. Use gold for borders, primary buttons, and key text highlights.
    - **Gradients**: Use subtle gold-to-yellow gradients for buttons (`bg-gradient-to-r from-gold to-yellow-600`).
- **Typography**: Clean, sans-serif (Inter/Outfit). High contrast headlines.
- **Interactions**: Smooth transitions (`duration-300`), hover effects that glow or lift.

## 2. Copywriting Voice
- **Tone**: Professional, Authoritative, Innovative.
- **Keywords**: "AI-Driven", "Enterprise", "Scalable", "Dominance", "Automated".
- **Avoid**: "Cheap", "Quick fix", "Basic". We sell *solutions* and *futures*, not just websites.

## 3. SEO Strategy
- **Focus**: High-ticket keywords ("Enterprise AI Development", "Office AI Consulting", "Custom Web Application").
- **Technical Rules**:
    - **SSL**: Every domain MUST have its dedicated certificate path in Nginx. No certificate sharing.
    - **Soft 404**: Block invalid paths (vulnerabilities, junk slugs) directly at the Nginx level with `404` or `410`.
    - **Frontend**: Force `noindex` meta tag on the `NotFound` page to ensure SPA errors aren't indexed.
- **Tools**: GA4, Google Search Console.

## 4. Office AI Philosophy
- **Dev-Tools for Professionals**: We adapt IDEs (VS Code/Cursor) and advanced LLM interfaces for non-devs.
- **Workflows**: Move clients from generic ChatGPT use to structured, dialogue-based prompting within a custom-tailored IDE environment.
- **Premium Consultancy**: We sell the setup and the training, not just the software.

## 5. Social Media
- **Channels**: LinkedIn (Technical/Professional), Instagram (Premium Portfolio).
- **Tone**: Authoritative, visionary, results-oriented.
