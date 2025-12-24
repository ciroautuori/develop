# Golden Rules for Agent Behavior

These rules are NON-NEGOTIABLE. They define how you must operate to ensure safety, reliability, and code quality.

## 1. Zero Hallucinations
- **Never guess** functionality or file paths.
- **Always verify** existence of files before editing (`list_dir`, `find`).
- **Always read** file content before replacing (`view_file`).
- If a tool fails, **stop and investigate**, do not make up a success.

## 2. No Blind Behavior
- Do not execute commands without understanding the context.
- Do not write code that assumes dependencies (like `fastapi` or specific modules) without verifying they are installed or importing them correctly.
- If you see a `ModuleNotFoundError` or `ImportError`, fix the import or environment, do not ignore it.

## 3. Error Prevention
- **Test your code**: Whenever possible, run a manual test script (like `manual_test_*.py`) to verify backend logic.
- **Check consistency**: Ensure new code matches existing patterns (e.g., Use `_get_llm_response` helper in Agents).
- **Type Safety**: Use correct type hints (`List`, `Dict`, `Any`, `Optional`).

## 4. UI/UX Consistency (Premium)
- **Aesthetic**: All new UI components must match the **StudioCentOS Premium** style (`Gold/Black` palette).
- **Styling**: Use `text-gold`, `border-gold`, `bg-gold/10` for accents.
- **Quality**: No "basic" designs. Components must look professional and high-end.

## 5. RAG & Knowledge
- Treat this `.agent` directory as your Source of Truth.
- Update these files if you learn something new about the system.
- Consult `agent_registry.md` and `marketing_strategy.md` before making decisions in those domains.
