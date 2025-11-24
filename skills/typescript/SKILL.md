---
name: TypeScript Best Practices
description: Comprehensive TypeScript coding standards and best practices for type-safe, maintainable code
---
# TypeScript Coding Standards

## Instructions

Follow these TypeScript best practices when writing or modifying TypeScript code:

---

## Type Safety & Patterns

### No `any` Type

**NEVER use `any` to bypass type errors**: Proactively find an alternative

```typescript
// ❌ NEVER use any
function handleData(data: any) {
    return data.something;
}

// ✅ Use specific types
interface MyData {
    something: string;
}

function handleData(data: MyData) {
    return data.something;
}

// ✅ Or use unknown for truly unknown data
function handleUnknown(data: unknown) {
    if (typeof data === 'object' && data !== null && 'something' in data) {
        return (data as MyData).something;
    }
}
```

**If you truly don't know the type:**

- Use `unknown` (forces type checking)
- Use type guards to narrow
- Document why type is unknown

**Any in Generic Functions**: When building generic functions, you may need to use `any` inside the function body when TypeScript cannot match runtime logic to type logic. Use `as any` for return statements in these cases. Outside of generic functions, use `any` extremely sparingly.

### Type Assertions

**LIMIT type casting unless absolutely necessary**: Always try to find the correct type, rather than casting to a type

```typescript
// ✅ OK - When you know more than TypeScript
const element = document.getElementById('my-element') as HTMLInputElement;
const value = element.value;

// ✅ OK - API response that you've validated
const response = await api.getData();
const user = response.data as User;  // You know the shape

// ❌ AVOID - Circumventing type safety
const data = getData() as any;  // WRONG - defeats TypeScript

// ❌ AVOID - Unsafe assertion
const value = unknownValue as string;  // Might not actually be string
```

### Discriminated Unions

**Discriminated Unions**: Proactively use discriminated unions to model data that can be in different shapes. Use switch statements to handle them. Prefer discriminated unions over "bag of optionals" to prevent impossible states.

```typescript
type LoadingState =
    | { status: 'idle' }
    | { status: 'loading' }
    | { status: 'success'; data: Data }
    | { status: 'error'; error: Error };

function Component({ state }: { state: LoadingState }) {
    // TypeScript narrows type based on status
    if (state.status === 'success') {
        return <Display data={state.data} />;  // data available here
    }

    if (state.status === 'error') {
        return <Error error={state.error} />;  // error available here
    }

    return <Loading />;
}
```

### React Children Type Compatibility

**React Children Type Compatibility**: When encountering React version mismatches (especially with component libraries having their own React types), NEVER use `any` to bypass ReactNode type errors. Instead, wrap the `children` prop in a React Fragment:

```ts
// ❌ Bad - Don't use any to bypass type errors
<Box>{children as any}</Box>

// ✅ Good - Wrap the `children` prop in a React Fragment
<Box><>{children}</></Box>
```

This approach ensures type safety and compatibility without compromising TypeScript's benefits.

### Readonly Properties

**Readonly Properties**: Use `readonly` properties for object types by default to prevent accidental mutation. Only omit `readonly` when the property is genuinely mutable.

### noUncheckedIndexedAccess

**noUncheckedIndexedAccess**: Be aware that if this tsconfig rule is enabled, indexing into objects and arrays returns `Type | undefined` instead of just `Type`.

---

## Strict Mode Configuration

TypeScript strict mode should be **enabled** in the project:

```json
// tsconfig.json
{
    "compilerOptions": {
        "strict": true,
        "noImplicitAny": true,
        "strictNullChecks": true
    }
}
```

**This means:**

- No implicit `any` types
- Null/undefined must be handled explicitly
- Type safety enforced

---

## Explicit Return Types

**Return Types**: When declaring functions at the top-level of a module, always declare their return types to help future understanding. Exception: Components returning JSX don't need explicit return type annotations.

### Function Return Types

