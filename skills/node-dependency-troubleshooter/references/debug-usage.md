# Debug Package Usage Guide

## Installation
```bash
npm install debug
```

## Basic Usage

Create a debug instance by passing your module/namespace name:

```javascript
const debug = require('debug')('http');

debug('booting application');
debug('request received: %s', req.url);
```

## Enabling Debug Output

### Node.js
Set `DEBUG` environment variable:

```bash
# Enable all debuggers
DEBUG=* node app.js

# Enable specific namespace
DEBUG=http node app.js

# Enable multiple namespaces (comma or space delimited)
DEBUG=http,worker node app.js

# Enable with wildcard
DEBUG=worker:* node app.js

# Exclude specific namespaces
DEBUG=*,-not_this node app.js

# In npm scripts
{
  "scripts": {
    "debug": "DEBUG=* node app.js"
  }
}
```

### Windows (CMD)
```cmd
set DEBUG=* & node app.js
```

### Windows (PowerShell)
```powershell
$env:DEBUG = "*"
node app.js
```

## Namespacing Pattern

Use colons to separate features for better organization:

```javascript
const debug = require('debug')('myapp:database');
const debugQuery = require('debug')('myapp:database:query');
const debugConnection = require('debug')('myapp:database:connection');

debug('database initialized');
debugQuery('executing: SELECT * FROM users');
debugConnection('connection pool created');
```

Then enable selectively:
```bash
# Enable all database debugging
DEBUG=myapp:database:* node app.js

# Enable only queries
DEBUG=myapp:database:query node app.js
```

## Extending Debug Instances

```javascript
const log = require('debug')('auth');

// Create extended debuggers
const logSign = log.extend('sign');
const logLogin = log.extend('login');

log('hello');      // auth hello
logSign('hello');  // auth:sign hello
logLogin('hello'); // auth:login hello
```

## Formatters

Debug uses printf-style formatting:

| Format | Description | Example |
|--------|-------------|---------|
| `%O` | Pretty-print object (multi-line) | `debug('user: %O', userObj)` |
| `%o` | Pretty-print object (single line) | `debug('config: %o', config)` |
| `%s` | String | `debug('name: %s', userName)` |
| `%d` | Number | `debug('count: %d', 42)` |
| `%j` | JSON | `debug('data: %j', jsonData)` |
| `%%` | Literal % | `debug('100%% complete')` |

Example:
```javascript
const debug = require('debug')('app');
debug('User %s has %d items: %O', username, count, items);
```

## Timing Information

Debug automatically shows time between calls:
```javascript
const debug = require('debug')('http');

debug('request started');
// ... some work ...
debug('request completed');  // Shows "+50ms" if 50ms elapsed
```

## Conditional Debugging

Check if debugging is enabled before expensive operations:

```javascript
const debug = require('debug')('expensive');

if (debug.enabled) {
  // Only compute this if debugging is on
  debug('expensive data: %O', computeExpensiveData());
}
```

## Dynamic Enable/Disable

```javascript
const debug = require('debug');

// Enable programmatically
debug.enable('test');
console.log(debug.enabled('test')); // true

// Disable all
debug.disable();
```

## Best Practices for Troubleshooting

### 1. Use Descriptive Namespaces
```javascript
// Good: Clear hierarchy
const debug = require('debug')('myapp:api:auth:login');

// Bad: Vague
const debug = require('debug')('stuff');
```

### 2. Log Key State Transitions
```javascript
const debug = require('debug')('app:dependency');

debug('checking package.json');
debug('found %d dependencies', deps.length);
debug('resolving versions: %o', versions);
debug('installation complete');
```

### 3. Use Different Debuggers for Different Concerns
```javascript
const debugError = require('debug')('app:error');
const debugWarn = require('debug')('app:warn');
const debugInfo = require('debug')('app:info');

debugError('failed to install package: %s', err.message);
debugWarn('deprecated package detected: %s', pkg.name);
debugInfo('starting installation');
```

### 4. Include Context in Messages
```javascript
// Good: Includes context
debug('parsing package-lock.json at %s', lockfilePath);
debug('found conflict: %s@%s vs %s@%s', name, v1, name, v2);

// Bad: Missing context
debug('parsing file');
debug('found conflict');
```

## Environment Variables

Control debug behavior:

| Variable | Purpose |
|----------|---------|
| `DEBUG` | Enable/disable namespaces |
| `DEBUG_COLORS` | Force color output (0=off, 1=on) |
| `DEBUG_DEPTH` | Object inspection depth (default: 2) |
| `DEBUG_SHOW_HIDDEN` | Show hidden object properties |
| `DEBUG_HIDE_DATE` | Hide timestamp in non-TTY output |

Example:
```bash
DEBUG=* DEBUG_DEPTH=5 node app.js
```

## Using Debug in Scripts

For automated dependency troubleshooting scripts:

```javascript
const debug = require('debug')('depcheck');

function analyzeDependencies(packageJson) {
  debug('analyzing %s', packageJson.name);
  
  const deps = Object.keys(packageJson.dependencies || {});
  debug('found %d dependencies', deps.length);
  
  deps.forEach(dep => {
    debug('checking %s', dep);
    // analysis logic
  });
  
  debug('analysis complete');
}

// Enable with: DEBUG=depcheck node script.js
```
