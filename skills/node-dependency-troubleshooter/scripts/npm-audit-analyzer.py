#!/usr/bin/env python3
"""
Parse and prioritize npm audit vulnerabilities
Helps understand security issues and suggests prioritized fixes
"""

import json
import sys
import subprocess
from collections import defaultdict

def run_npm_audit():
    """Run npm audit and return JSON output"""
    try:
        result = subprocess.run(['npm', 'audit', '--json'],
                              capture_output=True,
                              text=True,
                              check=False)
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Error: Could not parse npm audit output")
        return None
    except Exception as e:
        print(f"Error running npm audit: {e}")
        return None

def categorize_vulnerabilities(audit_data):
    """Categorize vulnerabilities by severity and type"""
    vulnerabilities = audit_data.get('vulnerabilities', {})
    
    by_severity = defaultdict(list)
    by_package = defaultdict(list)
    
    for pkg_name, vuln_info in vulnerabilities.items():
        severity = vuln_info.get('severity', 'unknown')
        
        vuln_detail = {
            'package': pkg_name,
            'severity': severity,
            'via': vuln_info.get('via', []),
            'effects': vuln_info.get('effects', []),
            'range': vuln_info.get('range', 'unknown'),
            'fixAvailable': vuln_info.get('fixAvailable', False)
        }
        
        by_severity[severity].append(vuln_detail)
        by_package[pkg_name].append(vuln_detail)
    
    return by_severity, by_package

def get_fix_commands(audit_data):
    """Generate fix commands based on audit data"""
    commands = []
    
    # Check if npm audit fix is available
    metadata = audit_data.get('metadata', {})
    vulnerabilities = metadata.get('vulnerabilities', {})
    
    total = vulnerabilities.get('total', 0)
    
    if total == 0:
        return []
    
    # Try automatic fix first
    commands.append({
        'command': 'npm audit fix',
        'description': 'Attempt automatic fix for non-breaking changes',
        'risk': 'low'
    })
    
    # Force fix for breaking changes
    commands.append({
        'command': 'npm audit fix --force',
        'description': 'Force fix including breaking changes (may break app)',
        'risk': 'high'
    })
    
    # Manual updates
    commands.append({
        'command': 'npm update',
        'description': 'Update all packages within their semver ranges',
        'risk': 'medium'
    })
    
    return commands

def analyze_impact(by_severity):
    """Analyze the impact of vulnerabilities"""
    severity_order = ['critical', 'high', 'moderate', 'low', 'info']
    
    impact = {
        'critical': 'IMMEDIATE ACTION REQUIRED - Known exploits, remote code execution',
        'high': 'HIGH PRIORITY - Serious security issues, potential data exposure',
        'moderate': 'MEDIUM PRIORITY - Security issues with limited scope',
        'low': 'LOW PRIORITY - Minor issues, limited attack vectors',
        'info': 'INFORMATIONAL - No immediate action required'
    }
    
    return [(sev, impact.get(sev, 'Unknown severity'), by_severity.get(sev, [])) 
            for sev in severity_order if sev in by_severity]

