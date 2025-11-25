---
name: react-state-machines
description: Use when modeling component states with multiple boolean flags (isLoading, isError, isSuccess) or status-dependent logic. Covers discriminated unions and type states to make impossible states impossible.
---

# React State Machines and Type States

## When to Use This Skill

Use this skill when:
- You have multiple boolean flags for state (isLoading, isError, isSuccess)
- Different data is available in different states
- You need to prevent impossible state combinations
- You're building multi-step flows or wizards
- Conditional rendering depends on a status value

## Core Principle

**Make impossible states impossible.** Rather than using multiple boolean flags that can create invalid combinations, use discriminated unions to define exactly which states are valid and what data is available in each.

---

## Anti-pattern: Multiple Boolean Flags

### The Problem

Boolean flags can combine in ways that don't make sense.

```tsx
// ANTI-PATTERN: Boolean flags create impossible states
function FlightSearch() {
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);
  const [data, setData] = useState<Flight[] | null>(null);

  // What if isLoading AND isError are both true?
  // What if data exists but isLoading is true?
  // These are "impossible states" that your code must handle

  const handleSearch = async () => {
    setIsLoading(true);
    setIsError(false); // Must remember to reset
    try {
      const flights = await searchFlights();
      setData(flights);
    } catch {
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Conditional logic becomes complex
  if (isLoading) return <Spinner />;
  if (isError) return <Error />;
  if (data) return <Results data={data} />;
  return <EmptyState />;
}
```

**Why it's problematic:**
- 3 booleans = 8 possible combinations, most are invalid
- Must manually keep flags in sync
- Easy to forget to reset a flag
- TypeScript can't help prevent invalid states
- Conditional rendering logic becomes complex

### The Solution: Discriminated Unions

Use a single state with a `status` field that determines what other data is available.

```tsx
// BEST PRACTICE: Discriminated union prevents impossible states
type FlightSearchState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'success'; flights: Flight[] };

function FlightSearch() {
  const [state, setState] = useState<FlightSearchState>({ status: 'idle' });

  const handleSearch = async () => {
    setState({ status: 'loading' });
    try {
      const flights = await searchFlights();
      setState({ status: 'success', flights });
    } catch (e) {
      setState({ status: 'error', error: e.message });
    }
  };

  // TypeScript knows exactly what's available in each branch
  switch (state.status) {
    case 'idle':
      return <SearchForm onSearch={handleSearch} />;
    case 'loading':
      return <Spinner />;
    case 'error':
      return <Error message={state.error} />; // error is available
    case 'success':
      return <Results flights={state.flights} />; // flights is available
  }
}
```

**Benefits:**
- Only 4 valid states, not 8 combinations
- TypeScript enforces correct data access
- No way to have `flights` during `loading`
- No forgotten flag resets
- Self-documenting state logic

---

## Combining Form Data with Status

For forms with associated loading states, combine the form data with the status discriminated union.

### Anti-pattern: Separate Form and Status State

```tsx
// ANTI-PATTERN: Separate states that should be combined
const [destination, setDestination] = useState('');
const [departure, setDeparture] = useState('');
const [passengers, setPassengers] = useState(1);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [flights, setFlights] = useState<Flight[] | null>(null);
const [selectedFlightId, setSelectedFlightId] = useState<string | null>(null);

// 7 separate state variables to coordinate!
```

### Best Practice: Combined State Object with Type State

```tsx
// Form data that exists in all states
interface FlightFormData {
  destination: string;
  departure: string;
  arrival: string;
  passengers: number;
  isRoundtrip: boolean;
  selectedFlightId: string | null;
}

// Combine form data with status-specific data
type FlightState = FlightFormData & (
  | { status: 'idle' }
  | { status: 'submitting'; selectedFlightId: null }
  | { status: 'error' }
  | { status: 'success'; flights: FlightOption[] }
);

function FlightBooking() {
  const [state, setState] = useState<FlightState>({
    status: 'idle',
    destination: '',
    departure: '',
    arrival: '',
    passengers: 1,
    isRoundtrip: false,
    selectedFlightId: null,
  });

  // Derive selected flight from flights array and ID
  const selectedFlight =
    state.status === 'success' && state.selectedFlightId
      ? state.flights.find((f) => f.id === state.selectedFlightId)
      : null;

  // Derive total price
  const totalPrice = selectedFlight
    ? selectedFlight.price * state.passengers
    : 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setState((prev) => ({
      ...prev,
      status: 'submitting',
      selectedFlightId: null,
    }));

    try {
      const flights = await searchFlights(state);
      setState((prev) => ({ ...prev, status: 'success', flights }));
    } catch {
      setState((prev) => ({ ...prev, status: 'error' }));
    }
  };

  // Type-safe selection handler
  const handleFlightSelect = (flight: FlightOption) => {
    setState((prev) =>
      prev.status === 'success'
        ? { ...prev, selectedFlightId: flight.id }
        : prev
    );
  };
}
```

