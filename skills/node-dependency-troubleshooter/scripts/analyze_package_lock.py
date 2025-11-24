#!/usr/bin/env python3
"""
Analyze package lock files to identify duplicate dependencies
Supports package-lock.json (npm), yarn.lock, and pnpm-lock.yaml
"""

import json
import sys
import os
from collections import defaultdict
from pathlib import Path

def analyze_npm_lock(lock_file_path):
    """Analyze npm package-lock.json for duplicates"""
    with open(lock_file_path, 'r') as f:
        lock_data = json.load(f)
    
    packages = defaultdict(list)
    
    # Handle lockfileVersion 2 and 3 format
    if 'packages' in lock_data:
        for path, pkg_info in lock_data.get('packages', {}).items():
            if not path:  # Skip root
                continue
            
            # Extract package name from path
            parts = path.split('node_modules/')
            if len(parts) > 1:
                name = parts[-1]
                version = pkg_info.get('version', 'unknown')
                packages[name].append({
                    'version': version,
                    'path': path
                })
    
    # Also check dependencies format (lockfileVersion 1)
    if 'dependencies' in lock_data:
        def walk_deps(deps, prefix=''):
            for name, info in deps.items():
                version = info.get('version', 'unknown')
                full_path = f"{prefix}{name}"
                packages[name].append({
                    'version': version,
                    'path': full_path
                })
                if 'dependencies' in info:
                    walk_deps(info['dependencies'], f"{full_path}/node_modules/")
        
        walk_deps(lock_data['dependencies'], 'node_modules/')
    
    return packages

def analyze_yarn_lock(lock_file_path):
    """Analyze yarn.lock for duplicates"""
    with open(lock_file_path, 'r') as f:
        content = f.read()
    
    packages = defaultdict(list)
    current_package = None
    current_version = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        # New package declaration
        if line and not line.startswith(' ') and not line.startswith('#'):
            # Parse package name
            if '@' in line:
                # Handle scoped packages
                parts = line.split('@')
                if line.startswith('@'):
                    # @scope/package@version
                    name = '@' + parts[1]
                    current_package = name
                else:
                    # package@version
                    name = parts[0].strip('"').strip(',')
                    current_package = name
        
        # Version line
        elif line.startswith('version '):
            version = line.split('version ')[1].strip('"')
            current_version = version
            
            if current_package and current_version:
                packages[current_package].append({
                    'version': current_version,
                    'path': f"{current_package}@{current_version}"
                })
    
    return packages

def analyze_pnpm_lock(lock_file_path):
    """Analyze pnpm-lock.yaml for duplicates"""
    try:
        import yaml
    except ImportError:
        print("Error: PyYAML required for pnpm-lock.yaml analysis")
        print("Install with: pip install PyYAML --break-system-packages")
        return {}
    
    with open(lock_file_path, 'r') as f:
        lock_data = yaml.safe_load(f)
    
    packages = defaultdict(list)
    
    # pnpm stores packages in 'packages' key
    for pkg_spec, info in lock_data.get('packages', {}).items():
        # Parse package spec like /package/1.0.0
        if pkg_spec.startswith('/'):
            parts = pkg_spec[1:].rsplit('/', 1)
            if len(parts) == 2:
                name, version = parts
                packages[name].append({
                    'version': version,
                    'path': pkg_spec
                })
    
    return packages

def find_duplicates(packages):
    """Find packages with multiple versions"""
    duplicates = {}
    for name, versions in packages.items():
        unique_versions = {}
        for v_info in versions:
            version = v_info['version']
            if version not in unique_versions:
                unique_versions[version] = []
            unique_versions[version].append(v_info['path'])
        
        if len(unique_versions) > 1:
            duplicates[name] = unique_versions
    
    return duplicates

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_package_lock.py <path-to-lock-file>")
        print("\nSupported lock files:")
        print("  - package-lock.json (npm)")
        print("  - yarn.lock (yarn)")
        print("  - pnpm-lock.yaml (pnpm)")
        sys.exit(1)
    
    lock_file = sys.argv[1]
    
    if not os.path.exists(lock_file):
        print(f"Error: Lock file not found: {lock_file}")
        sys.exit(1)
    
    print(f"Analyzing: {lock_file}\n")
    
    # Determine lock file type and analyze
    packages = {}
    if lock_file.endswith('package-lock.json'):
        packages = analyze_npm_lock(lock_file)
    elif lock_file.endswith('yarn.lock'):
        packages = analyze_yarn_lock(lock_file)
    elif lock_file.endswith('pnpm-lock.yaml'):
        packages = analyze_pnpm_lock(lock_file)
    else:
        print("Error: Unsupported lock file type")
        print("Supported: package-lock.json, yarn.lock, pnpm-lock.yaml")
        sys.exit(1)
    
    # Find and report duplicates
    duplicates = find_duplicates(packages)
    
    if not duplicates:
        print("✓ No duplicate dependencies found!")
    else:
        print(f"✗ Found {len(duplicates)} packages with multiple versions:\n")
        
        for name, versions in sorted(duplicates.items()):
            print(f"  {name}:")
            for version, paths in sorted(versions.items()):
                print(f"    ├─ version {version}")
                for path in paths[:3]:  # Show first 3 paths
                    print(f"    │  └─ {path}")
                if len(paths) > 3:
                    print(f"    │  └─ ... and {len(paths) - 3} more")
            print()
        
        print(f"\nTotal packages analyzed: {len(packages)}")
        print(f"Packages with duplicates: {len(duplicates)}")
        print("\nRecommended actions:")
        print("  1. Run: npm dedupe (or yarn dedupe / pnpm dedupe)")
        print("  2. If using Expo: npx expo install --fix")
        print("  3. Consider using resolutions/overrides in package.json")

if __name__ == '__main__':
    main()
