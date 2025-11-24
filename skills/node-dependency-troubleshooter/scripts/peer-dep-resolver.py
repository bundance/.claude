#!/usr/bin/env python3
"""
Find compatible versions for peer dependency conflicts
Analyzes ERESOLVE errors and suggests compatible version combinations
"""

import json
import sys
import subprocess
import re
from collections import defaultdict

def parse_package_json():
    """Parse local package.json"""
    try:
        with open('package.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading package.json: {e}")
        return None

def get_package_info(package_name, version_range='latest'):
    """Get package information from npm registry"""
    try:
        cmd = ['npm', 'view', f'{package_name}@{version_range}', '--json']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return None

def parse_version_range(range_str):
    """Parse and simplify version ranges"""
    range_str = range_str.strip()
    
    # Handle common patterns
    if range_str.startswith('^'):
        version = range_str[1:]
        return {'type': 'caret', 'version': version}
    elif range_str.startswith('~'):
        version = range_str[1:]
        return {'type': 'tilde', 'version': version}
    elif range_str.startswith('>='):
        version = range_str[2:].strip()
        return {'type': 'gte', 'version': version}
    elif range_str.startswith('>'):
        version = range_str[1:].strip()
        return {'type': 'gt', 'version': version}
    elif range_str.startswith('<='):
        version = range_str[2:].strip()
        return {'type': 'lte', 'version': version}
    elif range_str.startswith('<'):
        version = range_str[1:].strip()
        return {'type': 'lt', 'version': version}
    elif range_str == '*' or range_str == '':
        return {'type': 'any', 'version': '*'}
    else:
        return {'type': 'exact', 'version': range_str}

def extract_peer_dependencies(package_name):
    """Get peer dependencies for a package"""
    info = get_package_info(package_name)
    if not info:
        return {}
    
    # Handle array response (multiple versions)
    if isinstance(info, list):
        info = info[0]
    
    return info.get('peerDependencies', {})

def analyze_peer_conflicts():
    """Analyze peer dependency conflicts in current project"""
    pkg_data = parse_package_json()
    if not pkg_data:
        return None
    
    all_deps = {
        **pkg_data.get('dependencies', {}),
        **pkg_data.get('devDependencies', {})
    }
    
    print("Analyzing peer dependencies...\n")
    
    peer_requirements = defaultdict(list)
    
    # Collect peer dependencies from all installed packages
    for pkg_name, version_range in all_deps.items():
        print(f"Checking {pkg_name}...", end='\r')
        peers = extract_peer_dependencies(pkg_name)
        
        for peer_name, peer_range in peers.items():
            peer_requirements[peer_name].append({
                'requiredBy': pkg_name,
                'range': peer_range,
                'parsed': parse_version_range(peer_range)
            })
    
    print(" " * 50, end='\r')  # Clear the line
    
    return peer_requirements, all_deps

def find_conflicts(peer_requirements):
    """Identify conflicting peer dependency requirements"""
    conflicts = {}
    
    for peer_name, requirements in peer_requirements.items():
        if len(requirements) <= 1:
            continue
        
        # Check if ranges are potentially incompatible
        ranges = [req['range'] for req in requirements]
        unique_ranges = set(ranges)
        
        if len(unique_ranges) > 1:
            conflicts[peer_name] = requirements
    
    return conflicts

def suggest_resolution(peer_name, requirements, current_version=None):
    """Suggest compatible versions for a peer dependency"""
    print(f"\n{'=' * 70}")
    print(f"CONFLICT: {peer_name}")
    print('=' * 70)
    
    print(f"\nRequired by {len(requirements)} package(s):\n")
    
    for req in requirements:
        print(f"  • {req['requiredBy']}: {req['range']}")
    
    if current_version:
        print(f"\nCurrently installed: {current_version}")
    
    # Analyze ranges
    print("\nAnalysis:")
    
    # Check for completely incompatible ranges
    has_caret = any(req['parsed']['type'] == 'caret' for req in requirements)
    has_tilde = any(req['parsed']['type'] == 'tilde' for req in requirements)
    has_exact = any(req['parsed']['type'] == 'exact' for req in requirements)
    
    if has_exact and (has_caret or has_tilde):
        print("  ⚠ Mix of exact and range versions - may be incompatible")
    
    # Try to find common version
    print("\nRecommended actions:")
    
    # Get latest version
    latest_info = get_package_info(peer_name, 'latest')
    if latest_info:
        if isinstance(latest_info, list):
            latest_info = latest_info[0]
        latest_version = latest_info.get('version', 'unknown')
        print(f"\n  1. Try latest version: {peer_name}@{latest_version}")
        print(f"     npm install {peer_name}@{latest_version}")
    
    # Suggest checking each package's latest version
    print(f"\n  2. Update packages to their latest versions:")
    for req in requirements:
        print(f"     npm install {req['requiredBy']}@latest")
    
    # Suggest using overrides
    print(f"\n  3. Force a specific version (npm 8.3+):")
    print(f"     Add to package.json:")
    print(f'     "overrides": {{')
    print(f'       "{peer_name}": "{latest_version if latest_info else "VERSION"}"')
    print(f'     }}')
    
    # Suggest using resolutions (Yarn)
    print(f"\n  4. Force version with Yarn resolutions:")
    print(f'     "resolutions": {{')
    print(f'       "{peer_name}": "{latest_version if latest_info else "VERSION"}"')
    print(f'     }}')
    
    return latest_version if latest_info else None

def main():
    print("=" * 70)
    print("Peer Dependency Resolver")
    print("=" * 70)
    print()
    
    # Check if package.json exists
    pkg_data = parse_package_json()
    if not pkg_data:
        print("Error: package.json not found or invalid")
        sys.exit(1)
    
    print(f"Project: {pkg_data.get('name', 'unknown')}\n")
    
    # Analyze peer dependencies
    result = analyze_peer_conflicts()
    if not result:
        print("Could not analyze dependencies")
        sys.exit(1)
    
    peer_requirements, all_deps = result
    
    if not peer_requirements:
        print("✓ No peer dependencies found or no conflicts detected")
        return
    
    # Find conflicts
    conflicts = find_conflicts(peer_requirements)
    
    if not conflicts:
        print("✓ No peer dependency conflicts detected!")
        print(f"\nAnalyzed {len(peer_requirements)} peer dependencies")
        return
    
    print(f"⚠ Found {len(conflicts)} peer dependency conflict(s)\n")
    
    # Show each conflict with suggestions
    for peer_name, requirements in conflicts.items():
        current_version = all_deps.get(peer_name)
        suggest_resolution(peer_name, requirements, current_version)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"\nTotal conflicts: {len(conflicts)}")
    print(f"Total dependencies analyzed: {len(all_deps)}")
    
    print("\nGeneral recommendations:")
    print("  1. Update all packages to latest compatible versions")
    print("  2. Use npm 8.3+ or Yarn for automatic peer dependency installation")
    print("  3. Use --legacy-peer-deps flag as temporary workaround")
    print("  4. Use overrides/resolutions to force specific versions")
    print("  5. Consider alternative packages with compatible peer deps")
    
    print("\nQuick fixes to try:")
    print("  npm install --legacy-peer-deps")
    print("  npm update")
    print("  npm dedupe")
    print()

if __name__ == '__main__':
    main()
