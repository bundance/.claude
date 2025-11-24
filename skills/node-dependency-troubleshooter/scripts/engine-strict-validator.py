#!/usr/bin/env python3
"""
Strict validation against engines field in package.json
Validates Node.js, npm, yarn, pnpm versions and checks platform requirements
"""

import json
import sys
import os
import subprocess
import re
import platform

def get_current_versions():
    """Get currently installed versions of Node and package managers"""
    versions = {}
    
    # Node.js
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, check=True)
        versions['node'] = result.stdout.strip().lstrip('v')
    except:
        versions['node'] = None
    
    # npm
    try:
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, check=True)
        versions['npm'] = result.stdout.strip()
    except:
        versions['npm'] = None
    
    # Yarn
    try:
        result = subprocess.run(['yarn', '--version'], 
                              capture_output=True, text=True, check=True)
        versions['yarn'] = result.stdout.strip()
    except:
        versions['yarn'] = None
    
    # pnpm
    try:
        result = subprocess.run(['pnpm', '--version'], 
                              capture_output=True, text=True, check=True)
        versions['pnpm'] = result.stdout.strip()
    except:
        versions['pnpm'] = None
    
    return versions

def parse_semver(version_str):
    """Parse semantic version string into components"""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return {
            'major': int(match.group(1)),
            'minor': int(match.group(2)),
            'patch': int(match.group(3))
        }
    return None

def check_version_constraint(version, constraint):
    """Check if version satisfies constraint"""
    if not version or not constraint:
        return False
    
    constraint = constraint.strip()
    version_parts = parse_semver(version)
    
    if not version_parts:
        return False
    
    # Handle different constraint patterns
    if constraint.startswith('>='):
        required = parse_semver(constraint[2:].strip())
        if not required:
            return False
        if version_parts['major'] > required['major']:
            return True
        if version_parts['major'] == required['major']:
            if version_parts['minor'] > required['minor']:
                return True
            if version_parts['minor'] == required['minor']:
                return version_parts['patch'] >= required['patch']
        return False
    
    elif constraint.startswith('>'):
        required = parse_semver(constraint[1:].strip())
        if not required:
            return False
        if version_parts['major'] > required['major']:
            return True
        if version_parts['major'] == required['major']:
            if version_parts['minor'] > required['minor']:
                return True
            if version_parts['minor'] == required['minor']:
                return version_parts['patch'] > required['patch']
        return False
    
    elif constraint.startswith('<='):
        required = parse_semver(constraint[2:].strip())
        if not required:
            return False
        if version_parts['major'] < required['major']:
            return True
        if version_parts['major'] == required['major']:
            if version_parts['minor'] < required['minor']:
                return True
            if version_parts['minor'] == required['minor']:
                return version_parts['patch'] <= required['patch']
        return False
    
    elif constraint.startswith('<'):
        required = parse_semver(constraint[1:].strip())
        if not required:
            return False
        if version_parts['major'] < required['major']:
            return True
        if version_parts['major'] == required['major']:
            if version_parts['minor'] < required['minor']:
                return True
            if version_parts['minor'] == required['minor']:
                return version_parts['patch'] < required['patch']
        return False
    
    elif constraint.startswith('^'):
        # Caret range: ^1.2.3 := >=1.2.3 <2.0.0
        required = parse_semver(constraint[1:].strip())
        if not required:
            return False
        if version_parts['major'] != required['major']:
            return False
        if version_parts['minor'] > required['minor']:
            return True
        if version_parts['minor'] == required['minor']:
            return version_parts['patch'] >= required['patch']
        return False
    
    elif constraint.startswith('~'):
        # Tilde range: ~1.2.3 := >=1.2.3 <1.3.0
        required = parse_semver(constraint[1:].strip())
        if not required:
            return False
        if version_parts['major'] != required['major']:
            return False
        if version_parts['minor'] != required['minor']:
            return False
        return version_parts['patch'] >= required['patch']
    
    elif constraint == '*' or constraint == '':
        return True
    
    else:
        # Exact version
        required = parse_semver(constraint)
        if not required:
            return False
        return (version_parts['major'] == required['major'] and
                version_parts['minor'] == required['minor'] and
                version_parts['patch'] == required['patch'])
    
    return False

def get_platform_info():
    """Get current platform information"""
    system = platform.system().lower()
    
    # Map to npm platform names
    platform_map = {
        'darwin': 'darwin',
        'linux': 'linux',
        'windows': 'win32'
    }
    
    return {
        'os': platform_map.get(system, system),
        'arch': platform.machine(),
        'platform': platform.platform()
    }

def check_dependencies_engines(package_json_dir='node_modules'):
    """Check engines fields in all installed dependencies"""
    issues = []
    
    if not os.path.exists(package_json_dir):
        return []
    
    current_versions = get_current_versions()
    
    # Walk through node_modules
    for root, dirs, files in os.walk(package_json_dir):
        if 'package.json' in files:
            try:
                pkg_path = os.path.join(root, 'package.json')
                with open(pkg_path, 'r') as f:
                    data = json.load(f)
                
                engines = data.get('engines', {})
                if engines:
                    pkg_name = data.get('name', 'unknown')
                    
                    for engine, constraint in engines.items():
                        current = current_versions.get(engine)
                        if current and not check_version_constraint(current, constraint):
                            issues.append({
                                'package': pkg_name,
                                'engine': engine,
                                'required': constraint,
                                'current': current
                            })
            except:
                continue
        
        # Don't recurse into nested node_modules
        dirs[:] = [d for d in dirs if d != 'node_modules']
    
    return issues

