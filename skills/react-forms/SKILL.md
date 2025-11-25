---
name: react-forms
description: Use when building forms with multiple fields, handling form submissions, or needing validation. Covers FormData, server actions, useActionState, and Zod validation to eliminate useState boilerplate.
---

# Form Handling with FormData and Server Actions

## When to Use This Skill

Use this skill when:
- Building forms with 3+ fields
- You need server-side form processing
- Forms require validation
- You want progressive enhancement (works without JavaScript)
- File uploads are involved
- Using Next.js App Router

## Core Principle

**Use FormData and server actions instead of multiple useState hooks.** FormData automatically captures form values, server actions handle processing, and Zod provides type-safe validation. This eliminates boilerplate and enables progressive enhancement.

---

## Anti-pattern: useState for Every Field

### The Problem

Creating individual state variables and change handlers for each form field.

```tsx
// ANTI-PATTERN: Individual useState for each field
function TravelBookingForm() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [destination, setDestination] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [passengers, setPassengers] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleFirstNameChange = (e) => setFirstName(e.target.value);
  const handleLastNameChange = (e) => setLastName(e.target.value);
  const handleEmailChange = (e) => setEmail(e.target.value);
  // ... 4 more handlers

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await submitBooking({
        firstName, lastName, email, destination, startDate, endDate, passengers
      });
    } catch (err) {
      setErrors({ submit: err.message });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={firstName} onChange={handleFirstNameChange} />
      {/* ... many more inputs */}
    </form>
  );
}
```

**Why it's problematic:**
- 7+ useState calls for a simple form
- Manual change handlers for every input
- Easy to forget to wire up state to inputs
- Complex state synchronization
- No progressive enhancement
- Difficult to add new fields

---

## Best Practice: FormData + Server Actions

### Step 1: Create a Server Action

```tsx
// actions.ts
'use server';

import { z } from 'zod';

const bookingSchema = z.object({
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required'),
  email: z.string().email('Invalid email address'),
  destination: z.string().min(1, 'Destination is required'),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().min(1, 'End date is required'),
  passengers: z.coerce.number().min(1).max(10),
});

export type BookingFormState = {
  status: 'idle' | 'error' | 'success';
  errors?: Record<string, string[]>;
  message?: string;
};

export async function submitBooking(
  prevState: BookingFormState,
  formData: FormData
): Promise<BookingFormState> {
  // Convert FormData to object
  const rawData = Object.fromEntries(formData);

  // Validate with Zod
  const result = bookingSchema.safeParse(rawData);

  if (!result.success) {
    return {
      status: 'error',
      errors: result.error.flatten().fieldErrors,
    };
  }

  // Process validated data
  const validData = result.data;

  try {
    await saveBookingToDatabase(validData);
    return { status: 'success', message: 'Booking confirmed!' };
  } catch (error) {
    return { status: 'error', message: 'Failed to save booking' };
  }
}
```

### Step 2: Use useActionState in Component

```tsx
'use client';

import { useActionState } from 'react';
import { submitBooking, type BookingFormState } from './actions';

const initialState: BookingFormState = { status: 'idle' };

function TravelBookingForm() {
  const [state, formAction, isPending] = useActionState(
    submitBooking,
    initialState
  );

  return (
    <form action={formAction}>
      <div>
        <label htmlFor="firstName">First Name</label>
        <input id="firstName" name="firstName" required />
        {state.errors?.firstName && (
          <span className="error">{state.errors.firstName[0]}</span>
        )}
      </div>

      <div>
        <label htmlFor="lastName">Last Name</label>
        <input id="lastName" name="lastName" required />
        {state.errors?.lastName && (
          <span className="error">{state.errors.lastName[0]}</span>
        )}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" required />
        {state.errors?.email && (
          <span className="error">{state.errors.email[0]}</span>
        )}
      </div>

      <div>
        <label htmlFor="passengers">Passengers</label>
        <input id="passengers" name="passengers" type="number" min="1" max="10" defaultValue={1} />
      </div>

      <button type="submit" disabled={isPending}>
        {isPending ? 'Booking...' : 'Book Trip'}
      </button>

      {state.status === 'success' && (
        <div className="success">{state.message}</div>
      )}

      {state.status === 'error' && state.message && (
        <div className="error">{state.message}</div>
      )}
    </form>
  );
}
```

