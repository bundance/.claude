---
name: react-state-testing
description: Use when testing state management logic, reducers, or business rules. Covers testing pure reducer functions, state transitions, and business logic in isolation without rendering components.
---

# Testing App Logic

## When to Use This Skill

Use this skill when:
- Writing tests for reducers or state logic
- Testing business rules and validation
- Verifying state transitions in multi-step flows
- Testing derived state calculations
- You want fast, reliable tests without component rendering

## Core Principle

**Test your business logic, not your UI implementation.** Extract state logic into pure reducer functions that can be tested in isolation. Pure functions are deterministic, fast to test, and don't require mocking React hooks or DOM interactions.

---

## Anti-pattern: Testing Mixed UI/Logic

### The Problem

Testing state logic through component rendering is slow and brittle.

```tsx
// ANTI-PATTERN: Testing logic through component
function BookingForm() {
  const [step, setStep] = useState('search');
  const [flight, setFlight] = useState(null);
  const [hotel, setHotel] = useState(null);

  const handleFlightSelect = (selectedFlight) => {
    setFlight(selectedFlight);
    setStep('hotel');
  };

  // Business logic mixed with UI...
}

// Brittle test - requires rendering and DOM interactions
test('should move to hotel step after flight selection', async () => {
  render(<BookingForm />);

  // Find and click a flight... complex DOM queries
  const flightCard = screen.getByTestId('flight-123');
  fireEvent.click(flightCard);

  // Assert DOM changed
  await waitFor(() => {
    expect(screen.getByText('Select Hotel')).toBeInTheDocument();
  });
});
```

**Why it's problematic:**
- Slow: Renders full component tree
- Brittle: Breaks when UI changes
- Complex: Requires DOM queries and async waits
- Incomplete: Hard to test edge cases
- Coupled: Tests break for unrelated UI changes

---

## Best Practice: Test Pure Reducers

### Extract Business Logic

```tsx
// bookingReducer.ts
type BookingState = {
  step: 'search' | 'flights' | 'hotels' | 'confirm';
  searchParams: SearchParams | null;
  selectedFlight: Flight | null;
  selectedHotel: Hotel | null;
};

type BookingAction =
  | { type: 'searchSubmitted'; params: SearchParams }
  | { type: 'flightSelected'; flight: Flight }
  | { type: 'hotelSelected'; hotel: Hotel }
  | { type: 'back' }
  | { type: 'reset' };

function bookingReducer(state: BookingState, action: BookingAction): BookingState {
  switch (action.type) {
    case 'searchSubmitted':
      return {
        ...state,
        step: 'flights',
        searchParams: action.params,
      };

    case 'flightSelected':
      return {
        ...state,
        step: 'hotels',
        selectedFlight: action.flight,
      };

    case 'hotelSelected':
      return {
        ...state,
        step: 'confirm',
        selectedHotel: action.hotel,
      };

    case 'back':
      const stepOrder = ['search', 'flights', 'hotels', 'confirm'];
      const currentIndex = stepOrder.indexOf(state.step);
      if (currentIndex <= 0) return state;
      return {
        ...state,
        step: stepOrder[currentIndex - 1] as BookingState['step'],
      };

    case 'reset':
      return initialState;

    default:
      return state;
  }
}
```

### Test the Reducer Directly

```tsx
// bookingReducer.test.ts
import { describe, test, expect } from 'vitest';
import { bookingReducer, initialState } from './bookingReducer';

describe('bookingReducer', () => {
  describe('flightSelected', () => {
    test('should move to hotels step after flight selection', () => {
      const state = { ...initialState, step: 'flights' as const };
      const mockFlight = { id: 'f1', airline: 'Test Air', price: 500 };

      const result = bookingReducer(state, {
        type: 'flightSelected',
        flight: mockFlight,
      });

      expect(result.step).toBe('hotels');
      expect(result.selectedFlight).toBe(mockFlight);
    });
  });
});
```

**Benefits:**
- **Fast**: No rendering, runs in milliseconds
- **Reliable**: Pure function = deterministic results
- **Simple**: Direct input → output assertions
- **Complete**: Easy to test all edge cases
- **Isolated**: UI changes don't break tests

---

## Testing State Transitions

### Happy Path Tests

Test the main user flows work correctly.

```tsx
describe('booking flow', () => {
  test('complete booking flow: search → flight → hotel → confirm', () => {
    let state = initialState;

    // Submit search
    state = bookingReducer(state, {
      type: 'searchSubmitted',
      params: { destination: 'Paris', date: '2024-06-01' },
    });
    expect(state.step).toBe('flights');
    expect(state.searchParams?.destination).toBe('Paris');

    // Select flight
    const flight = { id: 'f1', price: 500 };
    state = bookingReducer(state, { type: 'flightSelected', flight });
    expect(state.step).toBe('hotels');
    expect(state.selectedFlight).toBe(flight);

    // Select hotel
    const hotel = { id: 'h1', price: 200 };
    state = bookingReducer(state, { type: 'hotelSelected', hotel });
    expect(state.step).toBe('confirm');
    expect(state.selectedHotel).toBe(hotel);
  });
});
```

### Edge Case Tests

Test boundary conditions and error scenarios.

