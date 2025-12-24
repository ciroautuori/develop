# Memory: LangChain Introspection Bug & BaseTool Fix
**Date**: 2025-12-24
**Component**: Backend / LLM Service
**Severity**: Critical

## The Problem
A `NameError: name 'BaseTool' is not defined` (and similar errors for `Runnable`, `BaseMessage`) occurred when initializing `WizardAgent` or any agent using `RunnableWithFallbacks` in LangChain. This happened during LangChain's internal introspection (`typing.get_type_hints`) because the primitives were not visible in the global namespace of the module being inspected.

## The Solution
1. **Global Monkeypatch**: In `main.py`, we inject `BaseTool` and other primitives into `typing` and global namespaces. This acts as a safety against introspection failures.
2. **Bypass Introspection**: In `llm_service.py`, we discovered that avoiding `with_fallbacks` wrapper or manually handling `bind_tools` prevents the buggy `__getattr__` recursion.
3. **Provider Selection**: `ChatOllama` (local) does not natively support `bind_tools` in older versions. We MUST use `ChatGroq` or a newer wrapper as the primary provider for tool-calling agents.

## Lessons Learned
- **Verify Introspection**: Complex Pydantic/LangChain wrappers often break introspection. Explicit imports or global injections are necessary.
- **Provider Capabilities**: Always test if a provider (`Ollama` vs `Groq`) supports the specific method (`bind_tools`) before making it primary.
- **Timeout Management**: Local LLMs need significantly higher timeouts (300s+) for the first load.

## Code Pattern to Maintain
When defining chains with fallbacks:
```python
# Safer fallback handling if introspection causes issues
return primary # Direct return if fallbacks are causing NameErrors
# OR ensure BaseTool is globally injected BEFORE this runs
```
