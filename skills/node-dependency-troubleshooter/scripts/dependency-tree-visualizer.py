#!/usr/bin/env python3
"""
Generate visual dependency trees from lock files
Shows package hierarchy and highlights duplicates
"""

import json
import sys
import os
from collections import defaultdict

def load_npm_lock(filepath):
    """Load and parse npm package-lock.json"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    tree = {}
    duplicates = defaultdict(list)
    
    # Handle lockfileVersion 2/3
    if 'packages' in data:
        for path, pkg_info in data.get('packages', {}).items():
            if not path:  # Skip root
                continue
            
            parts = path.split('node_modules/')
            if len(parts) > 1:
                name = parts[-1]
                version = pkg_info.get('version', 'unknown')
                depth = len(parts) - 1
                
                duplicates[name].append({
                    'version': version,
                    'path': path,
                    'depth': depth
                })
    
    # Also handle lockfileVersion 1
    if 'dependencies' in data:
        def walk_deps(deps, prefix='', depth=0):
            for name, info in deps.items():
                version = info.get('version', 'unknown')
                full_path = f"{prefix}{name}"
                
                duplicates[name].append({
                    'version': version,
                    'path': full_path,
                    'depth': depth
                })
                
                if 'dependencies' in info:
                    walk_deps(info['dependencies'], f"{full_path}/node_modules/", depth + 1)
        
        walk_deps(data['dependencies'])
    
    return duplicates

def build_tree_structure(duplicates, focus_package=None):
    """Build hierarchical tree structure"""
    if focus_package and focus_package in duplicates:
        # Show only the focused package
        return {focus_package: duplicates[focus_package]}
    
    return duplicates

def print_tree(tree_data, show_duplicates_only=False, max_depth=None):
    """Print tree in ASCII format"""
    
    packages = sorted(tree_data.items(), key=lambda x: x[0])
    
    for pkg_name, instances in packages:
        # Check if duplicate
        unique_versions = set(inst['version'] for inst in instances)
        is_duplicate = len(unique_versions) > 1
        
        if show_duplicates_only and not is_duplicate:
            continue
        
        # Print package name
        marker = "⚠ " if is_duplicate else "  "
        print(f"{marker}{pkg_name}")
        
        # Group by version
        by_version = defaultdict(list)
        for inst in instances:
            by_version[inst['version']].append(inst)
        
        versions = sorted(by_version.items())
        
        for i, (version, locs) in enumerate(versions):
            is_last_version = (i == len(versions) - 1)
            version_prefix = "└─" if is_last_version else "├─"
            
            # Filter by depth if specified
            if max_depth is not None:
                locs = [loc for loc in locs if loc['depth'] <= max_depth]
            
            if not locs:
                continue
            
            print(f"  {version_prefix} {version} ({len(locs)} instance{'s' if len(locs) > 1 else ''})")
            
            # Show paths
            for j, loc in enumerate(locs[:5]):  # Show first 5 paths
                is_last_loc = (j == len(locs) - 1) or (j == 4)
                loc_prefix = "   └─" if is_last_version and is_last_loc else "   ├─" if is_last_version else "   │ ├─" if not is_last_loc else "   │ └─"
                
                # Simplify path for readability
                path = loc['path']
                if path.startswith('node_modules/'):
                    path = path[13:]  # Remove 'node_modules/' prefix
                
                # Show depth indicator
                depth_indicator = "  " * loc['depth']
                print(f"{loc_prefix} {depth_indicator}{path}")
            
            if len(locs) > 5:
                continuation_prefix = "   └─" if is_last_version else "   │ └─"
                print(f"{continuation_prefix} ... and {len(locs) - 5} more")
        
        print()

def analyze_depth(tree_data):
    """Analyze dependency depth statistics"""
    all_depths = []
    
    for pkg_name, instances in tree_data.items():
        for inst in instances:
            all_depths.append(inst['depth'])
    
    if not all_depths:
        return {}
    
    return {
        'max': max(all_depths),
        'avg': sum(all_depths) / len(all_depths),
        'total_packages': len(all_depths)
    }

def count_duplicates(tree_data):
    """Count packages with multiple versions"""
    duplicates = 0
    total_instances = 0
    
    for pkg_name, instances in tree_data.items():
        unique_versions = set(inst['version'] for inst in instances)
        if len(unique_versions) > 1:
            duplicates += 1
        total_instances += len(instances)
    
    return duplicates, total_instances, len(tree_data)

def main():
    print("=" * 70)
    print("Dependency Tree Visualizer")
    print("=" * 70)
    print()
    
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python3 dependency-tree-visualizer.py <lock-file> [options]")
        print("\nOptions:")
        print("  --package <name>    Focus on specific package")
        print("  --duplicates-only   Show only packages with multiple versions")
        print("  --max-depth <n>     Limit tree depth to n levels")
        print("\nExample:")
        print("  python3 dependency-tree-visualizer.py package-lock.json")
        print("  python3 dependency-tree-visualizer.py package-lock.json --package react")
        print("  python3 dependency-tree-visualizer.py package-lock.json --duplicates-only")
        sys.exit(1)
    
    lock_file = sys.argv[1]
    
    # Parse options
    focus_package = None
    duplicates_only = False
    max_depth = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--package' and i + 1 < len(sys.argv):
            focus_package = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--duplicates-only':
            duplicates_only = True
            i += 1
        elif sys.argv[i] == '--max-depth' and i + 1 < len(sys.argv):
            max_depth = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    # Check file exists
    if not os.path.exists(lock_file):
        print(f"Error: Lock file not found: {lock_file}")
        sys.exit(1)
    
    print(f"Analyzing: {lock_file}")
    if focus_package:
        print(f"Focusing on: {focus_package}")
    if duplicates_only:
        print("Mode: Duplicates only")
    if max_depth:
        print(f"Max depth: {max_depth}")
    print()
    
    # Load and parse lock file
    if lock_file.endswith('package-lock.json'):
        tree_data = load_npm_lock(lock_file)
    else:
        print("Error: Only package-lock.json is supported currently")
        print("Support for yarn.lock and pnpm-lock.yaml coming soon")
        sys.exit(1)
    
    # Build tree structure
    tree = build_tree_structure(tree_data, focus_package)
    
    if not tree:
        if focus_package:
            print(f"Package '{focus_package}' not found in dependency tree")
        else:
            print("No dependencies found")
        sys.exit(0)
    
    # Statistics
    print("=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print()
    
    depth_stats = analyze_depth(tree_data)
    dup_count, total_inst, unique_pkgs = count_duplicates(tree_data)
    
    print(f"Total unique packages: {unique_pkgs}")
    print(f"Total package instances: {total_inst}")
    print(f"Packages with duplicates: {dup_count}")
    if depth_stats:
        print(f"Max dependency depth: {depth_stats['max']}")
        print(f"Average depth: {depth_stats['avg']:.1f}")
    print()
    
    # Print tree
    print("=" * 70)
    print("DEPENDENCY TREE")
    print("=" * 70)
    print()
    print("Legend:")
    print("  ⚠  Package with multiple versions (duplicate)")
    print("     Single version package")
    print()
    
    print_tree(tree, show_duplicates_only=duplicates_only, max_depth=max_depth)
    
    # Recommendations
    if dup_count > 0:
        print("=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)
        print()
        print(f"Found {dup_count} package(s) with duplicate versions")
        print("\nTo deduplicate:")
        print("  npm dedupe")
        print("  # or")
        print("  yarn dedupe")
        print("  # or")
        print("  pnpm dedupe")
        print("\nFor specific packages, use overrides in package.json")
        print()

if __name__ == '__main__':
    main()
