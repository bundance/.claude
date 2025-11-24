#!/usr/bin/env python3
"""
Comprehensive dependency diagnostic tool
Runs multiple checks and provides actionable recommendations
"""

import json
import sys
import os
import subprocess
from pathlib import Path

def run_command(cmd, check=False):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              check=check,
                              shell=isinstance(cmd, str))
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode
    except Exception as e:
        return "", str(e), 1

def detect_package_manager():
    """Detect which package manager is in use"""
    if os.path.exists('pnpm-lock.yaml'):
        return 'pnpm'
    elif os.path.exists('yarn.lock'):
        return 'yarn'
    elif os.path.exists('package-lock.json'):
        return 'npm'
    return None

def check_package_json():
    """Check if package.json exists and is valid"""
    if not os.path.exists('package.json'):
        return False, "package.json not found"
    
    try:
        with open('package.json', 'r') as f:
            data = json.load(f)
        return True, data
    except Exception as e:
        return False, f"Invalid package.json: {e}"

def check_node_modules():
    """Check if node_modules exists"""
    return os.path.exists('node_modules') and os.path.isdir('node_modules')

def detect_expo():
    """Check if this is an Expo project"""
    try:
        with open('package.json', 'r') as f:
            data = json.load(f)
        deps = data.get('dependencies', {})
        dev_deps = data.get('devDependencies', {})
        return 'expo' in deps or 'expo' in dev_deps
    except:
        return False

def main():
    print("=" * 60)
    print("Node.js Dependency Diagnostic Tool")
    print("=" * 60)
    print()
    
    issues = []
    recommendations = []
    
    # 1. Check package.json
    print("[1/8] Checking package.json...")
    valid, result = check_package_json()
    if not valid:
        print(f"  ✗ {result}")
        issues.append("Invalid or missing package.json")
        return
    else:
        print(f"  ✓ package.json found")
        package_data = result
        print(f"      Project: {package_data.get('name', 'unnamed')}")
        print(f"      Version: {package_data.get('version', 'unknown')}")
    
    # 2. Detect package manager
    print("\n[2/8] Detecting package manager...")
    pkg_manager = detect_package_manager()
    if pkg_manager:
        print(f"  ✓ Detected: {pkg_manager}")
    else:
        print("  ⚠ No lock file found - project may not be installed")
        issues.append("No lock file present")
    
    # 3. Check Node.js version
    print("\n[3/8] Checking Node.js version...")
    node_ver, _, exit_code = run_command(['node', '--version'])
    if exit_code == 0:
        print(f"  ✓ Node.js: {node_ver}")
        
        # Check engines field
        engines = package_data.get('engines', {})
        if 'node' in engines:
            print(f"      Required: {engines['node']}")
    else:
        print("  ✗ Node.js not found")
        issues.append("Node.js not installed")
    
    # 4. Check package manager version
    print(f"\n[4/8] Checking package manager versions...")
    for pm in ['npm', 'yarn', 'pnpm']:
        ver, _, exit_code = run_command([pm, '--version'])
        if exit_code == 0:
            marker = "✓" if pm == pkg_manager else " "
            print(f"  {marker} {pm}: v{ver}")
    
    # 5. Check node_modules
    print("\n[5/8] Checking node_modules...")
    if check_node_modules():
        print("  ✓ node_modules exists")
        
        # Count packages
        nm_path = Path('node_modules')
        try:
            # Count direct dependencies
            dirs = [d for d in nm_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            print(f"      ~{len(dirs)} packages installed")
        except:
            pass
    else:
        print("  ✗ node_modules not found")
        issues.append("Dependencies not installed")
        recommendations.append(f"Run: {pkg_manager} install")
    
    # 6. Check for Expo
    print("\n[6/8] Checking for Expo...")
    is_expo = detect_expo()
    if is_expo:
        print("  ✓ Expo project detected")
        
        # Try to run expo-doctor
        print("      Running expo-doctor...")
        stdout, stderr, exit_code = run_command('npx expo-doctor')
        if exit_code != 0:
            print("      ⚠ expo-doctor found issues")
            issues.append("Expo dependency issues detected")
            recommendations.append("Run: npx expo install --fix")
        else:
            print("      ✓ No Expo issues found")
    else:
        print("  - Not an Expo project")
    
    # 7. Check for TypeScript
    print("\n[7/8] Checking TypeScript configuration...")
    if os.path.exists('tsconfig.json'):
        print("  ✓ tsconfig.json found")
        
        # Check if typescript is installed
        deps = {**package_data.get('dependencies', {}), 
                **package_data.get('devDependencies', {})}
        if 'typescript' in deps:
            print(f"      TypeScript: {deps['typescript']}")
        else:
            print("      ⚠ TypeScript config exists but not in dependencies")
            issues.append("TypeScript not in dependencies")
            recommendations.append(f"Run: {pkg_manager} install -D typescript")
    else:
        print("  - No TypeScript configuration")
    
    # 8. Check for ESLint
    print("\n[8/8] Checking ESLint configuration...")
    eslint_configs = ['.eslintrc', '.eslintrc.js', '.eslintrc.json', 'eslint.config.js']
    eslint_found = any(os.path.exists(cfg) for cfg in eslint_configs)
    
    if eslint_found:
        print("  ✓ ESLint configuration found")
        deps = {**package_data.get('dependencies', {}), 
                **package_data.get('devDependencies', {})}
        if 'eslint' in deps:
            print(f"      ESLint: {deps['eslint']}")
        else:
            print("      ⚠ ESLint config exists but not in dependencies")
            issues.append("ESLint not in dependencies")
    else:
        print("  - No ESLint configuration")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if not issues:
        print("\n✓ No issues detected!")
    else:
        print(f"\n✗ Found {len(issues)} issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    if recommendations:
        print(f"\nRecommended actions:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Additional checks
    print("\nAdditional diagnostic commands:")
    if pkg_manager:
        print(f"  - Check for duplicates: python3 scripts/analyze_package_lock.py {pkg_manager}-lock*")
    print(f"  - Check Node compatibility: python3 scripts/check_node_version.py")
    if is_expo:
        print(f"  - Expo diagnostics: npx expo-doctor")
        print(f"  - Check dependencies: npx expo install --check")
    
    print()

if __name__ == '__main__':
    main()
