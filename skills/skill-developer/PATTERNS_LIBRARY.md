# Common Patterns Library

Ready-to-use regex and glob patterns for skill triggers. Copy and customize for your skills.

---

## Intent Patterns (Regex)

### Feature/Endpoint Creation
```regex
(add|create|implement|build).*?(feature|endpoint|route|service|controller)
```

### Component Creation
```regex
(create|add|make|build).*?(component|UI|page|modal|dialog|form)
```

### Error Handling
```regex
(fix|handle|catch|debug).*?(error|exception|bug)
(add|implement).*?(try|catch|error.*?handling)
```

### Explanation Requests
```regex
(how does|how do|explain|what is|describe|tell me about).*?
```

### Testing
```regex
(write|create|add).*?(test|spec|unit.*?test)
```

---

## File Path Patterns (Glob)

### Frontend
```glob
**/src/**/*.tsx        # All React components
**/src/**/*.ts         # All TypeScript files
```

### Test Exclusions

```glob
**/*.test.ts                # TypeScript tests
**/*.test.tsx               # React component tests
**/*.spec.ts                # Spec files
```

---

## Content Patterns (Regex)

### Error Handling
```regex
try\s*\{                        # Try blocks
catch\s*\(                      # Catch blocks
throw new                        # Throw statements
```

### React/Components
```regex
export.*React\.FC               # React functional components
export default function.*       # Default function exports
useState|useEffect              # React hooks
```

---

**Usage Example:**

```json
{
  "my-skill": {
    "promptTriggers": {
      "intentPatterns": [
        "(create|add|build).*?(component|UI|page)"
      ]
    },
    "fileTriggers": {
      "pathPatterns": [
        "**/src/**/*.tsx"
      ],
      "contentPatterns": [
        "export.*React\\.FC",
        "useState|useEffect"
      ]
    }
  }
}
```

---

**Related Files:**
- [SKILL.md](SKILL.md) - Main skill guide
- [TRIGGER_TYPES.md](TRIGGER_TYPES.md) - Detailed trigger documentation
- [SKILL_RULES_REFERENCE.md](SKILL_RULES_REFERENCE.md) - Complete schema
