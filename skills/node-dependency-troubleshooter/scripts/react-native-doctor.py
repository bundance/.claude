#!/usr/bin/env python3
"""
React Native specific dependency checker
Validates React Native version compatibility and native dependencies
"""

import json
import os
import sys
import subprocess

def check_react_native():
    """Check if project uses React Native"""
    try:
        with open('package.json') as f:
            data = json.load(f)
        deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
        return 'react-native' in deps, deps.get('react-native'), deps
    except:
        return False, None, {}

def check_react_compatibility(deps):
    """Check React and React Native version compatibility"""
    rn_version = deps.get('react-native', '')
    react_version = deps.get('react', '')
    
    issues = []
    
    if not react_version:
        issues.append("React not found in dependencies")
        return issues
    
    # Extract major versions
    rn_major = int(rn_version.lstrip('^~>=<').split('.')[0]) if rn_version else 0
    react_major = int(react_version.lstrip('^~>=<').split('.')[0]) if react_version else 0
    
    # React Native 0.70+ requires React 18+
    if rn_major >= 70 and react_major < 18:
        issues.append(f"React Native {rn_version} requires React 18+, found {react_version}")
    
    # React Native 0.68-0.69 works with React 17-18
    if 68 <= rn_major < 70 and react_major > 18:
        issues.append(f"React Native {rn_version} may not support React {react_version}")
    
    return issues

def check_metro_config():
    """Check for Metro bundler configuration"""
    metro_files = ['metro.config.js', 'metro.config.json']
    
    for config in metro_files:
        if os.path.exists(config):
            return True, config
    
    return False, None

def check_native_dependencies(deps):
    """Identify native dependencies that may need linking"""
    native_deps = []
    
    # Common native modules
    known_native = [
        'react-native-vector-icons',
        'react-native-gesture-handler',
        'react-native-reanimated',
        'react-native-screens',
        'react-native-safe-area-context',
        '@react-native-async-storage/async-storage',
        'react-native-svg',
        'react-native-camera',
        'react-native-maps'
    ]
    
    for pkg in known_native:
        if pkg in deps:
            native_deps.append((pkg, deps[pkg]))
    
    return native_deps

def check_pods():
    """Check if iOS Pods are installed (macOS only)"""
    if not os.path.exists('ios'):
        return None, "No ios directory"
    
    podfile = os.path.join('ios', 'Podfile')
    if not os.path.exists(podfile):
        return False, "No Podfile found"
    
    pods_dir = os.path.join('ios', 'Pods')
    if not os.path.exists(pods_dir):
        return False, "Pods not installed - run: cd ios && pod install"
    
    return True, "Pods installed"

def check_gradle():
    """Check if Android Gradle is properly configured"""
    if not os.path.exists('android'):
        return None, "No android directory"
    
    gradle_file = os.path.join('android', 'build.gradle')
    if not os.path.exists(gradle_file):
        return False, "No build.gradle found"
    
    return True, "Gradle configured"

def main():
    print("=" * 70)
    print("React Native Doctor")
    print("=" * 70)
    print()
    
    # Check if React Native project
    is_rn, rn_version, deps = check_react_native()
    
    if not is_rn:
        print("✗ Not a React Native project")
        sys.exit(1)
    
    print(f"✓ React Native project detected: {rn_version}\n")
    
    # Check React compatibility
    print("[1/5] Checking React compatibility...")
    react_issues = check_react_compatibility(deps)
    
    if react_issues:
        print("  ✗ Issues:")
        for issue in react_issues:
            print(f"    • {issue}")
    else:
        print(f"  ✓ React {deps.get('react')} compatible with RN {rn_version}")
    
    # Check Metro config
    print("\n[2/5] Checking Metro bundler...")
    has_metro, metro_file = check_metro_config()
    
    if has_metro:
        print(f"  ✓ Metro config found: {metro_file}")
    else:
        print("  ⚠ No metro.config.js found")
        print("    May use default configuration")
    
    # Check native dependencies
    print("\n[3/5] Checking native dependencies...")
    native_deps = check_native_dependencies(deps)
    
    if native_deps:
        print(f"  Found {len(native_deps)} native module(s):")
        for pkg, version in native_deps:
            print(f"    • {pkg}: {version}")
        print("\n  ⚠ Native modules require linking")
        print("    Auto-linking should handle this automatically")
    else:
        print("  ✓ No common native dependencies detected")
    
    # Check iOS setup
    print("\n[4/5] Checking iOS setup...")
    pods_status, pods_msg = check_pods()
    
    if pods_status is None:
        print(f"  ℹ {pods_msg}")
    elif pods_status:
        print(f"  ✓ {pods_msg}")
    else:
        print(f"  ✗ {pods_msg}")
    
    # Check Android setup
    print("\n[5/5] Checking Android setup...")
    gradle_status, gradle_msg = check_gradle()
    
    if gradle_status is None:
        print(f"  ℹ {gradle_msg}")
    elif gradle_status:
        print(f"  ✓ {gradle_msg}")
    else:
        print(f"  ✗ {gradle_msg}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("\nFor native dependencies:")
    print("  iOS: cd ios && pod install")
    print("  Android: cd android && ./gradlew clean")
    print("\nCommon fixes:")
    print("  • Clear Metro cache: npx react-native start --reset-cache")
    print("  • Rebuild: npx react-native run-ios / run-android")
    print("  • Check autolinking: npx react-native config")
    print("\nFor Expo projects:")
    print("  • Use expo-doctor instead of this tool")
    print("  • Run: npx expo-doctor")
    print()

if __name__ == '__main__':
    main()
