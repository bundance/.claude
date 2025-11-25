---
name: react-url-state
description: Use when state should be shareable, bookmarkable, or persist across page refreshes. Covers URL query parameters with nuqs for type-safe URL state management in Next.js.
---

# URL Query State Management

## When to Use This Skill

Use this skill when:
- Users should be able to share URLs that preserve state
- State should survive page refreshes
- Browser back/forward navigation should work with state
- Building search, filter, or pagination interfaces
- Creating deep links to specific application states

## Core Principle

**Store shareable and persistent state in URL query parameters.** If the state affects what the user sees and should be shareable or bookmarkable, it belongs in the URL, not in component state.

---

## Anti-pattern: useState for Shareable State

### The Problem

Using `useState` for state that should be shareable or persistent.

```tsx
// ANTI-PATTERN: Local state for shareable data
function FlightSearch() {
  const [destination, setDestination] = useState('');
  const [departureDate, setDepartureDate] = useState('');
  const [returnDate, setReturnDate] = useState('');
  const [passengers, setPassengers] = useState(1);

  // Problems:
  // 1. State lost on page refresh
  // 2. Can't share search with others
  // 3. Can't bookmark specific searches
  // 4. Back button doesn't preserve state

  return (
    <form>
      <input value={destination} onChange={(e) => setDestination(e.target.value)} />
      {/* ... */}
    </form>
  );
}
```

**Why it's problematic:**
- User loses search criteria on page refresh
- No way to share a specific search via URL
- Browser navigation doesn't work with form state
- Can't deep link to specific searches

---

## Best Practice: URL State with nuqs

### Installation

```bash
npm install nuqs
```

### Setup Provider (App Router)

```tsx
// app/layout.tsx
import { NuqsAdapter } from 'nuqs/adapters/next/app';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <NuqsAdapter>{children}</NuqsAdapter>
      </body>
    </html>
  );
}
```

### Basic Usage

```tsx
'use client';

import { useQueryState, parseAsInteger, parseAsString } from 'nuqs';

function FlightSearch() {
  // String parameter (default parser)
  const [destination, setDestination] = useQueryState('destination');

  // With custom parser and default value
  const [passengers, setPassengers] = useQueryState(
    'passengers',
    parseAsInteger.withDefault(1)
  );

  // URL will be: /search?destination=Paris&passengers=2

  return (
    <form>
      <input
        value={destination ?? ''}
        onChange={(e) => setDestination(e.target.value || null)}
      />
      <input
        type="number"
        value={passengers}
        onChange={(e) => setPassengers(parseInt(e.target.value) || 1)}
      />
    </form>
  );
}
```

**Benefits:**
- State persists in URL automatically
- Shareable URLs with preserved state
- Browser back/forward works naturally
- Bookmarkable searches
- SSR compatible

---

## nuqs Parsers

nuqs provides type-safe parsers for common data types:

```tsx
import {
  parseAsString,       // String (default)
  parseAsInteger,      // Integer numbers
  parseAsFloat,        // Floating point numbers
  parseAsBoolean,      // true/false
  parseAsIsoDateTime,  // ISO date strings
  parseAsArrayOf,      // Arrays
  parseAsStringEnum,   // Enums
  parseAsJson,         // JSON objects
} from 'nuqs';

// String enum for trip type
const [tripType, setTripType] = useQueryState(
  'type',
  parseAsStringEnum(['one-way', 'round-trip']).withDefault('round-trip')
);

// Date parsing
const [departureDate, setDepartureDate] = useQueryState(
  'departure',
  parseAsIsoDateTime
);

// Boolean for filters
const [directOnly, setDirectOnly] = useQueryState(
  'direct',
  parseAsBoolean.withDefault(false)
);

// Array of selected airlines
const [airlines, setAirlines] = useQueryState(
  'airlines',
  parseAsArrayOf(parseAsString)
);
```

---

## Combining Multiple Query Params