def main():
    print("=" * 70)
    print("Engine Strict Validator")
    print("=" * 70)
    print()
    
    # Read package.json
    if not os.path.exists('package.json'):
        print("Error: package.json not found")
        sys.exit(1)
    
    try:
        with open('package.json', 'r') as f:
            pkg_data = json.load(f)
    except Exception as e:
        print(f"Error reading package.json: {e}")
        sys.exit(1)
    
    print(f"Project: {pkg_data.get('name', 'unknown')}")
    print(f"Version: {pkg_data.get('version', 'unknown')}")
    print()
    
    # Get current versions
    current_versions = get_current_versions()
    platform_info = get_platform_info()
    
    print("Current Environment:")
    print(f"  Platform: {platform_info['os']} ({platform_info['platform']})")
    print(f"  Architecture: {platform_info['arch']}")
    print(f"  Node.js: {current_versions['node'] or 'Not installed'}")
    print(f"  npm: {current_versions['npm'] or 'Not installed'}")
    print(f"  Yarn: {current_versions['yarn'] or 'Not installed'}")
    print(f"  pnpm: {current_versions['pnpm'] or 'Not installed'}")
    print()
    
    # Check engines field
    engines = pkg_data.get('engines', {})
    
    if not engines:
        print("✓ No engines field specified - any version accepted")
        print()
    else:
        print("=" * 70)
        print("ENGINES VALIDATION")
        print("=" * 70)
        print()
        
        all_valid = True
        
        for engine, constraint in engines.items():
            current = current_versions.get(engine)
            
            print(f"{engine}:")
            print(f"  Required: {constraint}")
            print(f"  Current: {current if current else 'Not installed'}")
            
            if not current:
                print(f"  Status: ✗ NOT INSTALLED")
                all_valid = False
            elif check_version_constraint(current, constraint):
                print(f"  Status: ✓ VALID")
            else:
                print(f"  Status: ✗ INVALID")
                all_valid = False
                
                # Suggest fix
                if engine == 'node':
                    # Extract version number from constraint
                    version_match = re.search(r'(\d+)', constraint)
                    if version_match:
                        suggested_version = version_match.group(1)
                        print(f"  Fix: Install Node.js {constraint}")
                        print(f"       nvm install {suggested_version}")
                        print(f"       nvm use {suggested_version}")
                elif engine in ['npm', 'yarn', 'pnpm']:
                    print(f"  Fix: Install {engine} with required version")
                    print(f"       npm install -g {engine}@{constraint}")
            
            print()
        
        if all_valid:
            print("✓ All engine requirements satisfied")
        else:
            print("✗ Some engine requirements not satisfied")
        print()
    
    # Check os field (platform restrictions)
    os_constraints = pkg_data.get('os', [])
    if os_constraints:
        print("Platform Restrictions:")
        current_os = platform_info['os']
        
        # os field can be array of allowed or denied (with !) platforms
        allowed = [o for o in os_constraints if not o.startswith('!')]
        denied = [o[1:] for o in os_constraints if o.startswith('!')]
        
        compatible = True
        
        if allowed and current_os not in allowed:
            compatible = False
            print(f"  ✗ Current platform '{current_os}' not in allowed list: {allowed}")
        
        if denied and current_os in denied:
            compatible = False
            print(f"  ✗ Current platform '{current_os}' is in denied list")
        
        if compatible:
            print(f"  ✓ Current platform '{current_os}' is compatible")
        print()
    
    # Check cpu field (architecture restrictions)
    cpu_constraints = pkg_data.get('cpu', [])
    if cpu_constraints:
        print("CPU Architecture Restrictions:")
        current_arch = platform_info['arch']
        
        allowed = [c for c in cpu_constraints if not c.startswith('!')]
        denied = [c[1:] for c in cpu_constraints if c.startswith('!')]
        
        compatible = True
        
        if allowed and current_arch not in allowed:
            compatible = False
            print(f"  ✗ Current architecture '{current_arch}' not in allowed list: {allowed}")
        
        if denied and current_arch in denied:
            compatible = False
            print(f"  ✗ Current architecture '{current_arch}' is in denied list")
        
        if compatible:
            print(f"  ✓ Current architecture '{current_arch}' is compatible")
        print()
    
    # Check dependencies' engines
    print("=" * 70)
    print("CHECKING DEPENDENCIES' ENGINE REQUIREMENTS")
    print("=" * 70)
    print()
    
    if not os.path.exists('node_modules'):
        print("⚠ node_modules not found - run npm install first")
    else:
        print("Scanning installed dependencies...")
        dep_issues = check_dependencies_engines()
        
        if not dep_issues:
            print("✓ All installed dependencies compatible with current environment")
        else:
            print(f"⚠ Found {len(dep_issues)} package(s) with engine mismatches:\n")
            
            for issue in dep_issues[:20]:  # Show first 20
                print(f"  • {issue['package']}")
                print(f"    {issue['engine']}: requires {issue['required']}, have {issue['current']}")
            
            if len(dep_issues) > 20:
                print(f"\n  ... and {len(dep_issues) - 20} more packages")
    
    print()
    
    # Summary and recommendations
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    if engines:
        print("To enforce engines strictly:")
        print("  1. Add .npmrc file with: engine-strict=true")
        print("  2. Run: npm config set engine-strict true")
        print("  3. This will prevent installation if engines don't match")
        print()
    
    print("Version management tools:")
    print("  • nvm (Node Version Manager): https://github.com/nvm-sh/nvm")
    print("  • volta: https://volta.sh/")
    print("  • fnm: https://github.com/Schniz/fnm")
    print()

if __name__ == '__main__':
    main()