def main():
    print("=" * 70)
    print("NPM Security Audit Analyzer")
    print("=" * 70)
    print()
    
    # Check if audit data was provided via file
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                audit_data = json.load(f)
            print(f"Loaded audit data from: {sys.argv[1]}\n")
        except Exception as e:
            print(f"Error loading file: {e}")
            print("Falling back to running npm audit...\n")
            audit_data = run_npm_audit()
    else:
        print("Running npm audit...\n")
        audit_data = run_npm_audit()
    
    if not audit_data:
        print("Could not get audit data")
        sys.exit(1)
    
    # Get metadata
    metadata = audit_data.get('metadata', {})
    vulnerabilities = metadata.get('vulnerabilities', {})
    
    total = vulnerabilities.get('total', 0)
    
    if total == 0:
        print("✓ No vulnerabilities found!")
        return
    
    print(f"Found {total} vulnerabilities:\n")
    
    # Show counts by severity
    for severity in ['critical', 'high', 'moderate', 'low', 'info']:
        count = vulnerabilities.get(severity, 0)
        if count > 0:
            icon = '🔴' if severity == 'critical' else '🟠' if severity == 'high' else '🟡' if severity == 'moderate' else '⚪'
            print(f"  {icon} {severity.upper()}: {count}")
    
    print("\n" + "=" * 70)
    print("DETAILED ANALYSIS")
    print("=" * 70)
    
    # Categorize vulnerabilities
    by_severity, by_package = categorize_vulnerabilities(audit_data)
    
    # Analyze impact
    impact_analysis = analyze_impact(by_severity)
    
    for severity, description, vulns in impact_analysis:
        if not vulns:
            continue
        
        print(f"\n{severity.upper()} ({len(vulns)} issues)")
        print(f"Impact: {description}")
        print("-" * 70)
        
        for vuln in vulns[:5]:  # Show first 5 of each severity
            print(f"\n  Package: {vuln['package']}")
            print(f"  Range: {vuln['range']}")
            
            # Show vulnerability chain
            via = vuln.get('via', [])
            if via:
                print(f"  Via:")
                for v in via[:3]:  # Show first 3 in chain
                    if isinstance(v, dict):
                        title = v.get('title', 'Unknown')
                        url = v.get('url', '')
                        print(f"    - {title}")
                        if url:
                            print(f"      {url}")
                    elif isinstance(v, str):
                        print(f"    - {v}")
            
            # Show if fix is available
            fix_available = vuln.get('fixAvailable')
            if fix_available:
                if isinstance(fix_available, dict):
                    fix_name = fix_available.get('name', 'unknown')
                    fix_version = fix_available.get('version', 'unknown')
                    is_breaking = fix_available.get('isSemVerMajor', False)
                    breaking_text = ' (BREAKING CHANGE)' if is_breaking else ''
                    print(f"  Fix: Update to {fix_name}@{fix_version}{breaking_text}")
                else:
                    print(f"  Fix: Available")
            else:
                print(f"  Fix: Not available - may need to update or remove package")
        
        if len(vulns) > 5:
            print(f"\n  ... and {len(vulns) - 5} more {severity} vulnerabilities")
    
    print("\n" + "=" * 70)
    print("RECOMMENDED ACTIONS")
    print("=" * 70)
    
    fix_commands = get_fix_commands(audit_data)
    
    print("\nPriority order:\n")
    
    # High priority: Critical and High severity
    critical_count = vulnerabilities.get('critical', 0) + vulnerabilities.get('high', 0)
    if critical_count > 0:
        print(f"1. ADDRESS CRITICAL/HIGH SEVERITY ({critical_count} issues)")
        print("   These require immediate attention")
        print()
    
    # Show fix commands
    for i, cmd_info in enumerate(fix_commands, 1):
        risk_color = '🔴' if cmd_info['risk'] == 'high' else '🟡' if cmd_info['risk'] == 'medium' else '🟢'
        print(f"{i}. {cmd_info['command']}")
        print(f"   {cmd_info['description']}")
        print(f"   Risk: {risk_color} {cmd_info['risk'].upper()}")
        print()
    
    # Additional recommendations
    print("Additional steps:")
    print("  - Review package dependencies - can any vulnerable packages be removed?")
    print("  - Check for alternative packages without vulnerabilities")
    print("  - Update to latest compatible versions: npm update")
    print("  - For unfixable issues, evaluate the actual risk to your application")
    print()
    
    # Dependencies count
    deps = metadata.get('dependencies', {})
    print(f"Total dependencies scanned: {deps.get('total', 'unknown')}")
    print(f"Production dependencies: {deps.get('prod', 'unknown')}")
    print(f"Development dependencies: {deps.get('dev', 'unknown')}")
    print()

if __name__ == '__main__':
    main()
