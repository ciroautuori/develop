# Architecture Decision Records (ADR)

## ADR-001: Centralized Logging Strategy

**Date**: 2025-11-25
**Status**: ✅ Implemented

### Context
The application had inconsistent logging with `print()` statements in Python and `console.log/error` in TypeScript scattered throughout the codebase.

### Decision
Implement centralized logging infrastructure:
- **Backend**: Python logger with structured logging
- **Frontend**: TypeScript logger with environment-aware behavior
- Replace all ad-hoc logging with centralized logger

### Consequences
**Positive**:
- Consistent log format across application
- Easy to configure log levels
- Better production debugging
- Logs can be aggregated easily

**Negative**:
- Requires discipline to use logger instead of console
- Migration effort for existing codebase

---

## ADR-002: TypeScript Strict Mode & Type Safety

**Date**: 2025-11-25
**Status**: ✅ Implemented (95%)

### Context
Codebase had 20+ instances of `any` types, reducing type safety and IntelliSense effectiveness.

### Decision
- Define strict interfaces for all data structures
- Eliminate `any` types (target: 95%+)
- Use proper TypeScript types throughout

### Consequences
**Positive**:
- Better IDE support and autocomplete
- Catch errors at compile time
- Easier refactoring
- Self-documenting code

**Negative**:
- More upfront type definition work
- Some legitimate `any` cases (e.g., event handlers)

---

## ADR-003: Session-Based Token Storage

**Date**: 2025-11-25
**Status**: ✅ Implemented

### Context
Authentication tokens were stored in `localStorage`, persisting across browser sessions and increasing XSS attack surface.

### Decision
- Migrate from `localStorage` to `sessionStorage`
- Create `useAuthStorage` hook for centralized access
- Tokens auto-clear on tab close

### Consequences
**Positive**:
- Reduced XSS attack surface
- Better security posture
- Automatic cleanup on session end
- Centralized token management

**Negative**:
- Users need to re-login on new tabs (acceptable tradeoff)
- Slightly more friction in UX

---

## ADR-004: React Performance Optimization Strategy

**Date**: 2025-11-25
**Status**: ✅ Implemented

### Context
Application had unnecessary re-renders due to lack of memoization.

### Decision
- Use `React.memo` for expensive components
- Use `useCallback` for functions passed as props
- Use `useMemo` for expensive computations
- Apply to 5 critical components initially

### Consequences
**Positive**:
- Reduced re-renders
- Better performance
- More responsive UI

**Negative**:
- Slightly more complex code
- Need to manage dependency arrays carefully

---

## ADR-005: Immutable State Updates in Zustand

**Date**: 2025-11-25
**Status**: ✅ Implemented

### Context
`mealPlannerStore` had direct state mutations, making state changes unpredictable.

### Decision
- Always use spread operators for updates
- Never mutate state directly
- Return new objects/arrays

### Consequences
**Positive**:
- Predictable state updates
- Easier debugging
- Better DevTools support

**Negative**:
- Slightly more verbose code

---

## ADR-006: Centralized API Error Handling

**Date**: 2025-11-25
**Status**: ✅ Implemented

### Context
Error handling was inconsistent across API calls, with different error message formats.

### Decision
- Create `apiErrorHandler` utility
- Implement automatic retry logic
- Classify errors (auth, validation, network)
- Provide user-friendly messages

### Consequences
**Positive**:
- Consistent error handling
- Better UX with clear messages
- Automatic retries for transient failures
- Centralized logging

**Negative**:
- More abstraction to learn

---

## ADR-007: Accessibility-First Approach

**Date**: 2025-11-25
**Status**: ✅ Implemented

### Context
Application lacked proper ARIA labels and keyboard navigation support.

### Decision
- Create accessibility utilities
- ARIA labels for all interactive elements
- Keyboard navigation support
- Screen reader announcements
- Focus management

### Consequences
**Positive**:
- Inclusive design
- Better UX for all users
- Legal compliance (accessibility laws)
- SEO benefits

**Negative**:
- Additional development time
- More testing required

---

## Template for New ADRs

```markdown
## ADR-XXX: Title

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Implemented | Rejected

### Context
Why is this decision needed?

### Decision
What did we decide?

### Consequences
**Positive**:
- Benefits

**Negative**:
- Drawbacks
```
