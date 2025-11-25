---
name: react-state-libraries
description: Use when React's built-in state (useState, useReducer, Context) doesn't scale, or when syncing with external data sources. Covers Zustand, Jotai, XState Store, and useSyncExternalStore.
---

# External State Management Libraries

## When to Use This Skill

Use this skill when:
- Context causes performance issues from too many re-renders
- Multiple unrelated components need shared state
- Business logic is too complex for useReducer alone
- You need selective subscriptions for performance
- Syncing with external data sources (WebSocket, browser APIs)

## Core Principle

**Choose the right tool for your state complexity.** React's built-in state works for most cases, but external libraries provide better performance, debugging, and organization for complex applications. Understand the tradeoffs between store-based (centralized) and atomic (distributed) approaches.

---

## When React Built-ins Aren't Enough

### Problem: Context Re-renders Everything

```tsx
// ANTI-PATTERN: Single context causes all consumers to re-render
const AppContext = createContext({
  user: null,
  cart: [],
  notifications: [],
  settings: {},
});

function App() {
  const [state, setState] = useState(initialState);

  return (
    <AppContext.Provider value={{ ...state, setState }}>
      {/* Every update to ANY field re-renders ALL consumers */}
      <Header />      {/* Re-renders when cart changes */}
      <Sidebar />     {/* Re-renders when user changes */}
      <MainContent /> {/* Re-renders when anything changes */}
    </AppContext.Provider>
  );
}
```

### Problem: Prop Drilling Through Many Layers

```tsx
// ANTI-PATTERN: Passing state through components that don't use it
function App() {
  const [booking, setBooking] = useState(null);
  return <Page1 booking={booking} setBooking={setBooking} />;
}

function Page1({ booking, setBooking }) {
  return <Section booking={booking} setBooking={setBooking} />;
}

function Section({ booking, setBooking }) {
  return <Component booking={booking} setBooking={setBooking} />;
}
// Component finally uses the state
```

---

## Store-Based vs Atomic Approaches

### Store-Based (Zustand, Redux Toolkit, XState Store)

**Centralized**: All related state lives in one place.

```tsx
// Zustand store
const useBookingStore = create((set) => ({
  flights: [],
  selectedFlight: null,
  hotels: [],
  selectedHotel: null,

  selectFlight: (flight) => set({ selectedFlight: flight }),
  selectHotel: (hotel) => set({ selectedHotel: hotel }),
  clearBooking: () => set({ selectedFlight: null, selectedHotel: null }),
}));
```

**Best for:**
- Complex state relationships (many pieces depend on each other)
- Clear data flow requirements
- Team coordination on shared state
- Business logic that spans multiple concerns

### Atomic (Jotai, Recoil)

**Distributed**: State is broken into independent atoms that can be composed.

```tsx
// Jotai atoms
const flightsAtom = atom<Flight[]>([]);
const selectedFlightAtom = atom<Flight | null>(null);
const hotelsAtom = atom<Hotel[]>([]);
const selectedHotelAtom = atom<Hotel | null>(null);

// Derived atom
const totalPriceAtom = atom((get) => {
  const flight = get(selectedFlightAtom);
  const hotel = get(selectedHotelAtom);
  return (flight?.price ?? 0) + (hotel?.price ?? 0);
});
```

**Best for:**
- Independent pieces of state
- Component-specific concerns
- Performance-critical applications (fine-grained subscriptions)
- Bottom-up architecture

---

## Zustand: Simple Store Pattern

```bash
npm install zustand
```

### Creating a Store

```tsx
import { create } from 'zustand';

interface BookingState {
  step: 'search' | 'flights' | 'hotels' | 'confirm';
  searchParams: SearchParams | null;
  selectedFlight: Flight | null;
  selectedHotel: Hotel | null;

  setSearchParams: (params: SearchParams) => void;
  selectFlight: (flight: Flight) => void;
  selectHotel: (hotel: Hotel) => void;
  nextStep: () => void;
  reset: () => void;
}

const useBookingStore = create<BookingState>((set) => ({
  step: 'search',
  searchParams: null,
  selectedFlight: null,
  selectedHotel: null,

  setSearchParams: (params) => set({ searchParams: params, step: 'flights' }),
  selectFlight: (flight) => set({ selectedFlight: flight, step: 'hotels' }),
  selectHotel: (hotel) => set({ selectedHotel: hotel, step: 'confirm' }),
  nextStep: () => set((state) => {
    const steps = ['search', 'flights', 'hotels', 'confirm'];
    const idx = steps.indexOf(state.step);
    return { step: steps[Math.min(idx + 1, steps.length - 1)] as BookingState['step'] };
  }),
  reset: () => set({ step: 'search', searchParams: null, selectedFlight: null, selectedHotel: null }),
}));
```

### Selective Subscriptions