```typescript
// ✅ CORRECT - Explicit return type
function getUser(id: number): Promise<User> {
    return apiClient.get(`/users/${id}`);
}

function calculateTotal(items: Item[]): number {
    return items.reduce((sum, item) => sum + item.price, 0);
}

// ❌ AVOID - Implicit return type (less clear)
function getUser(id: number) {
    return apiClient.get(`/users/${id}`);
}
```

### Component Return Types

```typescript
// React.FC already provides return type (ReactElement)
export const MyComponent: React.FC<Props> = ({ prop }) => {
    return <div>{prop}</div>;
};

// For custom hooks
function useMyData(id: number): { data: Data; isLoading: boolean } {
    const [data, setData] = useState<Data | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    return { data: data!, isLoading };
}
```

---

## Type Imports

**Import Type**: Use `import type` whenever importing types. Prefer top-level `import type { ... }` over inline `import { type ... }` to ensure imports are erased during transpilation.

```typescript
// ✅ CORRECT - Explicitly mark as type import
import type { User } from '~types/user';
import type { Post } from '~types/post';
import type { SxProps, Theme } from '@mui/material';

// ❌ AVOID - Mixed value and type imports
import { User } from '~types/user';  // Unclear if type or value
```

**Benefits:**

- Clearly separates types from values
- Better tree-shaking
- Prevents circular dependencies
- TypeScript compiler optimization

---

## Component Prop Interfaces

### Interface Pattern

```typescript
/**
 * Props for MyComponent
 */
interface MyComponentProps {
    /** The user ID to display */
    userId: number;

    /** Optional callback when action completes */
    onComplete?: () => void;

    /** Display mode for the component */
    mode?: 'view' | 'edit';

    /** Additional CSS classes */
    className?: string;
}

export const MyComponent: React.FC<MyComponentProps> = ({
    userId,
    onComplete,
    mode = 'view',  // Default value
    className,
}) => {
    return <div>...</div>;
};
```

**Key Points:**

- Separate interface for props
- JSDoc comments for each prop
- Optional props use `?`
- Provide defaults in destructuring

### Props with Children

```typescript
interface ContainerProps {
    children: React.ReactNode;
    title: string;
}

// React.FC automatically includes children type, but be explicit
export const Container: React.FC<ContainerProps> = ({ children, title }) => {
    return (
        <div>
            <h2>{title}</h2>
            {children}
        </div>
    );
};
```

---

## Utility Types

### Partial<T>

```typescript
// Make all properties optional
type UserUpdate = Partial<User>;

function updateUser(id: number, updates: Partial<User>) {
    // updates can have any subset of User properties
}
```

### Pick<T, K>

```typescript
// Select specific properties
type UserPreview = Pick<User, 'id' | 'name' | 'email'>;

const preview: UserPreview = {
    id: 1,
    name: 'John',
    email: 'john@example.com',
    // Other User properties not allowed
};
```

### Omit<T, K>

```typescript
// Exclude specific properties
type UserWithoutPassword = Omit<User, 'password' | 'passwordHash'>;

const publicUser: UserWithoutPassword = {
    id: 1,
    name: 'John',
    email: 'john@example.com',
    // password and passwordHash not allowed
};
```

### Required<T>

```typescript
// Make all properties required
type RequiredConfig = Required<Config>;  // All optional props become required
```

### Record<K, V>

```typescript
// Type-safe object/map
const userMap: Record<string, User> = {
    'user1': { id: 1, name: 'John' },
    'user2': { id: 2, name: 'Jane' },
};

```

---

## Type Guards

### Basic Type Guards

```typescript
function isUser(data: unknown): data is User {
    return (
        typeof data === 'object' &&
        data !== null &&
        'id' in data &&
        'name' in data
    );
}

// Usage
if (isUser(response)) {
    console.log(response.name);  // TypeScript now knows that `response` is User
}
```

---

## Generic Types

### Generic Functions

```typescript
function getById<T>(items: T[], id: number): T | undefined {
    return items.find(item => (item as any).id === id);
}

// Usage with type inference
const users: User[] = [...];
const user = getById(users, 123);  // Type: User | undefined
```

