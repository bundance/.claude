---
name: react-data-fetching
description: Use when fetching data from APIs, managing server state, or dealing with caching and background updates. Covers TanStack Query to replace useEffect + useState patterns for data fetching.
---

# Server State Management with TanStack Query

## When to Use This Skill

Use this skill when:
- Fetching data from APIs
- Multiple components need the same server data
- You need caching, background refetching, or request deduplication
- Building loading/error states for async operations
- Implementing optimistic updates or mutations

## Core Principle

**Use TanStack Query for server state, not useEffect + useState.** Server state (data from APIs) has different characteristics than client state. It's cached, can become stale, and needs synchronization with the server. TanStack Query handles all of this automatically.

---

## Anti-pattern: useEffect + useState for Fetching

### The Problem

Manual data fetching with useEffect creates many edge cases to handle.

```tsx
// ANTI-PATTERN: Manual fetching with useEffect + useState
function FlightSearchResults({ searchParams }) {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const loadFlights = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchFlights(searchParams);
        if (!cancelled) {
          setFlights(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadFlights();

    return () => {
      cancelled = true;
    };
  }, [searchParams]);

  if (isLoading) return <Spinner />;
  if (error) return <Error message={error} />;
  return <FlightList flights={flights} />;
}
```

**Why it's problematic:**
- Boilerplate: Every fetch needs loading, error, data states
- Race conditions: Rapid parameter changes can cause stale data
- No caching: Same data fetched repeatedly
- Memory leaks: Must manually cancel on unmount
- No background refetching: Data becomes stale
- No request deduplication: Multiple components = multiple requests

---

## Best Practice: TanStack Query

### Installation

```bash
npm install @tanstack/react-query
```

### Setup Provider

```tsx
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        retry: 2,
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Basic Query

```tsx
import { useQuery } from '@tanstack/react-query';

function FlightSearchResults({ searchParams }) {
  const {
    data: flights,
    isLoading,
    error,
    isFetching, // Background refetch indicator
  } = useQuery({
    queryKey: ['flights', searchParams],
    queryFn: () => fetchFlights(searchParams),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  if (isLoading) return <Spinner />;
  if (error) return <Error message={error.message} />;

  return (
    <div>
      {isFetching && <RefreshIndicator />}
      <FlightList flights={flights} />
    </div>
  );
}
```

**Benefits:**
- Automatic loading/error states
- Built-in caching by query key
- Request deduplication across components
- Background refetching when stale
- No memory leak concerns
- Retry on failure
- DevTools for debugging

---

## Query Keys Best Practices

Query keys uniquely identify cached data. Structure them hierarchically.

```tsx
// Good: Structured keys with all relevant parameters
queryKey: ['flights', { destination, departure, passengers }]
queryKey: ['hotels', { checkIn, checkOut, location }]
queryKey: ['user', userId]
queryKey: ['booking', bookingId, 'details']

// Bad: Non-unique or unstable keys
queryKey: ['flights']                    // Not specific enough
queryKey: ['flights', searchObject]      // Object reference changes
queryKey: [Math.random()]                // Never cached
```

### Key Hierarchy Pattern

```tsx
// All flights queries
queryKey: ['flights', ...]

// Specific search
queryKey: ['flights', 'search', { destination: 'Paris', date: '2024-06-01' }]

// Single flight detail
queryKey: ['flights', flightId]

// Invalidate all flights
queryClient.invalidateQueries({ queryKey: ['flights'] });
```

---

## Mutations for Data Updates

Use `useMutation` for creating, updating, or deleting data.

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

function BookingForm({ flight, hotel }) {
  const queryClient = useQueryClient();

  const bookingMutation = useMutation({
    mutationFn: (bookingData: BookingData) => submitBooking(bookingData),
    onSuccess: (newBooking) => {
      // Invalidate related queries to refetch
      queryClient.invalidateQueries({ queryKey: ['bookings'] });
      queryClient.invalidateQueries({ queryKey: ['user', 'trips'] });
    },
    onError: (error) => {
      toast.error(`Booking failed: ${error.message}`);
    },
  });

  const handleSubmit = () => {
    bookingMutation.mutate({
      flightId: flight.id,
      hotelId: hotel.id,
    });
  };

  return (
    <button
      onClick={handleSubmit}
      disabled={bookingMutation.isPending}
    >
      {bookingMutation.isPending ? 'Booking...' : 'Confirm Booking'}
    </button>
  );
}
```

---

## Common Query Patterns

### Dependent Queries

```tsx
// First query: Get user
const { data: user } = useQuery({
  queryKey: ['user'],
  queryFn: fetchUser,
});

// Second query: Get bookings (only runs when user exists)
const { data: bookings } = useQuery({
  queryKey: ['bookings', user?.id],
  queryFn: () => fetchBookings(user.id),
  enabled: !!user, // Only fetch when user is available
});
```

### Parallel Queries

```tsx
// Multiple independent queries run in parallel
const flightsQuery = useQuery({
  queryKey: ['flights', searchParams],
  queryFn: () => fetchFlights(searchParams),
});

const hotelsQuery = useQuery({
  queryKey: ['hotels', searchParams],
  queryFn: () => fetchHotels(searchParams),
});

// Or use useQueries for dynamic arrays
const queries = useQueries({
  queries: destinations.map(dest => ({
    queryKey: ['destination', dest.id],
    queryFn: () => fetchDestination(dest.id),
  })),
});
```

### Prefetching

```tsx
const queryClient = useQueryClient();

// Prefetch on hover
const handleHover = () => {
  queryClient.prefetchQuery({
    queryKey: ['flight', flightId, 'details'],
    queryFn: () => fetchFlightDetails(flightId),
  });
};
```

### Optimistic Updates

```tsx
const mutation = useMutation({
  mutationFn: updateBooking,
  onMutate: async (newData) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['booking', id] });

    // Snapshot previous value
    const previous = queryClient.getQueryData(['booking', id]);

    // Optimistically update
    queryClient.setQueryData(['booking', id], newData);

    return { previous };
  },
  onError: (err, newData, context) => {
    // Rollback on error
    queryClient.setQueryData(['booking', id], context.previous);
  },
  onSettled: () => {
    // Refetch to ensure consistency
    queryClient.invalidateQueries({ queryKey: ['booking', id] });
  },
});
```

---

## Quick Reference

### Query States

| Property | Description |
|----------|-------------|
| `isLoading` | First load, no cached data |
| `isFetching` | Any fetch (including background) |
| `isError` | Query failed |
| `isSuccess` | Query succeeded |
| `data` | The cached/fetched data |
| `error` | Error object if failed |

### Query Options

```tsx
useQuery({
  queryKey: ['key'],
  queryFn: fetchFn,
  staleTime: 5 * 60 * 1000,    // Time until data is considered stale
  gcTime: 10 * 60 * 1000,       // Time to keep unused data in cache
  refetchOnWindowFocus: true,   // Refetch when window regains focus
  refetchOnReconnect: true,     // Refetch when network reconnects
  retry: 3,                     // Number of retries on failure
  enabled: true,                // Whether query should run
});
```

### Invalidation Patterns

```tsx
// Invalidate exact key
queryClient.invalidateQueries({ queryKey: ['flights', searchParams] });

// Invalidate all flights queries
queryClient.invalidateQueries({ queryKey: ['flights'] });

// Invalidate everything
queryClient.invalidateQueries();
```

---

## Related Skills

- **react-state-antipatterns** - For understanding when NOT to use useState
- **react-cascading-effects** - TanStack Query replaces effect chains for data
- **react-url-state** - Combine with nuqs for URL-based search params
