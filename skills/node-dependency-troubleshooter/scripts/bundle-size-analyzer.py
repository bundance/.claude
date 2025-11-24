#!/usr/bin/env python3
"""
Analyze bundle size impact of dependencies
Helps optimize package weight for web/mobile apps
"""

import json
import subprocess
import sys

def get_package_size(package_name, version='latest'):
    """Get package size from npm registry"""
    try:
        cmd = ['npm', 'view', f'{package_name}@{version}', 'dist.unpackedSize', '--json']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        size = json.loads(result.stdout)
        return size
    except:
        return None

def format_size(bytes_size):
    """Format bytes to human readable"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"

def main():
    print("=" * 70)
    print("Bundle Size Analyzer")
    print("=" * 70)
    print()
    
    try:
        with open('package.json', 'r') as f:
            data = json.load(f)
    except:
        print("Error: Could not read package.json")
        sys.exit(1)
    
    deps = data.get('dependencies', {})
    
    print(f"Analyzing {len(deps)} dependencies...\n")
    
    sizes = []
    total_size = 0
    
    for pkg, version in deps.items():
        print(f"Checking {pkg}...", end='\r')
        size = get_package_size(pkg, version)
        if size:
            sizes.append((pkg, size, version))
            total_size += size
    
    print(" " * 50, end='\r')
    
    if not sizes:
        print("Could not determine package sizes")
        return
    
    # Sort by size
    sizes.sort(key=lambda x: x[1], reverse=True)
    
    print("=" * 70)
    print(f"TOTAL SIZE: {format_size(total_size)}")
    print("=" * 70)
    print("\nLargest dependencies:\n")
    
    for i, (pkg, size, version) in enumerate(sizes[:15], 1):
        percentage = (size / total_size) * 100
        print(f"{i:2d}. {pkg:30s} {format_size(size):>10s} ({percentage:5.1f}%)")
    
    # Heavy packages (>1MB)
    heavy = [(p, s) for p, s, v in sizes if s > 1024 * 1024]
    if heavy:
        print(f"\n⚠ {len(heavy)} package(s) over 1 MB:")
        for pkg, size in heavy[:5]:
            print(f"  • {pkg}: {format_size(size)}")
    
    print("\nRecommendations:")
    print("  • Consider lighter alternatives for heavy packages")
    print("  • Use bundler tree-shaking to remove unused code")
    print("  • Check bundlephobia.com for package analysis")
    print()

if __name__ == '__main__':
    main()
