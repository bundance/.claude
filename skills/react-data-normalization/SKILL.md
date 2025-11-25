---
name: react-data-normalization
description: Use when managing nested data structures with parent-child relationships, or when updates require traversing arrays to find items. Covers flattening data to entity-based structures for O(1) lookups.
---

# Data Normalization

## When to Use This Skill

Use this skill when:
- Data has parent-child relationships (destinations with todos, categories with items)
- Updates require finding items in nested arrays
- Multiple components need to reference the same entity
- Performance suffers from deep object traversals
- You need efficient cross-entity operations (search, bulk updates)

## Core Principle

**Flatten data structures by storing entities in separate collections with ID references.** Normalization converts nested data into a database-like structure where each entity type has its own collection and relationships use IDs instead of nested objects.

---

## Anti-pattern: Deeply Nested Data

### The Problem

Storing child entities nested inside parents.

```tsx
// ANTI-PATTERN: Nested data structure
interface NestedState {
  destinations: Array<{
    id: string;
    name: string;
    todos: Array<{
      id: string;
      text: string;
      completed: boolean;
    }>;
  }>;
}

// To update a todo, must traverse nested arrays
function reducer(state: NestedState, action: Action): NestedState {
  switch (action.type) {
    case 'TOGGLE_TODO':
      return {
        ...state,
        destinations: state.destinations.map((dest) =>
          dest.id === action.destinationId
            ? {
                ...dest,
                todos: dest.todos.map((todo) =>
                  todo.id === action.todoId
                    ? { ...todo, completed: !todo.completed }
                    : todo
                ),
              }
            : dest
        ),
      };

    case 'DELETE_TODO':
      return {
        ...state,
        destinations: state.destinations.map((dest) =>
          dest.id === action.destinationId
            ? {
                ...dest,
                todos: dest.todos.filter((todo) => todo.id !== action.todoId),
              }
            : dest
        ),
      };
  }
}
```

**Why it's problematic:**
- **O(n×m) complexity**: Every operation iterates destinations AND todos
- **Verbose reducers**: Simple updates require deep spreading
- **Re-renders**: Updating one todo recreates entire destinations array
- **Error-prone**: Easy to miss a level when spreading
- **Hard to extend**: Adding more nesting increases complexity exponentially

---

## Best Practice: Normalized Structure

### Flatten to Entity Collections

```tsx
// BEST PRACTICE: Normalized structure
interface NormalizedState {
  destinations: Record<string, {
    id: string;
    name: string;
  }>;
  todos: Record<string, {
    id: string;
    text: string;
    completed: boolean;
    destinationId: string;
  }>;
  // Optional: maintain order with ID arrays
  destinationIds: string[];
}
```

### Simple Reducer Operations

```tsx
function reducer(state: NormalizedState, action: Action): NormalizedState {
  switch (action.type) {
    case 'TOGGLE_TODO':
      const todo = state.todos[action.todoId];
      return {
        ...state,
        todos: {
          ...state.todos,
          [action.todoId]: { ...todo, completed: !todo.completed },
        },
      };

    case 'DELETE_TODO':
      const { [action.todoId]: removed, ...remainingTodos } = state.todos;
      return {
        ...state,
        todos: remainingTodos,
      };

    case 'ADD_TODO':
      const newTodo = {
        id: action.id,
        text: action.text,
        completed: false,
        destinationId: action.destinationId,
      };
      return {
        ...state,
        todos: {
          ...state.todos,
          [action.id]: newTodo,
        },
      };

    case 'ADD_DESTINATION':
      return {
        ...state,
        destinations: {
          ...state.destinations,
          [action.id]: { id: action.id, name: action.name },
        },
        destinationIds: [...state.destinationIds, action.id],
      };
  }
}
```

**Benefits:**
- **O(1) lookups**: Direct access by ID
- **Simple updates**: No nested traversals
- **Minimal re-renders**: Only affected entities change
- **Clear logic**: Each operation is straightforward
- **Easy cross-entity queries**: Find all todos, search, filter

---

## Deriving Nested Views

When components need nested data, derive it from the normalized structure.

