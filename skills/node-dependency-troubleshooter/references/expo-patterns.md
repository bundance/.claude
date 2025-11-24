# Expo Dependency Troubleshooting Patterns

## Common Causes of Dependency Issues

1. **SDK Version Misalignment**: Dependencies incompatible with installed Expo SDK
2. **Conflicting Transitive Dependencies**: Dependencies depend on incompatible versions of same packages
3. **Duplicate Packages**: Package manager has duplicated versions in dependency tree
4. **Unclean Package Manager State**: Corrupted cache or lock files

## Why Duplicates Matter

**Runtime Issues**: Packages acting as singletons (like `react`) break when multiple versions exist in bundle. Package state isn't stored globally but locally within each version.

**Native Linking Issues**: Expo Autolinking searches dependencies and links them into native build. Native modules can only have ONE version compiled, but JavaScript may be duplicated, causing mismatches.

## Expo-Specific Tools

### Check Dependencies
```bash
# Check which packages need updating
npx expo install --check

# Auto-fix invalid package versions
npx expo install --fix
```

### Expo Doctor
```bash
# Run comprehensive checks
npx expo-doctor

# Verbose output
npx expo-doctor --verbose
```

### Autolinking Verification
```bash
# List all native modules and highlight duplicates
expo-modules-autolinking verify -v
```

## Resolution Strategies

### 1. Expo Install Fix (First Try)
```bash
npx expo install --fix
```
Auto-updates packages to compatible versions for current SDK.

### 2. Deduplicate Dependencies
```bash
# npm
npm dedupe

# yarn
yarn dedupe

# pnpm
pnpm dedupe
```

### 3. Clean Reinstall
```bash
# Remove node_modules and lock file
rm -rf node_modules package-lock.json

# Clear cache
npm cache clean --force

# Reinstall
npm install
```

### 4. Force Resolution (package.json)
For persistent duplicates, force specific versions:

**npm (package.json)**:
```json
{
  "overrides": {
    "expo-dev-menu": "7.0.14"
  }
}
```

**yarn (package.json)**:
```json
{
  "resolutions": {
    "expo-dev-menu": "7.0.14"
  }
}
```

**pnpm (package.json)**:
```json
{
  "pnpm": {
    "overrides": {
      "expo-dev-menu": "7.0.14"
    }
  }
}
```

### 5. Clear Metro Cache
```bash
npx expo start -c
```

### 6. Regenerate Native Directories (CNG)
```bash
npx expo prebuild --clean
```

## Common Error Patterns

### "Found duplicates for [package]"
**Cause**: Multiple versions of native module installed
**Solution**: 
1. Run `npx expo install --fix`
2. If persists, use package manager deduplication
3. If still persists, add resolution/override in package.json

### "Module not found" / Import errors
**Cause**: Dependency not installed or wrong version
**Solution**:
1. Check package.json has dependency listed
2. Run `npx expo install [package]`
3. Clear Metro cache: `npx expo start -c`

### Peer dependency warnings
**Cause**: Package requires specific version of another package
**Solution**:
1. Run `npx expo install --check` to see mismatches
2. Install compatible versions
3. For npm, can use `--legacy-peer-deps` flag temporarily

### Build failures after SDK upgrade
**Cause**: Packages not compatible with new SDK version
**Solution**:
1. Run `npx expo install --fix` 
2. Check third-party package GitHub for new releases
3. May need to wait for package updates or find alternatives

## SDK Upgrade Workflow

1. Update expo package: `npx expo install expo@latest`
2. Run compatibility check: `npx expo install --check`
3. Auto-fix dependencies: `npx expo install --fix`
4. Clear caches: `npx expo start -c`
5. If using CNG: `npx expo prebuild --clean`
6. Test thoroughly

## Key Principles

- **Expo SDK determines version compatibility**: SDK version from `expo` package determines what dependency versions are tested and supported
- **Limited test matrix**: Only specific version ranges tested with each SDK release
- **Autolinking is critical**: Discovers and links native modules - duplicates cause compilation errors
- **React must be singleton**: Multiple React versions in bundle cause runtime errors
- **Package manager matters**: npm, yarn, pnpm handle deduplication differently
