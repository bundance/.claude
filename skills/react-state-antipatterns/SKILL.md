---
name: react-state-antipatterns
description: Use when writing React components with useState, useEffect, or useRef. Covers derived state, refs vs state, and redundant state patterns to eliminate synchronization bugs and unnecessary re-renders.
---

# React State Anti-patterns

## When to Use This Skill

Use this skill when:
- Creating or reviewing React components with state management
- You see `useState` + `useEffect` used together for state synchronization
- Deciding between `useState` and `useRef`
- Storing objects in state when only an ID is needed
- Experiencing unnecessary re-renders or synchronization bugs

## Core Principles

React state should be **minimal**. Store only what cannot be derived from other state or props. Every piece of unnecessary state is a potential synchronization bug waiting to happen.

---

## Anti-pattern 1: Derived State

### The Problem

Using `useState` + `useEffect` to sync state that can be calculated from existing data.

```tsx
// ANTI-PATTERN: Storing derived values in state
function TripSummary() {
  const [tripItems] = useState([
    { name: 'Flight', cost: 500 },
    { name: 'Hotel', cost: 300 },
  ]);
  const [totalCost, setTotalCost] = useState(0); // Unnecessary state

  useEffect(() => {
    setTotalCost(tripItems.reduce((sum, item) => sum + item.cost, 0)); // Sync effect
  }, [tripItems]);

  return <div>Total: ${totalCost}</div>;
}
```

**Why it's problematic:**
- Extra render cycle (initial render + effect update)
- Synchronization bugs if effect dependencies are wrong
- More complex mental model
- Harder to debug

### The Solution

Calculate derived values directly during render.

```tsx
// BEST PRACTICE: Derive the value directly
function TripSummary() {
  const [tripItems] = useState([
    { name: 'Flight', cost: 500 },
    { name: 'Hotel', cost: 300 },
  ]);

  // Derive the value - always in sync, no extra render
  const totalCost = tripItems.reduce((sum, item) => sum + item.cost, 0);

  return <div>Total: ${totalCost}</div>;
}
```

### Common Derived State Examples

| Derived Value | Source Data |
|---------------|-------------|
| Filtered list | Original list + filter criteria |
| Sorted list | Original list + sort key |
| Total/sum | Array of items |
| Formatted date | Raw date value |
| Validation errors | Form values |
| Selected item | Items array + selected ID |

### When to Use useMemo

Only use `useMemo` when:
1. The calculation is computationally expensive (e.g., processing thousands of items)
2. Dependencies change infrequently
3. You have measured a performance problem

```tsx
// useMemo for expensive calculations only
const expensiveResult = useMemo(() => {
  return hugeArray.filter(item => complexPredicate(item));
}, [hugeArray]);
```

Do not use `useMemo` by default. Premature optimization adds complexity without benefit.

---

## Anti-pattern 2: useState for Non-Rendering Values

### The Problem

Using `useState` for values that don't affect what's rendered.

```tsx
// ANTI-PATTERN: useState for timer ID
function Timer() {
  const [timeLeft, setTimeLeft] = useState(60);
  const [timerId, setTimerId] = useState<NodeJS.Timeout | null>(null); // Causes re-renders

  const startTimer = () => {
    const id = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);
    setTimerId(id); // Triggers unnecessary re-render
  };

  useEffect(() => {
    return () => timerId && clearInterval(timerId);
  }, [timerId]); // Effect runs every time timerId changes
}
```

**Why it's problematic:**
- Unnecessary re-renders when setting the timer ID
- Effect cleanup runs more often than needed
- Wastes resources on state updates that don't change UI

### The Solution

Use `useRef` for mutable values that don't affect rendering.

```tsx
// BEST PRACTICE: useRef for non-rendering values
function Timer() {
  const [timeLeft, setTimeLeft] = useState(60);
  const timerIdRef = useRef<NodeJS.Timeout | null>(null); // No re-renders

  const startTimer = () => {
    if (timerIdRef.current) clearInterval(timerIdRef.current);

    const id = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(id);
          timerIdRef.current = null;
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    timerIdRef.current = id; // No re-render triggered
  };

  useEffect(() => {
    return () => {
      if (timerIdRef.current) clearInterval(timerIdRef.current);
    };
  }, []); // Effect runs only on mount/unmount
}
```

### useRef Use Cases

| Use Case | Example |
|----------|---------|
| Timer IDs | `setInterval`, `setTimeout` references |
| Scroll position | Tracking for analytics, not display |
| Previous values | Comparing current vs previous props |
| DOM references | Direct DOM manipulation |
| Analytics data | Search counts, timing metrics |
| Cached calculations | Values needed in callbacks but not render |

### Decision Guide: useState vs useRef

```
Does changing this value need to update the UI?
├── YES → useState
└── NO → useRef
```

---

## Anti-pattern 3: Redundant State

### The Problem

Storing entire objects when only an identifier is needed.

```tsx
// ANTI-PATTERN: Storing full object
function HotelSelection() {
  const [hotels] = useState([
    { id: 'h1', name: 'Grand Hotel', price: 200, amenities: [...] },
    { id: 'h2', name: 'Budget Inn', price: 80, amenities: [...] },
  ]);
  const [selectedHotel, setSelectedHotel] = useState<Hotel | null>(null); // Full object

  const handleSelect = (hotel: Hotel) => {
    setSelectedHotel(hotel); // Duplicates data from hotels array
  };
}
```

**Why it's problematic:**
- Data can get out of sync if hotels array updates
- More memory usage
- Harder to track which hotel is actually selected
- Updates to hotel data don't reflect in selectedHotel

### The Solution

Store only the ID, derive the full object when needed.

```tsx
// BEST PRACTICE: Store only ID
function HotelSelection() {
  const [hotels] = useState([
    { id: 'h1', name: 'Grand Hotel', price: 200, amenities: [...] },
    { id: 'h2', name: 'Budget Inn', price: 80, amenities: [...] },
  ]);
  const [selectedHotelId, setSelectedHotelId] = useState<string | null>(null); // Just ID

  const handleSelect = (hotelId: string) => {
    setSelectedHotelId(hotelId); // Store minimal data
  };

  // Derive the full object when needed - always in sync
  const selectedHotel = hotels.find((h) => h.id === selectedHotelId);
}
```

### Single Source of Truth Principle

For each piece of data in your application, there should be exactly one place where it lives. Everything else should reference or derive from that source.

**Patterns to avoid:**
- Storing both raw and formatted versions of the same data
- Copying prop data into local state
- Keeping calculated values in separate state
- Storing full objects when ID is sufficient

---

## Quick Reference

### State Hygiene Checklist

Before adding state, ask:

1. **Can this be calculated?** If yes, derive it during render.
2. **Does it affect rendering?** If no, use `useRef`.
3. **Is this duplicating existing data?** If yes, store only the reference (ID).
4. **Am I using useEffect to sync state?** If yes, you probably have derived state.

### Common Fixes

| Symptom | Problem | Solution |
|---------|---------|----------|
| `useState` + `useEffect` for sync | Derived state | Calculate during render |
| State for timer/interval IDs | Non-rendering value | Use `useRef` |
| Storing full objects in selection | Redundant state | Store ID only |
| Multiple states always update together | Related state | Combine into single object |

---

## Related Skills

- **react-state-machines** - When you need to prevent impossible states with discriminated unions
- **react-data-fetching** - For server state, use TanStack Query instead of useState + useEffect
- **react-cascading-effects** - When multiple useEffects trigger each other
