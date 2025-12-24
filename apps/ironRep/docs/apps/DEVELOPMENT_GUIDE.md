# IronRep Frontend - Development Guide

## Table of Contents
- [Architecture](#architecture)
- [Code Style](#code-style)
- [Component Guidelines](#component-guidelines)
- [State Management](#state-management)
- [Testing](#testing)
- [Accessibility](#accessibility)

## Architecture

### Tech Stack
- **React 19**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **TanStack Router**: Routing
- **TanStack Query**: Server state
- **Zustand**: Client state
- **Tailwind CSS**: Styling

### Project Structure
```
src/
├── components/        # Shared components
├── features/         # Feature modules
│   ├── auth/
│   ├── chat/
│   ├── workout/
│   └── ...
├── lib/              # Utilities
├── hooks/            # Custom hooks
├── routes/           # Route components
└── stores/           # Zustand stores
```

## Code Style

### TypeScript Guidelines
1. **No `any` types** - Use proper interfaces
2. **Strict null checks** - Handle undefined/null explicitly
3. **Functional components** - Use hooks, avoid classes (except ErrorBoundary)
4. **Named exports** - Prefer named over default exports

### Component Structure
```typescript
// 1. Imports
import { useState } from 'react';
import { Button } from '../components/Button';

// 2. Types/Interfaces
interface MyComponentProps {
  title: string;
  onSubmit: (data: FormData) => void;
}

// 3. Component
export function MyComponent({ title, onSubmit }: MyComponentProps) {
  // 4. Hooks
  const [state, setState] = useState('');

  // 5. Handlers
  const handleClick = () => {
    // logic
  };

  // 6. Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

## Component Guidelines

### Performance
- Use `React.memo` for expensive components
- Use `useCallback` for functions passed as props
- Use `useMemo` for expensive computations
- Avoid inline object/array creation in JSX

### Error Handling
- Wrap main app in `ErrorBoundary`
- Use try-catch for async operations
- Log errors with centralized logger
- Show user-friendly error messages

### Loading States
- Use `LoadingSpinner` component
- Show skeleton loaders for better UX
- Handle loading states explicitly

## State Management

### When to use what
- **useState**: Local component state
- **TanStack Query**: Server state (API data)
- **Zustand**: Global client state
- **Context**: Dependency injection (auth, theme)

### Zustand Best Practices
```typescript
// ✅ Good: Immutable updates
set((state) => ({
  items: [...state.items, newItem]
}));

// ❌ Bad: Direct mutation
set((state) => {
  state.items.push(newItem);
  return state;
});
```

## Testing

### Test Structure
```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

describe('MyComponent', () => {
  it('should render title', () => {
    render(<MyComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

### Testing Utilities
- Use `testUtils` for mocks and helpers
- Mock API calls with MSW
- Mock storage with `mockSessionStorage`

## Accessibility

### ARIA Labels
```typescript
import { generateAriaId } from '../lib/accessibility';

const labelId = generateAriaId('input');

<label id={labelId}>Name</label>
<input aria-labelledby={labelId} />
```

### Keyboard Navigation
- All interactive elements must be keyboard accessible
- Use `tabindex="0"` for custom interactive elements
- Implement focus trapping in modals
- Use semantic HTML (`<button>`, `<a>`, etc.)

### Screen Readers
```typescript
import { announceToScreenReader } from '../lib/accessibility';

// Announce success
announceToScreenReader('Workout saved successfully');
```

## API Integration

### Using HTTP Client
```typescript
import { get, post } from '../lib/httpClient';

// GET request with automatic retry
const data = await get<WorkoutData>('/api/workouts/today');

// POST request with error handling
try {
  const result = await post('/api/workouts', { data });
} catch (error) {
  const message = getErrorMessage(error);
  toast.error(message);
}
```

### Error Handling
```typescript
import { handleApiError, isAuthError } from '../lib/apiErrorHandler';

try {
  await api.call();
} catch (error) {
  if (isAuthError(error)) {
    // Redirect to login
    navigate('/login');
  } else {
    const apiError = handleApiError(error);
    toast.error(apiError.message);
  }
}
```

## Form Validation

```typescript
import { validateEmail, validatePassword } from '../lib/validation';

const errors = validatePassword(password);
if (!errors.isValid) {
  setFormErrors(errors.errors);
  return;
}
```

## Best Practices

1. **Always use TypeScript** - No plain JS files
2. **Centralized logging** - Use `logger` instead of `console.log`
3. **Error boundaries** - Wrap features in error boundaries
4. **Accessibility first** - ARIA labels, keyboard navigation
5. **Performance** - Memoization, code splitting
6. **Testing** - Write tests for critical paths
7. **Documentation** - Comment complex logic

## Common Patterns

### Loading Pattern
```typescript
if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;
return <Content data={data} />;
```

### Form Pattern
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  const result = validateForm(values, rules);
  if (!result.isValid) {
    setErrors(result.errors);
    return;
  }

  try {
    await post('/api/endpoint', values);
    toast.success('Success!');
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
};
```

---

**Questions?** Check existing code for examples or ask the team!
