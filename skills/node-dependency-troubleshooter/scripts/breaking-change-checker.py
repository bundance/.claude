#!/usr/bin/env python3
"""
Check for breaking changes when upgrading packages
Identifies major version changes and fetches changelog information
"""

import json
import sys
import subprocess
import re

def get_package_versions(package_name, current_version):
    """Get available versions from npm registry"""
    try:
        cmd = ['npm', 'view', package_name, 'versions', '--json']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        versions = json.loads(result.stdout)
        return versions if isinstance(versions, list) else [versions]
    except:
        return []

def parse_version(version_str):
    """Parse semver version"""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str.lstrip('^~>=<'))
    if match:
        return tuple(map(int, match.groups()))
    return None

def is_major_bump(current, new):
    """Check if upgrade is a major version bump"""
    curr = parse_version(current)
    new_v = parse_version(new)
    if curr and new_v:
        return new_v[0] > curr[0]
    return False

def get_changelog_url(package_name):
    """Get changelog URL from package registry"""
    try:
        cmd = ['npm', 'view', package_name, 'repository.url', '--json']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        repo_url = json.loads(result.stdout)
        
        if repo_url:
            # Convert git URL to GitHub URL
            repo_url = repo_url.replace('git+', '').replace('.git', '')
            repo_url = repo_url.replace('git://', 'https://')
            
            # Append common changelog paths
            changelog_paths = [
                '/blob/main/CHANGELOG.md',
                '/blob/master/CHANGELOG.md',
                '/releases'
            ]
            
            return repo_url, [repo_url + path for path in changelog_paths]
    except:
        pass
    
    return None, []

def analyze_package_json():
    """Analyze package.json for potential upgrades"""
    try:
        with open('package.json', 'r') as f:
            data = json.load(f)
    except:
        return None
    
    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
    return deps

def main():
    print("=" * 70)
    print("Breaking Change Checker")
    print("=" * 70)
    print()
    
    deps = analyze_package_json()
    if not deps:
        print("Error: Could not read package.json")
        sys.exit(1)
    
    print(f"Analyzing {len(deps)} dependencies for potential breaking changes...\n")
    
    breaking_changes = []
    
    for pkg_name, current_version in deps.items():
        # Get latest version
        try:
            cmd = ['npm', 'view', pkg_name, 'version']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            latest_version = result.stdout.strip()
            
            # Check if major bump
            if is_major_bump(current_version, latest_version):
                repo, changelog_urls = get_changelog_url(pkg_name)
                
                breaking_changes.append({
                    'package': pkg_name,
                    'current': current_version,
                    'latest': latest_version,
                    'repo': repo,
                    'changelogs': changelog_urls
                })
                
                print(f"⚠ {pkg_name}: {current_version} → {latest_version} (MAJOR)")
        except:
            continue
    
    if not breaking_changes:
        print("\n✓ No major version bumps detected for current dependencies")
        print("  All updates would be minor or patch versions")
        return
    
    print("\n" + "=" * 70)
    print(f"FOUND {len(breaking_changes)} PACKAGE(S) WITH MAJOR VERSION CHANGES")
    print("=" * 70)
    
    for change in breaking_changes:
        print(f"\n{change['package']}")
        print(f"  Current: {change['current']}")
        print(f"  Latest: {change['latest']}")
        print(f"  ⚠ MAJOR version change - may contain breaking changes")
        
        if change['repo']:
            print(f"  Repository: {change['repo']}")
        
        if change['changelogs']:
            print(f"  Check changelog at:")
            for url in change['changelogs'][:2]:
                print(f"    • {url}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("\nBefore upgrading:")
    print("  1. Review changelogs for breaking changes")
    print("  2. Check migration guides")
    print("  3. Update one package at a time")
    print("  4. Test thoroughly after each upgrade")
    print("  5. Consider using --legacy-peer-deps if needed")
    print("\nTo upgrade specific package:")
    print("  npm install <package>@latest")
    print("\nTo see all outdated packages:")
    print("  npm outdated")
    print()

if __name__ == '__main__':
    main()
