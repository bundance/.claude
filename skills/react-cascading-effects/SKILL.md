---
name: react-cascading-effects
description: Use when you see multiple useEffect hooks that trigger each other, effect chains causing race conditions, or state updates scattered across many effects. Covers event-driven architecture and consolidating to useReducer + single useEffect.
---

# Avoiding Cascading Effects

## When to Use This Skill

Use this skill when:
- You have multiple `useEffect` hooks that trigger in sequence
- One effect sets state that triggers another effect
- You're experiencing race conditions or timing bugs
- State logic is scattered across many effects
- Debugging requires tracing through multiple effects to understand the flow

## Core Principle

**Think about WHY data changes (events), not WHEN data changes (reactive).** Cascading effects make code hard to follow, debug, and maintain. Consolidate to event-driven state management with a single reducer and minimal effects.

---

## Anti-pattern: Cascading Effects

### The Problem

Multiple `useEffect` hooks that trigger each other in sequence.

```tsx
// ANTI-PATTERN: Effects that cascade
function TripBooking() {
  const [destination, setDestination] = useState('');
  const [startDate, setStartDate] = useState('');
  const [isSearchingFlights, setIsSearchingFlights] = useState(false);
  const [flights, setFlights] = useState([]);
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [isSearchingHotels, setIsSearchingHotels] = useState(false);
  const [hotels, setHotels] = useState([]);

  // Effect 1: Trigger flight search when inputs change
  useEffect(() => {
    if (destination && startDate) {
      setIsSearchingFlights(true);
    }
  }, [destination, startDate]);

  // Effect 2: Perform flight search
  useEffect(() => {
    if (!isSearchingFlights) return;
    searchFlights(destination).then(results => {
      setFlights(results);
      setIsSearchingFlights(false);
    });
  }, [isSearchingFlights, destination]);

  // Effect 3: Trigger hotel search when flight selected
  useEffect(() => {
    if (selectedFlight) {
      setIsSearchingHotels(true);
    }
  }, [selectedFlight]);

  // Effect 4: Perform hotel search
  useEffect(() => {
    if (!isSearchingHotels) return;
    searchHotels(selectedFlight.destination).then(results => {
      setHotels(results);
      setIsSearchingHotels(false);
    });
  }, [isSearchingHotels, selectedFlight]);
}
```

**Why it's problematic:**
- Logic flow jumps between different effects
- 4 effects chained together = hard to trace execution
- Race conditions if dependencies change rapidly
- Multiple state updates cause cascading re-renders
- Debugging requires understanding effect execution order
- Easy to create infinite loops or stale closures

---

## The Solution: Event-Driven with useReducer

Replace cascading effects with a single reducer that handles all state transitions, and a single effect for side effects.

### Step 1: Define Events (Actions)

Think about **what happened**, not when something should react.

```tsx
type BookingAction =
  | { type: 'searchSubmitted'; destination: string; startDate: string }
  | { type: 'flightsLoaded'; flights: Flight[] }
  | { type: 'flightSelected'; flight: Flight }
  | { type: 'hotelsLoaded'; hotels: Hotel[] }
  | { type: 'error'; message: string };
```

### Step 2: Centralize Logic in Reducer

```tsx
type BookingState = {
  status: 'idle' | 'searchingFlights' | 'selectingFlight' | 'searchingHotels' | 'selectingHotel';
  destination: string;
  startDate: string;
  flights: Flight[];
  selectedFlight: Flight | null;
  hotels: Hotel[];
  error: string | null;
};

function bookingReducer(state: BookingState, action: BookingAction): BookingState {
  switch (action.type) {
    case 'searchSubmitted':
      return {
        ...state,
        status: 'searchingFlights',
        destination: action.destination,
        startDate: action.startDate,
        flights: [],
        selectedFlight: null,
        hotels: [],
      };

    case 'flightsLoaded':
      return {
        ...state,
        status: 'selectingFlight',
        flights: action.flights,
      };

    case 'flightSelected':
      return {
        ...state,
        status: 'searchingHotels',
        selectedFlight: action.flight,
      };

    case 'hotelsLoaded':
      return {
        ...state,
        status: 'selectingHotel',
        hotels: action.hotels,
      };

    case 'error':
      return {
        ...state,
        status: 'idle',
        error: action.message,
      };

    default:
      return state;
  }
}
```

### Step 3: Single Effect for Side Effects

```tsx
function TripBooking() {
  const [state, dispatch] = useReducer(bookingReducer, initialState);

  // Single effect handles all async operations based on status
  useEffect(() => {
    if (state.status === 'searchingFlights') {
      searchFlights(state.destination)
        .then(flights => dispatch({ type: 'flightsLoaded', flights }))
        .catch(err => dispatch({ type: 'error', message: err.message }));
    }

    if (state.status === 'searchingHotels' && state.selectedFlight) {
      searchHotels(state.selectedFlight.destination)
        .then(hotels => dispatch({ type: 'hotelsLoaded', hotels }))
        .catch(err => dispatch({ type: 'error', message: err.message }));
    }
  }, [state.status, state.destination, state.selectedFlight]);

  // Event handlers dispatch actions
  const handleSearch = (destination: string, startDate: string) => {
    dispatch({ type: 'searchSubmitted', destination, startDate });
  };

  const handleFlightSelect = (flight: Flight) => {
    dispatch({ type: 'flightSelected', flight });
  };

  return (
    // UI renders based on state.status
  );
}
```

---

## Understanding Events vs Reactions

Ask yourself: **What user action or business event caused this state change?**

| Reactive Thinking (Bad) | Event-Driven Thinking (Good) |
|------------------------|------------------------------|
| "When destination changes..." | "User submitted search form" → `searchSubmitted` |
| "When isSearchingFlights becomes true..." | "API returned flight results" → `flightsLoaded` |
| "When selectedFlight changes..." | "User selected a flight" → `flightSelected` |
| "When isSearchingHotels becomes true..." | "API returned hotel results" → `hotelsLoaded` |

---

## Benefits of Event-Driven Approach

1. **Single source of truth**: All state lives in the reducer
2. **Predictable flow**: Each action explicitly defines what changes
3. **No race conditions**: State changes are synchronous within the reducer
4. **Easier debugging**: Clear action history in React DevTools
5. **Testable**: Reducer is a pure function, easy to unit test
6. **Self-documenting**: Action types describe business events

---

## Quick Reference

### Signs You Have Cascading Effects

- Multiple `useEffect` with state setters as dependencies
- Boolean flags like `isSearchingX` that trigger other effects
- Effects that set state watched by other effects
- Hard to trace which effect runs when

### Refactoring Checklist

1. **Identify all effects** that update state
2. **Define action types** representing business events
3. **Create a reducer** with status-based state
4. **Move logic** from effects into reducer
5. **Single effect** handles async operations based on status
6. **Event handlers** dispatch actions directly

### Effect Usage Guidelines

| Use Effects For | Don't Use Effects For |
|-----------------|----------------------|
| Fetching data based on status | Synchronizing state between variables |
| Subscribing to external sources | Triggering state updates in chains |
| Timers and intervals | Transforming props into state |
| Manual DOM manipulation | Derived calculations |

---

## Related Skills

- **react-reducer-patterns** - For implementing the useReducer + Context pattern
- **react-state-machines** - For the status-based state pattern used here
- **react-data-fetching** - When fetching becomes complex, consider TanStack Query