**Benefits:**
- Zero useState for form fields
- Automatic form data collection
- Server-side validation with Zod
- Type-safe throughout
- Loading state managed by useActionState
- Works without JavaScript (progressive enhancement)

---

## Zod Validation Patterns

### Common Field Validations

```tsx
import { z } from 'zod';

const formSchema = z.object({
  // Required string
  name: z.string().min(1, 'Name is required'),

  // Email validation
  email: z.string().email('Invalid email'),

  // Number coercion (FormData sends strings)
  age: z.coerce.number().min(18, 'Must be 18+'),

  // Date coercion
  birthDate: z.coerce.date(),

  // Optional with default
  newsletter: z.coerce.boolean().default(false),

  // Enum values
  tripType: z.enum(['one-way', 'round-trip']),

  // Conditional validation
  returnDate: z.string().optional(),
}).refine(
  (data) => data.tripType !== 'round-trip' || data.returnDate,
  { message: 'Return date required for round trips', path: ['returnDate'] }
);
```

### Displaying Validation Errors

```tsx
function FormField({ name, label, state, ...inputProps }) {
  const errors = state.errors?.[name];

  return (
    <div>
      <label htmlFor={name}>{label}</label>
      <input
        id={name}
        name={name}
        aria-invalid={errors ? 'true' : 'false'}
        aria-describedby={errors ? `${name}-error` : undefined}
        {...inputProps}
      />
      {errors && (
        <span id={`${name}-error`} className="error">
          {errors[0]}
        </span>
      )}
    </div>
  );
}
```

---

## When to Use FormData vs useState

### Use FormData When:

| Scenario | Reason |
|----------|--------|
| Traditional forms with submit buttons | Natural fit for form submissions |
| Server actions/mutations | Direct integration with server processing |
| Progressive enhancement needed | Works without JavaScript |
| Many form fields | Less boilerplate than useState |
| File uploads | FormData handles files naturally |
| Next.js App Router | Server actions are first-class |

### Use useState When:

| Scenario | Reason |
|----------|--------|
| Real-time validation on every keystroke | Need immediate feedback |
| Complex client-side logic between fields | Dynamic field dependencies |
| Search/filter interfaces | Instant filtering without submit |
| Controlled components with precise state | Fine-grained control needed |
| Wizard/multi-step forms with complex navigation | State persists across steps |

---

## Quick Reference

### Server Action Template

```tsx
'use server';

import { z } from 'zod';

const schema = z.object({ /* fields */ });

type FormState = {
  status: 'idle' | 'error' | 'success';
  errors?: Record<string, string[]>;
  message?: string;
};

export async function handleForm(
  prevState: FormState,
  formData: FormData
): Promise<FormState> {
  const result = schema.safeParse(Object.fromEntries(formData));

  if (!result.success) {
    return { status: 'error', errors: result.error.flatten().fieldErrors };
  }

  // Process result.data
  return { status: 'success', message: 'Done!' };
}
```

### useActionState Template

```tsx
'use client';

import { useActionState } from 'react';
import { handleForm, type FormState } from './actions';

function MyForm() {
  const [state, action, isPending] = useActionState(handleForm, { status: 'idle' });

  return (
    <form action={action}>
      {/* inputs with name attributes */}
      <button disabled={isPending}>
        {isPending ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

---

## Related Skills

- **react-state-antipatterns** - For the principle of minimal state
- **react-url-state** - When form state should persist in URL
- **react-state-machines** - For complex multi-step form flows
