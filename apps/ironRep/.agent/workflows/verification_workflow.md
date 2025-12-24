---
description: How to verify the Visual Smart Hybrid Wizard logic
---

# Verification Workflow: Visual Smart Hybrid

When modifying `WizardAgent` or `WizardOrchestrator`, you MUST verify the logic flow to ensure no regressions in the "Smart Skip" behavior.

## 1. Environment Check
Ensure `.env` in `apps/backend` contains valid API keys.

## 2. Run Verification Script
Use the dedicated verification script to simulate frontend payloads.

```bash
# From apps/backend root or project root (adjust PYTHONPATH)
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 verify_visual_hybrid_flow.py
```

## 3. Expected Output
Look for **SUCCESS** logs:
- `INFO: ✅ SUCCESS: Agent skipped PAIN_ASSESSMENT`
- `INFO: ✅ SUCCESS: Agent skipped NUTRITION_DETAILS`

## 4. Troubleshooting
If the script fails with `ModuleNotFoundError`, ensure `apps/backend` is in your `PYTHONPATH`.
If the script fails with `ImportError`, check for circular imports in `wizard_agent.py`.
