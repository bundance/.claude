# Complete Quick Reference - All 14 Scripts

## 🚀 Quick Start
```bash
# Always start here
python3 scripts/diagnose.py
```

## 📋 All Scripts by Category

### Diagnostic
```bash
python3 scripts/diagnose.py                    # Comprehensive check
python3 scripts/check_node_version.py          # Node compatibility
python3 scripts/engine-strict-validator.py     # Strict engine check
```

### Dependency Analysis  
```bash
python3 scripts/analyze_package_lock.py <file> # Find duplicates
python3 scripts/dependency-tree-visualizer.py package-lock.json
python3 scripts/dependency-tree-visualizer.py package-lock.json --duplicates-only
python3 scripts/dependency-tree-visualizer.py package-lock.json --package react
```

### Security & Compatibility
```bash
python3 scripts/npm-audit-analyzer.py          # Security analysis
python3 scripts/breaking-change-checker.py     # Pre-upgrade check
python3 scripts/bundle-size-analyzer.py        # Size analysis
```

### Conflict Resolution
```bash
python3 scripts/peer-dep-resolver.py           # Resolve peer deps
python3 scripts/monorepo-checker.py            # Monorepo validation
```

### Configuration
```bash
python3 scripts/typescript-config-validator.py # TS config
python3 scripts/eslint-config-resolver.py      # ESLint config
```

### Framework-Specific
```bash
python3 scripts/react-native-doctor.py         # React Native
```

## 🔧 Progressive Fixes (Apply in Order)

### Level 1: Cache Clear
```bash
npm cache clean --force
yarn cache clean
pnpm store prune
npx expo start -c  # Metro (Expo)
```

### Level 2: Reinstall
```bash
rm -rf node_modules && npm install
```

### Level 3: Clean Slate
```bash
rm -rf node_modules package-lock.json && npm install
```

### Level 4: Deduplicate
```bash
npm dedupe
```

### Level 5: Force Resolutions
Add to package.json:
```json
{
  "overrides": { "package": "version" },      // npm
  "resolutions": { "package": "version" },    // yarn
  "pnpm": { "overrides": { "package": "version" } }  // pnpm
}
```

### Level 6: Expo Fixes
```bash
npx expo install --check
npx expo install --fix
npx expo-doctor
npx expo prebuild --clean  # CNG only
```

## 🎯 Common Scenarios

### Scenario: ERESOLVE Error
```bash
python3 scripts/peer-dep-resolver.py
npm install --legacy-peer-deps  # Quick fix
```

### Scenario: Module Not Found
```bash
python3 scripts/diagnose.py
npm cache clean --force
rm -rf node_modules && npm install
```

### Scenario: Duplicate Dependencies
```bash
python3 scripts/analyze_package_lock.py package-lock.json
npm dedupe
```

### Scenario: TypeScript Errors
```bash
python3 scripts/typescript-config-validator.py
rm -rf node_modules @types && npm install
```

### Scenario: Before Upgrading
```bash
python3 scripts/breaking-change-checker.py
python3 scripts/engine-strict-validator.py
npm outdated
```

### Scenario: Security Audit
```bash
python3 scripts/npm-audit-analyzer.py
npm audit fix
npm audit fix --force  # If needed
```

### Scenario: Bundle Too Large
```bash
python3 scripts/bundle-size-analyzer.py
# Check bundlephobia.com for alternatives
```

### Scenario: Monorepo Issues
```bash
python3 scripts/monorepo-checker.py
python3 scripts/dependency-tree-visualizer.py package-lock.json
npm dedupe
```

### Scenario: React Native Build Failure
```bash
python3 scripts/react-native-doctor.py
cd ios && pod install
cd android && ./gradlew clean
npx react-native start --reset-cache
```

### Scenario: Expo Build Issues
```bash
npx expo-doctor
python3 scripts/diagnose.py
npx expo install --fix
```

## 🔍 Advanced Usage

### Visualize Specific Package
```bash
python3 scripts/dependency-tree-visualizer.py package-lock.json --package react
```

### Show Only Duplicates
```bash
python3 scripts/dependency-tree-visualizer.py package-lock.json --duplicates-only
```

### Limit Tree Depth
```bash
python3 scripts/dependency-tree-visualizer.py package-lock.json --max-depth 3
```

### Analyze Audit from File
```bash
npm audit --json > audit.json
python3 scripts/npm-audit-analyzer.py audit.json
```

## 🐛 Debug Package Usage

```bash
# Enable debug output
DEBUG=* npm install
DEBUG=myapp:* node app.js
DEBUG=depcheck,npm node script.js

# In code
const debug = require('debug')('myapp');
debug('message: %s', variable);
```

## 📁 File Locations

- **Main skill**: `SKILL.md`
- **Scripts**: `scripts/*.py` (14 scripts)
- **References**: `references/expo-patterns.md`, `references/debug-usage.md`

## 🆘 Emergency Commands

```bash
# Nuclear option (last resort)
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# For Expo
rm -rf node_modules
npx expo install --fix
npx expo start -c

# For React Native  
rm -rf node_modules ios/Pods
npm install
cd ios && pod install
npx react-native start --reset-cache
```

## 💡 Pro Tips

1. **Always run diagnose.py first** - saves time
2. **Read the output** - scripts provide context
3. **One fix at a time** - easier to debug
4. **Test after each fix** - isolate what worked
5. **Check lock files** - commit them to git
6. **Use debug package** - for deep investigation
7. **Keep Node/npm updated** - prevents issues
8. **Read changelogs** - before major upgrades

## 📚 Learn More

- Expo: https://expo.fyi/resolving-dependency-issues
- npm docs: https://docs.npmjs.com/
- Debug package: https://github.com/debug-js/debug
- Bundlephobia: https://bundlephobia.com/
