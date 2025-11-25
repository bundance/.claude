---
name: react-reducer-patterns
description: Use when managing complex state with 3+ related variables, prop drilling through multiple components, or needing shared state across a component tree. Covers useReducer, Context, and custom hooks.
---

# React Reducer and Context Patterns

## When to Use This Skill

Use this skill when:
- You have 3+ related state variables that update together
- You're passing state through multiple component layers (prop drilling)
- Multiple components need access to the same state
- State transitions are complex with multiple action types
- You need testable, predictable state logic

## Core Principles

**Centralize complex state logic in pure reducer functions.** Use Context to share state without prop drilling. Create custom hooks to provide clean APIs for state access.

---

## Anti-pattern: Prop Drilling

### The Problem

Passing state through components that don't use it.

```tsx
// ANTI-PATTERN: Prop drilling through multiple levels
function App() {
  const [bookingState, setBookingState] = useState(initialState);
  return (
    <BookingPage
      bookingState={bookingState}
      setBookingState={setBookingState}
    />
  );
}

function BookingPage({ bookingState, setBookingState }) {
  return (
    <FlightForm bookingState={bookingState} setBookingState={setBookingState} />
  );
}

function FlightForm({ bookingState, setBookingState }) {
  // Finally use the state here
}
```

**Why it's problematic:**
- Intermediate components must know about state they don't use
- Refactoring becomes difficult
- Component interfaces become bloated
- Tight coupling throughout the component tree

### The Solution: Context + useReducer

```tsx
// BEST PRACTICE: Context eliminates prop drilling
const BookingContext = createContext<{
  state: BookingState;
  dispatch: (action: BookingAction) => void;
} | null>(null);

function BookingProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(bookingReducer, initialState);
  return (
    <BookingContext.Provider value={{ state, dispatch }}>
      {children}
    </BookingContext.Provider>
  );
}

function FlightForm() {
  const { state, dispatch } = useBooking(); // Direct access
}
```

---

## Pattern: Action-Based State Updates

### Define Clear Action Types

```tsx
type BookingAction =
  | { type: 'submit'; payload: SearchParams }
  | { type: 'results'; flights: FlightOption[] }
  | { type: 'flightSelected'; flightId: string }
  | { type: 'back' }
  | { type: 'error' };
```

### Pure Reducer Function

```tsx
function bookingReducer(
  state: BookingState,
  action: BookingAction
): BookingState {
  switch (action.type) {
    case 'submit':
      return {
        ...state,
        status: 'submitting',
        searchParams: action.payload,
      };
    case 'results':
      return {
        ...state,
        status: 'results',
        flights: action.flights,
      };
    case 'flightSelected':
      if (state.status !== 'results') return state;
      return {
        ...state,
        selectedFlightId: action.flightId,
      };
    case 'back':
      if (state.status === 'results') {
        return { ...state, status: 'idle' };
      }
      return state;
    case 'error':
      return { ...state, status: 'error' };
    default:
      return state;
  }
}
```

**Benefits:**
- Each action clearly describes what happened
- State transitions are explicit and predictable
- Pure function is easy to test
- Action history visible in React DevTools

---

## Pattern: Custom Context Hook

Always create a custom hook for context access with validation.

```tsx
function useBooking() {
  const context = use(BookingContext);
  if (!context) {
    throw new Error('useBooking must be used within BookingProvider');
  }
  return context;
}

// Usage in components
function SearchResults() {
  const { state, dispatch } = useBooking();

  if (state.status !== 'results') return null;

  return (
    <div>
      {state.flights.map(flight => (
        <FlightCard
          key={flight.id}
          flight={flight}
          onSelect={() => dispatch({ type: 'flightSelected', flightId: flight.id })}
        />
      ))}
    </div>
  );
}
```

**Benefits:**
- Better error messages when used outside provider
- Type safety with proper inference
- Single place to add derived state or helpers
- Cleaner component code

---

## Complete Example

```tsx
// types.ts
type BookingState = {
  status: 'idle' | 'submitting' | 'error' | 'results';
  flights: FlightOption[] | null;
  searchParams: SearchParams | null;
};

type BookingAction =
  | { type: 'submit'; payload: SearchParams }
  | { type: 'results'; flights: FlightOption[] }
  | { type: 'back' }
  | { type: 'error' };

// reducer.ts
const initialState: BookingState = {
  status: 'idle',
  flights: null,
  searchParams: null,
};

function bookingReducer(state: BookingState, action: BookingAction): BookingState {
  switch (action.type) {
    case 'submit':
      return { ...state, status: 'submitting', searchParams: action.payload };
    case 'results':
      return { ...state, status: 'results', flights: action.flights };
    case 'back':
      return state.status === 'results' ? { ...state, status: 'idle' } : state;
    case 'error':
      return { ...state, status: 'error' };
    default:
      return state;
  }
}

// context.tsx
const BookingContext = createContext<{
  state: BookingState;
  dispatch: React.Dispatch<BookingAction>;
} | null>(null);

function BookingProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(bookingReducer, initialState);
  return (
    <BookingContext.Provider value={{ state, dispatch }}>
      {children}
    </BookingContext.Provider>
  );
}

function useBooking() {
  const context = use(BookingContext);
  if (!context) throw new Error('useBooking must be used within BookingProvider');
  return context;
}

// components.tsx
function BookingContent() {
  const { state, dispatch } = useBooking();

  const handleSubmit = async (params: SearchParams) => {
    dispatch({ type: 'submit', payload: params });
    try {
      const flights = await searchFlights(params);
      dispatch({ type: 'results', flights });
    } catch {
      dispatch({ type: 'error' });
    }
  };

  return (
    <div>
      {state.status !== 'results' ? (
        <BookingForm onSubmit={handleSubmit} />
      ) : (
        <SearchResults onBack={() => dispatch({ type: 'back' })} />
      )}
      {state.status === 'error' && <ErrorMessage />}
    </div>
  );
}
```

---

## Quick Reference

### When to Use useReducer vs useState

| Scenario | Use |
|----------|-----|
| Single value, simple updates | `useState` |
| Multiple related values | `useReducer` |
| Complex update logic | `useReducer` |
| State depends on previous state | `useReducer` |
| Need testable state logic | `useReducer` |

### Reducer Best Practices

1. **Pure functions only** - no side effects in reducers
2. **Return new state** - never mutate the existing state
3. **Handle unknown actions** - return current state for unrecognized actions
4. **Type your actions** - use discriminated unions for type safety
5. **Keep reducers focused** - split large reducers by domain

### Context Best Practices

1. **Create custom hooks** - never use `useContext` directly in components
2. **Validate context** - throw helpful errors when used outside provider
3. **Split contexts** - separate frequently changing state from stable state
4. **Memoize provider value** - prevent unnecessary re-renders

---

## Related Skills

- **react-state-machines** - For discriminated unions in your reducer state
- **react-state-libraries** - When Context performance becomes a problem
- **react-state-testing** - For testing your reducer logic in isolation