```tsx
// Only re-renders when selectedFlight changes
function FlightSummary() {
  const selectedFlight = useBookingStore((state) => state.selectedFlight);
  return selectedFlight ? <div>{selectedFlight.airline}</div> : null;
}

// Only re-renders when step changes
function StepIndicator() {
  const step = useBookingStore((state) => state.step);
  return <div>Current step: {step}</div>;
}

// Access multiple values
function BookingSummary() {
  const { selectedFlight, selectedHotel } = useBookingStore((state) => ({
    selectedFlight: state.selectedFlight,
    selectedHotel: state.selectedHotel,
  }));
  // ...
}
```

---

## Jotai: Atomic State

```bash
npm install jotai
```

### Creating Atoms

```tsx
import { atom, useAtom, useAtomValue, useSetAtom } from 'jotai';

// Primitive atoms
const destinationAtom = atom('');
const departureDateAtom = atom('');
const passengersAtom = atom(1);

// Derived atom (read-only)
const searchSummaryAtom = atom((get) => {
  const dest = get(destinationAtom);
  const date = get(departureDateAtom);
  const passengers = get(passengersAtom);
  return `${dest} on ${date} for ${passengers} passenger(s)`;
});

// Writable derived atom
const searchParamsAtom = atom(
  (get) => ({
    destination: get(destinationAtom),
    departure: get(departureDateAtom),
    passengers: get(passengersAtom),
  }),
  (get, set, update: Partial<SearchParams>) => {
    if (update.destination !== undefined) set(destinationAtom, update.destination);
    if (update.departure !== undefined) set(departureDateAtom, update.departure);
    if (update.passengers !== undefined) set(passengersAtom, update.passengers);
  }
);
```

### Using Atoms

```tsx
function DestinationInput() {
  const [destination, setDestination] = useAtom(destinationAtom);
  return (
    <input
      value={destination}
      onChange={(e) => setDestination(e.target.value)}
    />
  );
}

// Read-only hook (no setter)
function SearchSummary() {
  const summary = useAtomValue(searchSummaryAtom);
  return <div>{summary}</div>;
}

// Write-only hook (no reader)
function ResetButton() {
  const setDestination = useSetAtom(destinationAtom);
  return <button onClick={() => setDestination('')}>Clear</button>;
}
```

---

## useSyncExternalStore: External Data Sources

For subscribing to external stores (browser APIs, WebSockets, third-party libraries).

### Anti-pattern: useEffect + useState

```tsx
// ANTI-PATTERN: Manual subscription with useEffect
function NetworkStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    setIsOnline(navigator.onLine);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return <div>{isOnline ? 'Online' : 'Offline'}</div>;
}
```

### Best Practice: useSyncExternalStore

```tsx
import { useSyncExternalStore } from 'react';

function NetworkStatus() {
  const isOnline = useSyncExternalStore(
    // Subscribe function
    (callback) => {
      window.addEventListener('online', callback);
      window.addEventListener('offline', callback);
      return () => {
        window.removeEventListener('online', callback);
        window.removeEventListener('offline', callback);
      };
    },
    // Get snapshot (client)
    () => navigator.onLine,
    // Get server snapshot (SSR)
    () => true
  );

  return <div>{isOnline ? 'Online' : 'Offline'}</div>;
}
```

### Creating Reusable External Store Hooks

```tsx
function useWindowSize() {
  return useSyncExternalStore(
    (callback) => {
      window.addEventListener('resize', callback);
      return () => window.removeEventListener('resize', callback);
    },
    () => ({ width: window.innerWidth, height: window.innerHeight }),
    () => ({ width: 0, height: 0 }) // SSR fallback
  );
}

function useMediaQuery(query: string) {
  return useSyncExternalStore(
    (callback) => {
      const mql = window.matchMedia(query);
      mql.addEventListener('change', callback);
      return () => mql.removeEventListener('change', callback);
    },
    () => window.matchMedia(query).matches,
    () => false
  );
}
```

---

## Quick Reference: Choosing a Solution

| Scenario | Solution |
|----------|----------|
| Simple component state | `useState` |
| Complex state logic | `useReducer` |
| Shared state in subtree | Context + `useReducer` |
| Global state, simple | Zustand |
| Global state, complex | XState Store, Redux Toolkit |
| Independent atoms, perf-critical | Jotai |
| External data source | `useSyncExternalStore` |
| Server state | TanStack Query |

### Store vs Atoms Decision

| Factor | Choose Store | Choose Atoms |
|--------|-------------|--------------|
| State relationships | Many dependencies | Independent pieces |
| Team size | Large, needs coordination | Small, flexible |
| Debugging needs | Strong (single source) | Moderate |
| Performance | Good with selectors | Excellent (fine-grained) |
| Learning curve | Lower | Moderate |

---

## Related Skills

- **react-reducer-patterns** - For useReducer + Context baseline
- **react-data-normalization** - Normalize data in external stores
- **react-data-fetching** - TanStack Query for server state
- **react-state-testing** - Test store logic in isolation
