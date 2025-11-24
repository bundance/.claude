#!/usr/bin/env python3
"""
Resolve ESLint configuration conflicts
Validates plugins, extends chain, and compatibility
"""

import json
import os
import sys

def find_eslint_config():
    """Find ESLint configuration file"""
    configs = [
        'eslint.config.js',  # Flat config (ESLint 9+)
        '.eslintrc.js',
        '.eslintrc.cjs',
        '.eslintrc.json',
        '.eslintrc',
        'package.json'  # eslintConfig field
    ]
    
    for config in configs:
        if os.path.exists(config):
            if config == 'package.json':
                try:
                    with open(config) as f:
                        data = json.load(f)
                    if 'eslintConfig' in data:
                        return config, 'package.json-field'
                except:
                    continue
            else:
                return config, 'file'
    
    return None, None

def check_installed_packages():
    """Check which ESLint packages are installed"""
    try:
        with open('package.json') as f:
            data = json.load(f)
    except:
        return {}
    
    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
    
    eslint_packages = {}
    for pkg, version in deps.items():
        if pkg.startswith('eslint') or 'eslint-' in pkg:
            eslint_packages[pkg] = version
    
    return eslint_packages

def extract_extends_and_plugins(config_file):
    """Extract extends and plugins from config"""
    if config_file.endswith('.json') or config_file == 'package.json':
        try:
            with open(config_file) as f:
                data = json.load(f)
            
            if config_file == 'package.json':
                data = data.get('eslintConfig', {})
            
            return data.get('extends', []), data.get('plugins', [])
        except:
            return [], []
    
    # For .js files, we can't easily parse, return empty
    return [], []

def main():
    print("=" * 70)
    print("ESLint Config Resolver")
    print("=" * 70)
    print()
    
    # Find config
    config_file, config_type = find_eslint_config()
    
    if not config_file:
        print("✗ No ESLint configuration found")
        print("\nLooking for:")
        print("  • eslint.config.js (ESLint 9+ flat config)")
        print("  • .eslintrc.js, .eslintrc.json, .eslintrc")
        print("  • eslintConfig in package.json")
        sys.exit(1)
    
    print(f"✓ Found ESLint config: {config_file}\n")
    
    # Check installed packages
    print("[1/3] Checking installed ESLint packages...")
    eslint_packages = check_installed_packages()
    
    if not eslint_packages:
        print("  ✗ No ESLint packages found in package.json")
        print("  Install: npm install -D eslint")
        sys.exit(1)
    
    print(f"  ✓ Found {len(eslint_packages)} ESLint-related package(s):")
    for pkg, version in sorted(eslint_packages.items()):
        print(f"    • {pkg}: {version}")
    
    # Check ESLint version
    if 'eslint' in eslint_packages:
        version = eslint_packages['eslint']
        major_version = int(version.lstrip('^~>=<').split('.')[0])
        
        print(f"\n[2/3] ESLint version: {version}")
        
        if major_version >= 9:
            print("  ℹ ESLint 9+ uses flat config (eslint.config.js)")
            if config_file != 'eslint.config.js':
                print("  ⚠ Consider migrating to flat config format")
                print("    See: https://eslint.org/docs/latest/use/configure/migration-guide")
        else:
            print("  ℹ Using traditional config format")
    
    # Try to extract extends and plugins
    print("\n[3/3] Checking extends and plugins...")
    extends, plugins = extract_extends_and_plugins(config_file)
    
    if not extends and not plugins:
        print("  ⚠ Could not parse config (likely .js file)")
        print("  Manually verify extends and plugins match installed packages")
    else:
        # Check extends
        if extends:
            print("\n  Extends:")
            for ext in (extends if isinstance(extends, list) else [extends]):
                # Derive package name
                if ext.startswith('eslint:'):
                    print(f"    • {ext} (built-in)")
                else:
                    # Extract package name
                    pkg_name = ext
                    if '/' in pkg_name:
                        parts = pkg_name.split('/')
                        if pkg_name.startswith('@'):
                            pkg_name = f"{parts[0]}/{parts[1]}"
                        else:
                            pkg_name = parts[0]
                    
                    # Add eslint-config- prefix if not present
                    if not pkg_name.startswith('eslint-config-') and not pkg_name.startswith('@'):
                        pkg_name = f'eslint-config-{pkg_name}'
                    
                    installed = pkg_name in eslint_packages
                    status = "✓" if installed else "✗"
                    print(f"    {status} {ext}")
                    if not installed:
                        print(f"      Install: npm install -D {pkg_name}")
        
        # Check plugins
        if plugins:
            print("\n  Plugins:")
            for plugin in plugins:
                pkg_name = plugin
                
                # Add eslint-plugin- prefix if not present
                if not pkg_name.startswith('eslint-plugin-') and not pkg_name.startswith('@'):
                    pkg_name = f'eslint-plugin-{pkg_name}'
                
                installed = pkg_name in eslint_packages
                status = "✓" if installed else "✗"
                print(f"    {status} {plugin}")
                if not installed:
                    print(f"      Install: npm install -D {pkg_name}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("\n• Keep ESLint and plugins up to date")
    print("• Use TypeScript ESLint for TypeScript projects")
    print("• Consider migrating to flat config (ESLint 9+)")
    print("• Run: npx eslint --print-config . to see resolved config")
    print()

if __name__ == '__main__':
    main()