```tsx
// Selector to get todos for a destination
function getTodosForDestination(state: NormalizedState, destinationId: string) {
  return Object.values(state.todos).filter(
    (todo) => todo.destinationId === destinationId
  );
}

// Selector to get full destination with todos
function getDestinationWithTodos(state: NormalizedState, destinationId: string) {
  const destination = state.destinations[destinationId];
  const todos = getTodosForDestination(state, destinationId);
  return { ...destination, todos };
}

// Component usage
function DestinationCard({ destinationId }: { destinationId: string }) {
  const { state } = useItinerary();

  const destination = state.destinations[destinationId];
  const todos = getTodosForDestination(state, destinationId);

  return (
    <div>
      <h3>{destination.name}</h3>
      {todos.map((todo) => (
        <TodoItem key={todo.id} todoId={todo.id} />
      ))}
    </div>
  );
}
```

---

## Normalization Pattern

### Before: Nested

```tsx
{
  categories: [
    {
      id: '1',
      name: 'Electronics',
      products: [
        { id: 'p1', name: 'Phone', price: 999 },
        { id: 'p2', name: 'Laptop', price: 1299 },
      ],
    },
    {
      id: '2',
      name: 'Books',
      products: [
        { id: 'p3', name: 'React Guide', price: 49 },
      ],
    },
  ],
}
```

### After: Normalized

```tsx
{
  categories: {
    '1': { id: '1', name: 'Electronics' },
    '2': { id: '2', name: 'Books' },
  },
  products: {
    'p1': { id: 'p1', name: 'Phone', price: 999, categoryId: '1' },
    'p2': { id: 'p2', name: 'Laptop', price: 1299, categoryId: '1' },
    'p3': { id: 'p3', name: 'React Guide', price: 49, categoryId: '2' },
  },
  categoryIds: ['1', '2'],
}
```

---

## Using Immer for Complex Updates

Immer lets you write "mutable" code that produces immutable updates.

```bash
npm install immer
```

```tsx
import { produce } from 'immer';

function reducer(state: NormalizedState, action: Action): NormalizedState {
  return produce(state, (draft) => {
    switch (action.type) {
      case 'TOGGLE_TODO':
        draft.todos[action.todoId].completed = !draft.todos[action.todoId].completed;
        break;

      case 'DELETE_TODO':
        delete draft.todos[action.todoId];
        break;

      case 'UPDATE_DESTINATION':
        draft.destinations[action.id].name = action.name;
        break;

      case 'REORDER_DESTINATIONS':
        draft.destinationIds = action.newOrder;
        break;
    }
  });
}
```

---

## Advanced: Undo/Redo with Event Sourcing

Normalized data enables efficient undo/redo by storing action history.

```tsx
interface HistoryState {
  past: NormalizedState[];
  present: NormalizedState;
  future: NormalizedState[];
}

function historyReducer(state: HistoryState, action: Action): HistoryState {
  switch (action.type) {
    case 'UNDO':
      if (state.past.length === 0) return state;
      const previous = state.past[state.past.length - 1];
      return {
        past: state.past.slice(0, -1),
        present: previous,
        future: [state.present, ...state.future],
      };

    case 'REDO':
      if (state.future.length === 0) return state;
      const next = state.future[0];
      return {
        past: [...state.past, state.present],
        present: next,
        future: state.future.slice(1),
      };

    default:
      const newPresent = normalizedReducer(state.present, action);
      if (newPresent === state.present) return state;
      return {
        past: [...state.past, state.present],
        present: newPresent,
        future: [],
      };
  }
}
```

---

## Quick Reference

### Normalization Checklist

1. **Identify entities**: What are the distinct data types? (Users, Posts, Comments)
2. **Create collections**: Each entity gets its own `Record<string, Entity>`
3. **Add foreign keys**: Child entities reference parents by ID
4. **Maintain order**: Use ID arrays when order matters
5. **Create selectors**: Derive nested views when needed

### Nested vs Normalized

| Operation | Nested | Normalized |
|-----------|--------|------------|
| Find item | O(n×m) | O(1) |
| Update item | Deep spread | Single spread |
| Delete item | Filter nested | Delete key |
| Cross-entity query | Complex | Simple filter |
| Re-renders | All parents | Only changed |

### Common Selectors

```tsx
// Get all items of type
const allTodos = Object.values(state.todos);

// Get items by foreign key
const todosByDest = allTodos.filter(t => t.destinationId === destId);

// Get item by ID
const todo = state.todos[todoId];

// Check if item exists
const exists = todoId in state.todos;

// Get ordered items
const orderedDests = state.destinationIds.map(id => state.destinations[id]);
```

---

## Related Skills

- **react-state-antipatterns** - Store IDs not objects (redundant state)
- **react-reducer-patterns** - Combine normalization with useReducer
- **react-state-libraries** - Libraries like Redux Toolkit have normalization helpers
- **react-state-testing** - Normalized reducers are easy to test