```tsx
describe('edge cases', () => {
  test('back from search step does nothing', () => {
    const state = { ...initialState, step: 'search' as const };

    const result = bookingReducer(state, { type: 'back' });

    expect(result.step).toBe('search');
  });

  test('reset clears all selections', () => {
    const state = {
      step: 'confirm' as const,
      searchParams: { destination: 'Paris', date: '2024-06-01' },
      selectedFlight: { id: 'f1', price: 500 },
      selectedHotel: { id: 'h1', price: 200 },
    };

    const result = bookingReducer(state, { type: 'reset' });

    expect(result).toEqual(initialState);
  });

  test('unknown action returns current state', () => {
    const state = { ...initialState, step: 'flights' as const };

    // @ts-expect-error - testing unknown action
    const result = bookingReducer(state, { type: 'UNKNOWN' });

    expect(result).toBe(state);
  });
});
```

### Invalid Transition Tests

Verify the system prevents invalid states.

```tsx
describe('invalid transitions', () => {
  test('cannot select hotel before selecting flight', () => {
    const state = { ...initialState, step: 'flights' as const };
    const hotel = { id: 'h1', price: 200 };

    // If your reducer guards against this:
    const result = bookingReducer(state, { type: 'hotelSelected', hotel });

    // Stays in flights step (or however your reducer handles this)
    expect(result.step).toBe('flights');
  });
});
```

---

## Testing Derived State

Test selector functions and calculated values.

```tsx
// selectors.ts
export function calculateTotalCost(state: BookingState): number {
  const flightCost = state.selectedFlight?.price ?? 0;
  const hotelCost = state.selectedHotel?.price ?? 0;
  return flightCost + hotelCost;
}

export function canProceedToBooking(state: BookingState): boolean {
  return state.selectedFlight !== null && state.selectedHotel !== null;
}

// selectors.test.ts
describe('calculateTotalCost', () => {
  test('sums flight and hotel prices', () => {
    const state = {
      selectedFlight: { id: 'f1', price: 500 },
      selectedHotel: { id: 'h1', price: 200 },
    };

    expect(calculateTotalCost(state)).toBe(700);
  });

  test('returns 0 when no selections', () => {
    const state = { selectedFlight: null, selectedHotel: null };

    expect(calculateTotalCost(state)).toBe(0);
  });

  test('handles partial selection', () => {
    const state = {
      selectedFlight: { id: 'f1', price: 500 },
      selectedHotel: null,
    };

    expect(calculateTotalCost(state)).toBe(500);
  });
});
```

---

## Testing Business Rules

Test validation and business constraints.

```tsx
// validation.ts
export function isValidDateRange(departure: string, arrival: string): boolean {
  return new Date(arrival) > new Date(departure);
}

export function isValidPassengerCount(count: number): boolean {
  return count >= 1 && count <= 9;
}

// validation.test.ts
describe('isValidDateRange', () => {
  test('valid: arrival after departure', () => {
    expect(isValidDateRange('2024-06-01', '2024-06-10')).toBe(true);
  });

  test('invalid: arrival before departure', () => {
    expect(isValidDateRange('2024-06-10', '2024-06-01')).toBe(false);
  });

  test('invalid: same date', () => {
    expect(isValidDateRange('2024-06-01', '2024-06-01')).toBe(false);
  });
});

describe('isValidPassengerCount', () => {
  test.each([
    [1, true],
    [5, true],
    [9, true],
    [0, false],
    [10, false],
    [-1, false],
  ])('passengers: %i → %s', (count, expected) => {
    expect(isValidPassengerCount(count)).toBe(expected);
  });
});
```

---

## Test Organization

### File Structure

```
src/
  features/
    booking/
      bookingReducer.ts
      bookingReducer.test.ts
      selectors.ts
      selectors.test.ts
      validation.ts
      validation.test.ts
```

### Test Structure Pattern

```tsx
describe('featureName', () => {
  describe('actionType', () => {
    test('should [expected behavior] when [condition]', () => {
      // Arrange
      const state = { ... };
      const action = { type: 'ACTION', ... };

      // Act
      const result = reducer(state, action);

      // Assert
      expect(result.property).toBe(expected);
    });
  });
});
```

---

## Quick Reference

### What to Test

| Test Type | Examples |
|-----------|----------|
| State transitions | `search` → `flights` → `hotels` → `confirm` |
| Data updates | Flight selection stores flight data |
| Edge cases | Back from first step, empty selections |
| Business rules | Date validation, passenger limits |
| Derived values | Total cost, booking eligibility |
| Invalid inputs | Null values, wrong types |

### Test Utilities

```tsx
// Create test fixtures
const createMockFlight = (overrides = {}) => ({
  id: 'flight-1',
  airline: 'Test Air',
  price: 500,
  departure: '10:00',
  arrival: '14:00',
  ...overrides,
});

// Create initial state variants
const createBookingState = (overrides = {}): BookingState => ({
  ...initialState,
  ...overrides,
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run specific file
npm test -- bookingReducer.test.ts

# Run with coverage
npm test -- --coverage
```

---

## Related Skills

- **react-reducer-patterns** - Create the reducers to test
- **react-state-machines** - Type states make transitions testable
- **react-data-normalization** - Normalized data has simpler test cases
