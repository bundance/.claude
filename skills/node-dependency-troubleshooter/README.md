# Node Dependency Troubleshooter

A comprehensive cross-platform extension for diagnosing and resolving Node.js dependency issues across npm, yarn, pnpm, and Expo ecosystems.

## Platform Support

This extension works with both:
- **Claude Code** (via `SKILL.md`)
- **Gemini CLI** (via `gemini-extension.json` and `GEMINI.md`)

## Features

- Comprehensive diagnostic scripts for identifying dependency issues
- Automated analysis of lock files, dependency trees, and conflicts
- Security audit analysis and breaking change detection
- TypeScript and ESLint configuration validation
- Expo-specific troubleshooting tools
- React Native compatibility checks
- Monorepo validation
- Bundle size analysis

## Installation

### Claude Code

```bash
# Copy to your Claude skills directory
cp -r . ~/.claude/skills/node-dependency-troubleshooter
```

### Gemini CLI

```bash
# Install from directory
gemini extensions install /path/to/node-dependency-troubleshooter
```

## Quick Start

Run the comprehensive diagnostic first:

```bash
python3 scripts/diagnose.py
```

This checks:
- package.json validity
- Package manager detection
- Node.js version compatibility
- Installed dependencies
- Expo-specific issues (if applicable)
- TypeScript and ESLint configuration

## Available Scripts

All scripts are located in the `scripts/` directory:

### Diagnostic Scripts
- `diagnose.py` - Comprehensive system diagnostic (start here!)
- `check_node_version.py` - Node version compatibility check
- `engine-strict-validator.py` - Strict engine validation

### Dependency Analysis
- `analyze_package_lock.py` - Analyze lock file for duplicates
- `dependency-tree-visualizer.py` - Visualize dependency trees
- `peer-dep-resolver.py` - Resolve peer dependency conflicts

### Security & Compatibility
- `npm-audit-analyzer.py` - Security audit analysis
- `breaking-change-checker.py` - Detect breaking changes before upgrade
- `bundle-size-analyzer.py` - Bundle size analysis

### Configuration Validation
- `typescript-config-validator.py` - Validate TypeScript configuration
- `eslint-config-resolver.py` - ESLint config resolution

### Framework-Specific
- `react-native-doctor.py` - React Native specific checks
- `monorepo-checker.py` - Monorepo validation

## Usage Examples

```bash
# Comprehensive diagnostic
python3 scripts/diagnose.py

# Analyze lock file for duplicate packages
python3 scripts/analyze_package_lock.py package-lock.json

# Visualize dependency tree
python3 scripts/dependency-tree-visualizer.py package-lock.json

# Show only duplicates
python3 scripts/dependency-tree-visualizer.py package-lock.json --duplicates-only

# Analyze specific package
python3 scripts/dependency-tree-visualizer.py package-lock.json --package react

# Run security audit analysis
python3 scripts/npm-audit-analyzer.py

# Check for breaking changes
python3 scripts/breaking-change-checker.py

# Validate TypeScript config
python3 scripts/typescript-config-validator.py

# Check React Native setup
python3 scripts/react-native-doctor.py
```

## Progressive Fix Strategy

Apply fixes from least to most destructive:

1. **Non-destructive**: Clear caches (`npm cache clean --force`)
2. **Reinstall**: Remove and reinstall node_modules
3. **Clean slate**: Remove lock file and node_modules
4. **Deduplication**: Run `npm dedupe`
5. **Force resolution**: Add resolutions/overrides to package.json
6. **Expo-specific**: Use `npx expo install --fix`

## Common Issues

### ERESOLVE Errors (npm)
```bash
npm install --legacy-peer-deps
# or
npx expo install --fix
```

### Module Not Found
```bash
npm cache clean --force
rm -rf node_modules
npm install
```

### Expo Duplicate Modules
```bash
npx expo install --fix
npm dedupe
```

### TypeScript Errors
```bash
# Validate config
python3 scripts/typescript-config-validator.py

# Install missing types
npm install -D @types/<package>
```

## References

Additional documentation in `references/`:
- `expo-patterns.md` - Expo-specific patterns and solutions
- `debug-usage.md` - Using the debug npm package for troubleshooting

## Requirements

- Python 3.x (for diagnostic scripts)
- Node.js and npm/yarn/pnpm
- Git (for some analysis features)

## License

MIT

## Contributing

Contributions welcome! This is a universal extension designed to work with multiple AI CLI platforms.
