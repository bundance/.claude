#!/usr/bin/env python3
"""
Check if current Node.js version matches package.json engines requirements
"""

import json
import sys
import os
import subprocess
import re

def get_node_version():
    """Get currently installed Node.js version"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        version = result.stdout.strip().lstrip('v')
        return version
    except Exception as e:
        print(f"Error getting Node version: {e}")
        return None

def parse_version_range(range_str):
    """Parse version range string (simplified)"""
    # Handle common patterns: >=14.0.0, ^16.0.0, ~18.0.0, 16.x, etc.
    range_str = range_str.strip()
    
    # Extract numeric version
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', range_str)
    if match:
        major, minor, patch = match.groups()
        return {
            'major': int(major),
            'minor': int(minor),
            'patch': int(patch),
            'operator': range_str[:match.start()].strip() or '='
        }
    
    # Handle X.x pattern
    match = re.search(r'(\d+)\.x', range_str)
    if match:
        return {
            'major': int(match.group(1)),
            'minor': 0,
            'patch': 0,
            'operator': '^'
        }
    
    return None

def version_satisfies(current, requirement):
    """Check if current version satisfies requirement (simplified)"""
    curr_parts = [int(x) for x in current.split('.')]
    
    if requirement['operator'] in ['>=', '']:
        return (curr_parts[0] > requirement['major'] or
                (curr_parts[0] == requirement['major'] and 
                 curr_parts[1] >= requirement['minor']))
    
    elif requirement['operator'] == '^':
        # Major must match, minor can be greater
        return (curr_parts[0] == requirement['major'] and 
                curr_parts[1] >= requirement['minor'])
    
    elif requirement['operator'] == '~':
        # Major and minor must match, patch can be greater
        return (curr_parts[0] == requirement['major'] and 
                curr_parts[1] == requirement['minor'] and
                curr_parts[2] >= requirement['patch'])
    
    elif requirement['operator'] in ['=', '==']:
        return current == f"{requirement['major']}.{requirement['minor']}.{requirement['patch']}"
    
    return True  # Default to compatible if we can't parse

def check_npm_version():
    """Get npm version"""
    try:
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return result.stdout.strip()
    except:
        return None

def check_yarn_version():
    """Get yarn version if installed"""
    try:
        result = subprocess.run(['yarn', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return result.stdout.strip()
    except:
        return None

def check_pnpm_version():
    """Get pnpm version if installed"""
    try:
        result = subprocess.run(['pnpm', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return result.stdout.strip()
    except:
        return None

def main():
    # Find package.json
    package_json_path = 'package.json'
    if len(sys.argv) > 1:
        package_json_path = sys.argv[1]
    
    if not os.path.exists(package_json_path):
        print(f"Error: package.json not found at {package_json_path}")
        sys.exit(1)
    
    # Read package.json
    with open(package_json_path, 'r') as f:
        package_data = json.load(f)
    
    print("=== Node.js Version Compatibility Check ===\n")
    
    # Get current Node version
    current_node = get_node_version()
    if not current_node:
        print("Error: Could not determine Node.js version")
        sys.exit(1)
    
    print(f"Current Node.js version: v{current_node}")
    
    # Check package manager versions
    npm_ver = check_npm_version()
    yarn_ver = check_yarn_version()
    pnpm_ver = check_pnpm_version()
    
    print(f"npm version: {npm_ver if npm_ver else 'not installed'}")
    if yarn_ver:
        print(f"yarn version: {yarn_ver}")
    if pnpm_ver:
        print(f"pnpm version: {pnpm_ver}")
    
    print()
    
    # Check engines field
    engines = package_data.get('engines', {})
    
    if not engines:
        print("✓ No engines field specified in package.json")
        print("  (Any Node.js version can be used)")
        return
    
    print("Required engines from package.json:")
    
    # Check Node requirement
    node_requirement = engines.get('node')
    if node_requirement:
        print(f"  node: {node_requirement}")
        
        parsed = parse_version_range(node_requirement)
        if parsed:
            compatible = version_satisfies(current_node, parsed)
            
            if compatible:
                print(f"  ✓ Current version (v{current_node}) is compatible")
            else:
                print(f"  ✗ Current version (v{current_node}) may not be compatible!")
                print(f"    Required: {node_requirement}")
                print(f"    Consider using nvm to switch Node versions:")
                print(f"      nvm install {parsed['major']}")
                print(f"      nvm use {parsed['major']}")
        else:
            print(f"  ⚠ Could not parse version requirement: {node_requirement}")
    
    # Check npm requirement
    npm_requirement = engines.get('npm')
    if npm_requirement:
        print(f"\n  npm: {npm_requirement}")
        if npm_ver:
            print(f"  Current: {npm_ver}")
        else:
            print("  ✗ npm not found")
    
    # Check yarn requirement  
    yarn_requirement = engines.get('yarn')
    if yarn_requirement:
        print(f"\n  yarn: {yarn_requirement}")
        if yarn_ver:
            print(f"  Current: {yarn_ver}")
        else:
            print("  ✗ yarn not found")
            print("  Install with: npm install -g yarn")
    
    # Check pnpm requirement
    pnpm_requirement = engines.get('pnpm')
    if pnpm_requirement:
        print(f"\n  pnpm: {pnpm_requirement}")
        if pnpm_ver:
            print(f"  Current: {pnpm_ver}")
        else:
            print("  ✗ pnpm not found")
            print("  Install with: npm install -g pnpm")
    
    # Additional info
    print("\n=== Additional Information ===")
    print(f"Project: {package_data.get('name', 'unknown')}")
    print(f"Version: {package_data.get('version', 'unknown')}")
    
    # Check for Expo
    deps = package_data.get('dependencies', {})
    if 'expo' in deps:
        print(f"\nExpo SDK detected: {deps['expo']}")
        print("Run 'npx expo-doctor' for Expo-specific checks")

if __name__ == '__main__':
    main()