---

## Type Guards for Conditional Rendering

Use the status field to guard your rendering logic.

```tsx
function FlightBooking() {
  const [state, setState] = useState<FlightState>({ status: 'idle', ... });

  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* Form fields always available */}
        <input value={state.destination} onChange={...} />

        <button disabled={state.status === 'submitting'}>
          {state.status === 'submitting' ? 'Searching...' : 'Search'}
        </button>
      </form>

      {/* Error only when status is 'error' */}
      {state.status === 'error' && (
        <div className="error">Search failed. Please try again.</div>
      )}

      {/* Flights only when status is 'success' */}
      {state.status === 'success' && state.flights.length > 0 && (
        <FlightResults
          flights={state.flights}
          selectedId={state.selectedFlightId}
          onSelect={handleFlightSelect}
        />
      )}
    </div>
  );
}
```

---

## Common Type State Patterns

### Async Operation States

```tsx
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'pending' }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: T };
```

### Multi-Step Form/Wizard

```tsx
type WizardState =
  | { step: 'personal'; data: PersonalInfo }
  | { step: 'payment'; data: PersonalInfo & PaymentInfo }
  | { step: 'confirmation'; data: CompleteOrder }
  | { step: 'complete'; orderId: string };
```

### Modal/Dialog States

```tsx
type ModalState =
  | { isOpen: false }
  | { isOpen: true; mode: 'create' }
  | { isOpen: true; mode: 'edit'; itemId: string }
  | { isOpen: true; mode: 'delete'; itemId: string };
```

### Authentication States

```tsx
type AuthState =
  | { status: 'unauthenticated' }
  | { status: 'authenticating' }
  | { status: 'authenticated'; user: User }
  | { status: 'error'; error: string };
```

---

## State Transition Rules

With type states, transitions become explicit and type-safe.

```tsx
// Type-safe state transitions
const handleFlightSelect = (flight: FlightOption) => {
  setState((prev) => {
    // Can only select when we have flights
    if (prev.status !== 'success') return prev;

    return {
      ...prev,
      selectedFlightId: flight.id,
    };
  });
};

const handleBack = () => {
  setState((prev) => {
    // Can only go back from success to idle
    if (prev.status !== 'success') return prev;

    return {
      ...prev,
      status: 'idle',
    };
  });
};
```

---

## Quick Reference

### Boolean Flags → Discriminated Union

| Before | After |
|--------|-------|
| `isLoading`, `isError`, `data` | `{ status: 'idle' \| 'loading' \| 'error' \| 'success', ... }` |
| `isOpen`, `isEditing`, `itemId` | `{ mode: 'closed' \| 'create' \| 'edit', itemId?: string }` |
| `step1Done`, `step2Done`, `step3Done` | `{ step: 1 \| 2 \| 3 \| 'complete' }` |

### Type State Checklist

1. Identify all possible states your component can be in
2. Determine what data is available in each state
3. Define a discriminated union type with a `status` or `step` field
4. Each union member contains only the data available in that state
5. Use type guards (`state.status === 'success'`) before accessing state-specific data

### When NOT to Use Type States

- Simple boolean toggles (e.g., `isOpen` for a simple modal)
- Unrelated state that doesn't need to be coordinated
- When the overhead of the union type isn't worth the benefit

---

## Related Skills

- **react-state-antipatterns** - For the foundational principle of minimal state
- **react-reducer-patterns** - For implementing type states with useReducer
- **react-state-testing** - Type states make testing state transitions trivial
