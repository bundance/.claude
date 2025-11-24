#!/usr/bin/env python3
"""
Deep validation of TypeScript configuration
Checks tsconfig.json settings, paths, and type declarations
"""

import json
import os
import sys
from pathlib import Path

def read_tsconfig(path='tsconfig.json'):
    """Read and parse tsconfig.json with extends resolution"""
    try:
        with open(path, 'r') as f:
            # Remove comments (simplified)
            content = f.read()
            lines = []
            for line in content.split('\n'):
                if not line.strip().startswith('//'):
                    lines.append(line)
            clean_content = '\n'.join(lines)
            config = json.loads(clean_content)
            
            # Handle extends
            if 'extends' in config:
                base_path = config['extends']
                if not base_path.startswith('.'):
                    # Module extend
                    base_path = f'node_modules/{base_path}/tsconfig.json'
                
                if os.path.exists(base_path):
                    base_config = read_tsconfig(base_path)
                    # Merge configs
                    base_config.update(config)
                    return base_config
            
            return config
    except Exception as e:
        print(f"Error reading tsconfig: {e}")
        return None

def check_compiler_options(config):
    """Validate compiler options"""
    options = config.get('compilerOptions', {})
    issues = []
    warnings = []
    
    # Check target
    target = options.get('target', 'ES3')
    if target.upper() in ['ES3', 'ES5']:
        warnings.append(f"Target '{target}' is quite old - consider ES2015 or newer")
    
    # Check module
    module = options.get('module')
    if not module:
        issues.append("No 'module' specified - defaulting to CommonJS")
    
    # Check lib
    if 'lib' not in options and target:
        warnings.append("No 'lib' specified - will use default for target")
    
    # Check paths without baseUrl
    if 'paths' in options and 'baseUrl' not in options:
        issues.append("'paths' requires 'baseUrl' to be set")
    
    # Check strict mode
    if not options.get('strict'):
        warnings.append("'strict' mode not enabled - consider enabling for better type safety")
    
    # Check for React
    jsx = options.get('jsx')
    if jsx and jsx != 'preserve' and 'react' not in options.get('types', []):
        warnings.append(f"JSX is '{jsx}' but @types/react may not be configured")
    
    return issues, warnings

def check_paths_mapping(config):
    """Validate path mappings"""
    options = config.get('compilerOptions', {})
    paths = options.get('paths', {})
    base_url = options.get('baseUrl', '.')
    
    issues = []
    
    for alias, targets in paths.items():
        for target in targets:
            # Remove wildcard
            clean_target = target.replace('*', '')
            full_path = os.path.join(base_url, clean_target)
            
            if not os.path.exists(full_path):
                issues.append(f"Path alias '{alias}' points to non-existent '{full_path}'")
    
    return issues

def check_include_exclude(config):
    """Validate include/exclude patterns"""
    include = config.get('include', ['**/*'])
    exclude = config.get('exclude', [])
    
    warnings = []
    
    if 'node_modules' not in exclude:
        warnings.append("'node_modules' not in exclude - may slow compilation")
    
    if not include:
        warnings.append("No 'include' specified - will compile all .ts files")
    
    return warnings

def check_type_declarations():
    """Check if @types packages are installed"""
    try:
        with open('package.json', 'r') as f:
            pkg = json.load(f)
    except:
        return []
    
    deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
    
    # Common packages that need @types
    needs_types = {
        'react': '@types/react',
        'react-dom': '@types/react-dom',
        'node': '@types/node',
        'jest': '@types/jest',
        'express': '@types/express'
    }
    
    missing = []
    for pkg_name, types_pkg in needs_types.items():
        if pkg_name in deps and types_pkg not in deps:
            missing.append(f"Install {types_pkg} for {pkg_name}")
    
    return missing

def main():
    print("=" * 70)
    print("TypeScript Config Validator")
    print("=" * 70)
    print()
    
    if not os.path.exists('tsconfig.json'):
        print("✗ tsconfig.json not found")
        sys.exit(1)
    
    print("✓ tsconfig.json found\n")
    
    config = read_tsconfig()
    if not config:
        print("Could not parse tsconfig.json")
        sys.exit(1)
    
    # Validate compiler options
    print("[1/4] Checking compiler options...")
    issues, warnings = check_compiler_options(config)
    
    if issues:
        print("  ✗ Issues:")
        for issue in issues:
            print(f"    • {issue}")
    if warnings:
        print("  ⚠ Warnings:")
        for warning in warnings:
            print(f"    • {warning}")
    if not issues and not warnings:
        print("  ✓ No issues")
    
    # Check path mappings
    print("\n[2/4] Checking path mappings...")
    path_issues = check_paths_mapping(config)
    if path_issues:
        print("  ✗ Issues:")
        for issue in path_issues:
            print(f"    • {issue}")
    else:
        print("  ✓ No issues")
    
    # Check include/exclude
    print("\n[3/4] Checking include/exclude patterns...")
    ie_warnings = check_include_exclude(config)
    if ie_warnings:
        print("  ⚠ Warnings:")
        for warning in ie_warnings:
            print(f"    • {warning}")
    else:
        print("  ✓ No issues")
    
    # Check type declarations
    print("\n[4/4] Checking type declarations...")
    missing_types = check_type_declarations()
    if missing_types:
        print("  ⚠ Missing type declarations:")
        for missing in missing_types:
            print(f"    • {missing}")
    else:
        print("  ✓ All common types installed")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("\n• Enable 'strict' mode for better type safety")
    print("• Use 'skipLibCheck' to speed up compilation")
    print("• Configure 'paths' for cleaner imports")
    print("• Exclude unnecessary directories (node_modules, dist, build)")
    print()

if __name__ == '__main__':
    main()