Use `useQueryStates` for coordinated updates to multiple parameters:

```tsx
import { useQueryStates, parseAsInteger, parseAsString, parseAsBoolean } from 'nuqs';

function FlightSearchForm() {
  const [searchParams, setSearchParams] = useQueryStates({
    destination: parseAsString,
    departure: parseAsString,
    arrival: parseAsString,
    passengers: parseAsInteger.withDefault(1),
    directOnly: parseAsBoolean.withDefault(false),
  });

  const handleSearch = () => {
    // Update multiple params at once (single URL update)
    setSearchParams({
      destination: 'Paris',
      departure: '2024-06-01',
      arrival: '2024-06-10',
      passengers: 2,
    });
  };

  return (
    <form>
      <input
        placeholder="Destination"
        value={searchParams.destination ?? ''}
        onChange={(e) => setSearchParams({ destination: e.target.value || null })}
      />
      <input
        type="number"
        value={searchParams.passengers}
        onChange={(e) => setSearchParams({ passengers: parseInt(e.target.value) })}
      />
      <label>
        <input
          type="checkbox"
          checked={searchParams.directOnly}
          onChange={(e) => setSearchParams({ directOnly: e.target.checked })}
        />
        Direct flights only
      </label>
    </form>
  );
}
```

---

## URL State Options

### Shallow vs Push Updates

```tsx
// Default: shallow update (replaces current history entry)
const [query, setQuery] = useQueryState('q');

// Push to history (creates new entry, back button works)
const [query, setQuery] = useQueryState('q', { history: 'push' });

// Replace (same as shallow)
const [query, setQuery] = useQueryState('q', { history: 'replace' });
```

### Clearing Parameters

```tsx
// Set to null to remove from URL
setDestination(null);

// Clear all params in a group
setSearchParams({
  destination: null,
  departure: null,
  arrival: null,
});
```

---

## When State Belongs in URL

### Put in URL

| State Type | Example |
|------------|---------|
| Search/filter criteria | `?q=flights&destination=paris` |
| Pagination | `?page=2&limit=20` |
| Sorting | `?sort=price&order=asc` |
| Active tabs/views | `?view=list` or `?tab=details` |
| Selected items | `?selected=item-123` |
| Date ranges | `?from=2024-01-01&to=2024-01-31` |

### Keep in Component State

| State Type | Example |
|------------|---------|
| UI-only state | Dropdown open/closed |
| Ephemeral state | Form validation errors |
| Sensitive data | Auth tokens, passwords |
| Performance-critical | Rapid typing in controlled inputs |
| Derived state | Calculated totals |

---

## Quick Reference

### Basic Setup

```tsx
// 1. Install
npm install nuqs

// 2. Add provider (app/layout.tsx)
import { NuqsAdapter } from 'nuqs/adapters/next/app';
<NuqsAdapter>{children}</NuqsAdapter>

// 3. Use in components
import { useQueryState, parseAsInteger } from 'nuqs';
const [value, setValue] = useQueryState('key', parseAsInteger.withDefault(0));
```

### Common Parsers

```tsx
parseAsString                           // 'hello'
parseAsInteger                          // 42
parseAsFloat                            // 3.14
parseAsBoolean                          // true/false
parseAsIsoDateTime                      // 2024-01-15T10:30:00Z
parseAsArrayOf(parseAsString)           // ['a', 'b', 'c']
parseAsStringEnum(['a', 'b', 'c'])      // 'a' | 'b' | 'c'
parseAsJson<MyType>()                   // { complex: 'object' }
```

### Clearing Values

```tsx
// Remove single param
setValue(null);

// Remove multiple params
setParams({ key1: null, key2: null });
```

---

## Related Skills

- **react-forms** - For form handling with server actions
- **react-data-fetching** - Combine URL state with TanStack Query for cached searches
- **react-state-antipatterns** - For understanding when state should be derived vs stored
