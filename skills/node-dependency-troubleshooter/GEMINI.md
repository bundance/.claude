# Node Dependency Troubleshooter

Systematic approach to diagnosing and resolving Node.js dependency issues across npm, yarn, pnpm, and Expo ecosystems.

## Quick Start Diagnostic

Run the comprehensive diagnostic script first to identify issues:

```bash
python3 scripts/diagnose.py
```

This will check:

- package.json validity
- Package manager detection
- Node.js version compatibility
- Installed dependencies
- Expo-specific issues (if applicable)
- TypeScript and ESLint configuration

## Systematic Troubleshooting Workflow

### 1. Identify Error Type

Categorize into one of these common patterns:

**Installation Failures**
- `npm install` fails partway through
- Lock file corruption errors
- Network/registry errors
- Disk space or permission issues

**Resolution Conflicts**
- `ERESOLVE` errors (npm)
- Peer dependency conflicts
- Version range incompatibilities
- Duplicate package versions

**Runtime Errors**
- `Cannot find module 'X'`
- Module resolution failures
- Import/require errors
- Native module linking errors

**Configuration Errors**

- TypeScript: `Cannot find name`, `Module not found`
- ESLint: `Failed to load config`, plugin errors
- Build tool failures (Metro, Webpack, Vite)

**Expo-Specific**

- SDK version mismatches
- Native module duplicates
- Autolinking failures

### 2. Automated Analysis

Use provided scripts for detailed analysis:

```bash
# DIAGNOSTIC SCRIPTS
# Comprehensive diagnostic (run this first!)
python3 scripts/diagnose.py

# Check Node version compatibility
python3 scripts/check_node_version.py

# Strict engine validation
python3 scripts/engine-strict-validator.py

# DEPENDENCY ANALYSIS
# Analyze lock file for duplicates
python3 scripts/analyze_package_lock.py <path-to-lock-file>

# Visualize dependency tree
python3 scripts/dependency-tree-visualizer.py package-lock.json
python3 scripts/dependency-tree-visualizer.py package-lock.json --duplicates-only
python3 scripts/dependency-tree-visualizer.py package-lock.json --package react

# SECURITY & COMPATIBILITY
# Security audit analysis
python3 scripts/npm-audit-analyzer.py

# Breaking change detection before upgrading
python3 scripts/breaking-change-checker.py

# Bundle size analysis
python3 scripts/bundle-size-analyzer.py

# CONFLICT RESOLUTION
# Peer dependency resolution
python3 scripts/peer-dep-resolver.py

# Monorepo validation
python3 scripts/monorepo-checker.py

# CONFIGURATION VALIDATION
# TypeScript config validation
python3 scripts/typescript-config-validator.py

# ESLint config resolution
python3 scripts/eslint-config-resolver.py

# FRAMEWORK-SPECIFIC
# React Native specific checks
python3 scripts/react-native-doctor.py
```

### 3. Progressive Fix Strategy

Apply fixes in order from least to most destructive:

**Level 1: Non-destructive**

```bash
# Clear package manager cache
npm cache clean --force
# or
yarn cache clean
# or
pnpm store prune

# For Expo projects
npx expo start -c  # Clear Metro cache
```

**Level 2: Reinstall**

```bash
# Remove and reinstall node_modules
rm -rf node_modules
npm install
# or yarn install / pnpm install
```

**Level 3: Clean slate**

```bash
# Remove lock file and node_modules
rm -rf node_modules package-lock.json
npm install
```

**Level 4: Deduplication**

```bash
# After reinstall, deduplicate
npm dedupe
# or yarn dedupe / pnpm dedupe
```

**Level 5: Force resolution**

- Add resolutions/overrides to package.json (see references/expo-patterns.md)

**Level 6: Expo-specific fixes**
```bash
# For Expo projects only
npx expo install --check  # Check compatibility
npx expo install --fix    # Auto-fix versions
npx expo prebuild --clean # Regenerate native dirs (CNG only)
```

## Debug Package Integration

This skill uses the `debug` npm package for enhanced troubleshooting. When writing scripts or investigating issues:

### Installing Debug
```bash
npm install debug
```

### Using Debug in Troubleshooting

Add debug logging to custom scripts or when investigating package behavior:

```javascript
const debug = require('debug')('depcheck');

debug('analyzing package.json');
debug('found %d dependencies', count);
debug('conflict detected: %o', conflictData);
```

Enable debug output:
```bash
# Enable all debug output
DEBUG=* node script.js

# Enable specific namespace
DEBUG=depcheck node script.js

# Enable multiple namespaces
DEBUG=depcheck,npm,yarn node script.js
```

See `references/debug-usage.md` for complete debug package documentation.

## Common Error Patterns & Solutions

### "ERESOLVE unable to resolve dependency tree" (npm)

**Cause**: Peer dependency conflicts or version incompatibilities

**Solutions**:
1. Use `--legacy-peer-deps` flag: `npm install --legacy-peer-deps`
2. Update conflicting packages: `npm update <package>`
3. Add override in package.json
4. For Expo: `npx expo install --fix`

### "Module not found" / Import errors

**Cause**: Package not installed, wrong version, or cache issue

**Solutions**:
1. Verify package in package.json
2. Clear cache: `npm cache clean --force`
3. Reinstall: `rm -rf node_modules && npm install`
4. Clear Metro (Expo): `npx expo start -c`

### "Found duplicates for [package]" (Expo)

**Cause**: Multiple versions of native module

**Solutions**:
1. `npx expo install --fix`
2. `npm dedupe` (or yarn/pnpm equivalent)
3. Add resolution/override in package.json
4. Check `references/expo-patterns.md` for detailed strategies

### TypeScript "Cannot find module" or type errors

**Cause**: Misconfigured tsconfig.json or missing @types packages

**Solutions**:
1. Check `tsconfig.json` paths and moduleResolution
2. Install missing types: `npm install -D @types/<package>`
3. Verify `include` and `exclude` in tsconfig.json
4. Clear TypeScript cache: `rm -rf .tsbuildinfo`

### ESLint configuration errors

**Cause**: Missing plugins, incompatible versions, or config issues

**Solutions**:
1. Install missing ESLint plugins
2. Check ESLint config extends and plugins match installed packages
3. Update ESLint and plugins to compatible versions
4. For Expo: verify `eslint-config-expo` version

## When to Use References

- **references/expo-patterns.md**: For Expo-specific dependency issues, SDK upgrades, native module duplicates
- **references/debug-usage.md**: When adding debug logging to troubleshooting scripts or investigating package behavior in depth

## Key Principles

**Start conservatively**: Try least destructive fixes first (cache clear, reinstall) before modifying package.json or lock files.

**Preserve context**: When modifying configs, comment out old values rather than deleting them immediately.

**Verify incrementally**: Test after each fix to isolate what resolved the issue.

**Check compatibility**: Always verify Node version, package manager version, and peer dependencies align.

**Use automation**: Leverage scripts and tools (expo-doctor, analyze_package_lock.py) rather than manual inspection.

**Understand package managers**: npm, yarn, and pnpm handle resolution and deduplication differently.
