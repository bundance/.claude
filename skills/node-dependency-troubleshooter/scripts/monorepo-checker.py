#!/usr/bin/env python3
"""
Validate dependencies in monorepo workspaces
Supports npm workspaces, Yarn workspaces, pnpm workspaces, and Lerna
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict

def detect_monorepo_type():
    """Detect which monorepo tool is being used"""
    tools = []
    
    # Check for npm workspaces
    if os.path.exists('package.json'):
        try:
            with open('package.json', 'r') as f:
                data = json.load(f)
                if 'workspaces' in data:
                    tools.append('npm-workspaces')
        except:
            pass
    
    # Check for Lerna
    if os.path.exists('lerna.json'):
        tools.append('lerna')
    
    # Check for pnpm
    if os.path.exists('pnpm-workspace.yaml'):
        tools.append('pnpm-workspaces')
    
    # Check for Yarn (same as npm structure but presence of yarn.lock)
    if os.path.exists('yarn.lock') and 'npm-workspaces' in tools:
        tools.append('yarn-workspaces')
        tools.remove('npm-workspaces')
    
    return tools

def get_workspace_packages(monorepo_type):
    """Get list of workspace packages"""
    packages = []
    
    if monorepo_type in ['npm-workspaces', 'yarn-workspaces']:
        try:
            with open('package.json', 'r') as f:
                data = json.load(f)
                workspace_patterns = data.get('workspaces', [])
                
                # Handle object format
                if isinstance(workspace_patterns, dict):
                    workspace_patterns = workspace_patterns.get('packages', [])
                
                # Expand glob patterns
                for pattern in workspace_patterns:
                    # Simple glob expansion (supports packages/* pattern)
                    if '*' in pattern:
                        base = pattern.replace('/*', '').replace('*', '')
                        if os.path.exists(base):
                            for item in os.listdir(base):
                                path = os.path.join(base, item)
                                pkg_json = os.path.join(path, 'package.json')
                                if os.path.exists(pkg_json):
                                    packages.append(path)
                    else:
                        pkg_json = os.path.join(pattern, 'package.json')
                        if os.path.exists(pkg_json):
                            packages.append(pattern)
        except Exception as e:
            print(f"Error reading workspaces: {e}")
    
    elif monorepo_type == 'lerna':
        try:
            with open('lerna.json', 'r') as f:
                data = json.load(f)
                workspace_patterns = data.get('packages', ['packages/*'])
                
                for pattern in workspace_patterns:
                    if '*' in pattern:
                        base = pattern.replace('/*', '').replace('*', '')
                        if os.path.exists(base):
                            for item in os.listdir(base):
                                path = os.path.join(base, item)
                                pkg_json = os.path.join(path, 'package.json')
                                if os.path.exists(pkg_json):
                                    packages.append(path)
                    else:
                        pkg_json = os.path.join(pattern, 'package.json')
                        if os.path.exists(pkg_json):
                            packages.append(pattern)
        except Exception as e:
            print(f"Error reading lerna.json: {e}")
    
    elif monorepo_type == 'pnpm-workspaces':
        try:
            import yaml
            with open('pnpm-workspace.yaml', 'r') as f:
                data = yaml.safe_load(f)
                workspace_patterns = data.get('packages', [])
                
                for pattern in workspace_patterns:
                    if '*' in pattern:
                        base = pattern.replace('/*', '').replace('*', '')
                        if os.path.exists(base):
                            for item in os.listdir(base):
                                path = os.path.join(base, item)
                                pkg_json = os.path.join(path, 'package.json')
                                if os.path.exists(pkg_json):
                                    packages.append(path)
                    else:
                        pkg_json = os.path.join(pattern, 'package.json')
                        if os.path.exists(pkg_json):
                            packages.append(pattern)
        except ImportError:
            print("Warning: PyYAML not installed, cannot parse pnpm-workspace.yaml")
        except Exception as e:
            print(f"Error reading pnpm-workspace.yaml: {e}")
    
    return packages

def read_package_info(package_path):
    """Read package.json from a workspace package"""
    try:
        pkg_json = os.path.join(package_path, 'package.json')
        with open(pkg_json, 'r') as f:
            data = json.load(f)
            return {
                'name': data.get('name', 'unknown'),
                'version': data.get('version', '0.0.0'),
                'dependencies': data.get('dependencies', {}),
                'devDependencies': data.get('devDependencies', {}),
                'peerDependencies': data.get('peerDependencies', {}),
                'path': package_path
            }
    except Exception as e:
        print(f"Error reading {package_path}/package.json: {e}")
        return None

def check_version_mismatches(packages_info):
    """Check for version mismatches across workspaces"""
    dependency_versions = defaultdict(lambda: defaultdict(list))
    
    for pkg in packages_info:
        all_deps = {
            **pkg['dependencies'],
            **pkg['devDependencies']
        }
        
        for dep_name, version in all_deps.items():
            dependency_versions[dep_name][version].append(pkg['name'])
    
    mismatches = {}
    for dep_name, versions in dependency_versions.items():
        if len(versions) > 1:
            mismatches[dep_name] = versions
    
    return mismatches

def check_workspace_references(packages_info):
    """Check workspace:* references and cross-package dependencies"""
    workspace_names = {pkg['name']: pkg for pkg in packages_info}
    issues = []
    
    for pkg in packages_info:
        all_deps = {
            **pkg['dependencies'],
            **pkg['devDependencies']
        }
        
        for dep_name, version in all_deps.items():
            # Check workspace:* protocol
            if version.startswith('workspace:'):
                if dep_name not in workspace_names:
                    issues.append({
                        'type': 'missing_workspace',
                        'package': pkg['name'],
                        'dependency': dep_name,
                        'message': f"References workspace package '{dep_name}' which doesn't exist"
                    })
            
            # Check if dependency is a workspace package but not using workspace protocol
            elif dep_name in workspace_names:
                if not version.startswith('workspace:') and not version.startswith('*'):
                    issues.append({
                        'type': 'non_workspace_protocol',
                        'package': pkg['name'],
                        'dependency': dep_name,
                        'current_version': version,
                        'message': f"Uses '{version}' instead of 'workspace:*' for workspace package"
                    })
    
    return issues

def find_circular_dependencies(packages_info):
    """Find circular dependencies between workspace packages"""
    workspace_names = {pkg['name']: pkg for pkg in packages_info}
    
    def has_circular_dep(pkg_name, target_name, visited=None):
        if visited is None:
            visited = set()
        
        if pkg_name in visited:
            return False
        
        visited.add(pkg_name)
        
        if pkg_name not in workspace_names:
            return False
        
        pkg = workspace_names[pkg_name]
        all_deps = {**pkg['dependencies'], **pkg['devDependencies']}
        
        for dep_name in all_deps:
            if dep_name == target_name:
                return True
            if dep_name in workspace_names:
                if has_circular_dep(dep_name, target_name, visited.copy()):
                    return True
        
        return False
    
    circular = []
    for pkg in packages_info:
        all_deps = {**pkg['dependencies'], **pkg['devDependencies']}
        
        for dep_name in all_deps:
            if dep_name in workspace_names:
                if has_circular_dep(dep_name, pkg['name']):
                    circular.append({
                        'from': pkg['name'],
                        'to': dep_name
                    })
    
    return circular

def main():
    print("=" * 70)
    print("Monorepo Dependency Checker")
    print("=" * 70)
    print()
    
    # Detect monorepo type
    monorepo_types = detect_monorepo_type()
    
    if not monorepo_types:
        print("✗ Not a monorepo or unsupported monorepo structure")
        print("\nSupported structures:")
        print("  - npm workspaces (package.json with 'workspaces' field)")
        print("  - Yarn workspaces (yarn.lock + workspaces in package.json)")
        print("  - pnpm workspaces (pnpm-workspace.yaml)")
        print("  - Lerna (lerna.json)")
        sys.exit(1)
    
    print(f"✓ Detected monorepo type: {', '.join(monorepo_types)}\n")
    
    # Get workspace packages
    packages = get_workspace_packages(monorepo_types[0])
    
    if not packages:
        print("✗ No workspace packages found")
        sys.exit(1)
    
    print(f"Found {len(packages)} workspace package(s):\n")
    
    # Read package info
    packages_info = []
    for pkg_path in packages:
        info = read_package_info(pkg_path)
        if info:
            packages_info.append(info)
            print(f"  • {info['name']} (v{info['version']}) at {pkg_path}")
    
    print()
    
    if not packages_info:
        print("✗ Could not read any package information")
        sys.exit(1)
    
    # Check for issues
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    # 1. Version mismatches
    print("\n[1] Checking for version mismatches across workspaces...")
    mismatches = check_version_mismatches(packages_info)
    
    if mismatches:
        print(f"  ⚠ Found {len(mismatches)} package(s) with version mismatches:\n")
        
        for dep_name, versions in sorted(mismatches.items())[:10]:  # Show first 10
            print(f"  {dep_name}:")
            for version, used_by in versions.items():
                print(f"    {version} used by: {', '.join(used_by[:3])}")
                if len(used_by) > 3:
                    print(f"      ... and {len(used_by) - 3} more")
        
        if len(mismatches) > 10:
            print(f"\n  ... and {len(mismatches) - 10} more packages with mismatches")
    else:
        print("  ✓ No version mismatches found")
    
    # 2. Workspace references
    print("\n[2] Checking workspace references...")
    ws_issues = check_workspace_references(packages_info)
    
    if ws_issues:
        print(f"  ⚠ Found {len(ws_issues)} workspace reference issue(s):\n")
        
        for issue in ws_issues[:10]:  # Show first 10
            print(f"  • {issue['package']}: {issue['message']}")
        
        if len(ws_issues) > 10:
            print(f"\n  ... and {len(ws_issues) - 10} more issues")
    else:
        print("  ✓ No workspace reference issues found")
    
    # 3. Circular dependencies
    print("\n[3] Checking for circular dependencies...")
    circular = find_circular_dependencies(packages_info)
    
    if circular:
        print(f"  ⚠ Found {len(circular)} circular dependency chain(s):\n")
        
        for circ in circular[:10]:
            print(f"  • {circ['from']} ↔ {circ['to']}")
        
        if len(circular) > 10:
            print(f"\n  ... and {len(circular) - 10} more circular dependencies")
    else:
        print("  ✓ No circular dependencies found")
    
    # Summary and recommendations
    print("\n" + "=" * 70)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 70)
    
    total_issues = len(mismatches) + len(ws_issues) + len(circular)
    
    if total_issues == 0:
        print("\n✓ No issues found! Monorepo dependencies are clean.")
    else:
        print(f"\n⚠ Found {total_issues} total issue(s)\n")
        
        if mismatches:
            print("Version Mismatches:")
            print("  - Use a single version across all workspaces for shared dependencies")
            print("  - Add dependency to root package.json if used by multiple workspaces")
            print("  - Consider using pnpm catalog feature for version management")
        
        if ws_issues:
            print("\nWorkspace References:")
            print("  - Use 'workspace:*' protocol for workspace dependencies")
            print("  - Ensure all referenced workspace packages exist")
            print("  - Run package manager install to fix missing links")
        
        if circular:
            print("\nCircular Dependencies:")
            print("  - Refactor code to break circular dependencies")
            print("  - Move shared code to a common package")
            print("  - Consider restructuring package boundaries")
    
    print("\nGeneral recommendations:")
    print("  - Run dedupe: npm dedupe (or yarn dedupe / pnpm dedupe)")
    print("  - Use --ignore-workspace-root-check if needed")
    print("  - Consider using workspace protocols for all internal deps")
    print()

if __name__ == '__main__':
    main()