### Generic Components

```typescript
interface ListProps<T> {
    items: T[];
    renderItem: (item: T) => React.ReactNode;
}

export function List<T>({ items, renderItem }: ListProps<T>): React.ReactElement {
    return (
        <div>
            {items.map((item, index) => (
                <div key={index}>{renderItem(item)}</div>
            ))}
        </div>
    );
}

// Usage
<List<User>
    items={users}
    renderItem={(user) => <UserCard user={user} />}
/>
```

---

## Null/Undefined Handling

### Optional Chaining

```typescript
// ✅ CORRECT
const name = user?.profile?.name;

// Equivalent to:
const name = user && user.profile && user.profile.name;
```

### Nullish Coalescing

```typescript
// ✅ CORRECT
const displayName = user?.name ?? 'Anonymous';

// Only uses default if null or undefined
// (Different from || which triggers on '', 0, false)
```

### Non-Null Assertion (Use Carefully)

```typescript
// ✅ OK - When you're certain value exists
const data = queryClient.getQueryData<Data>(['data'])!;

// ⚠️ CAREFUL - Only use when you KNOW it's not null
// Better to check explicitly:
const data = queryClient.getQueryData<Data>(['data']);
if (data) {
    // Use data
}
```

---

## Code Organization

### Default Exports

**Default Exports**: Avoid default exports unless explicitly required by the framework (e.g., Next.js pages), or used extensively throughout the codebase. Always prefer named exports for clarity in imports.

### Enums

**Enums**: Do not introduce new enums. Use `as const` objects instead for enum-like behavior. Retain existing enums but understand numeric enums create reverse mappings.

```typescript
// ❌ AVOID - New enums
enum Status {
    Pending,
    Active,
    Completed
}

// ✅ PREFER - as const objects
const Status = {
    Pending: 'pending',
    Active: 'active',
    Completed: 'completed',
} as const;

type Status = typeof Status[keyof typeof Status];
```

### Interface Extends

**Interface Extends**: ALWAYS prefer interfaces when modeling inheritance. The `&` operator has terrible performance in TypeScript. Only use intersection types where `interface extends` is not possible.

```typescript
// ✅ PREFER - Use interface extends
interface BaseProps {
    id: string;
    name: string;
}

interface UserProps extends BaseProps {
    email: string;
}

// ❌ AVOID - Intersection types (poor performance)
type UserProps = BaseProps & {
    email: string;
};
```

---

## Documentation & Types

**JSDoc Comments**: Use JSDoc comments to annotate functions and types, but only when the behavior is not self-evident. Be concise. Use the `@link` tag to reference other functions/types within the same file.

```typescript
/**
 * Fetches user data by ID
 * @param id - The user ID to fetch
 * @returns Promise resolving to User object
 * @see {@link updateUser} for updating user data
 */
function getUser(id: number): Promise<User> {
    return apiClient.get(`/users/${id}`);
}
```

---

## Error Handling

**Throwing Errors**: Think carefully before implementing code that throws errors. For code requiring manual try-catch, consider using a Result type instead:

```ts
type Result<T, E extends Error> =
| { ok: true; value: T }
| { ok: false; error: E };
```

Only throw errors when they produce a desirable outcome in the system (e.g., in framework request handlers).

---

## Summary

**TypeScript Checklist:**

- ✅ Strict mode enabled
- ✅ No `any` type (use `unknown` if needed)
- ✅ Explicit return types on functions
- ✅ Use `import type` for type imports
- ✅ JSDoc comments on prop interfaces (when non-obvious)
- ✅ Utility types (Partial, Pick, Omit, Required, Record)
- ✅ Type guards for narrowing
- ✅ Discriminated unions over bag of optionals
- ✅ Optional chaining and nullish coalescing
- ✅ Interface extends over intersection types
- ✅ Named exports over default exports
- ✅ Readonly properties by default
- ❌ Avoid type assertions unless necessary
- ❌ Avoid new enums - use `as const` objects
