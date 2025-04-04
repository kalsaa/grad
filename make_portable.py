#!/usr/bin/env python3
"""
Create a portable package of the Network Monitoring Dashboard
This script creates a zip file with all necessary files to run the dashboard
"""

import os
import sys
import shutil
import zipfile

def create_portable_package():
    """Create a portable package for the Network Monitoring Dashboard"""
    print("Creating portable package for Network Monitoring Dashboard...")
    
    # Create a temporary directory for the package
    if os.path.exists('portable'):
        shutil.rmtree('portable')
    os.makedirs('portable')
    
    # List of files to include
    files_to_include = [
        'network_dashboard.py',
        'network_analyzer.py',
        'dashboard_ui.py',
        'chart_components.py',
        'generated-icon.png',
        'README.md'
    ]
    
    # Copy files to the package directory
    for file in files_to_include:
        if os.path.exists(file):
            shutil.copy(file, os.path.join('portable', file))
            print(f"Added {file}")
        else:
            print(f"Warning: {file} not found, skipping")
    
    # Create assets directory if it doesn't exist
    os.makedirs(os.path.join('portable', 'assets'), exist_ok=True)
    
    # Copy assets
    if os.path.exists('assets'):
        for asset in os.listdir('assets'):
            asset_path = os.path.join('assets', asset)
            if os.path.isfile(asset_path):
                shutil.copy(asset_path, os.path.join('portable', 'assets', asset))
                print(f"Added asset: {asset}")
    
    # Create a batch/shell script to run the dashboard
    if os.name == 'nt':  # Windows
        with open(os.path.join('portable', 'run_dashboard.bat'), 'w') as f:
            f.write("@echo off\n")
            f.write("echo Starting Network Monitoring Dashboard...\n")
            f.write("python network_dashboard.py\n")
            f.write("pause\n")
        print("Created run_dashboard.bat")
    else:  # Linux/Mac
        with open(os.path.join('portable', 'run_dashboard.sh'), 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("echo Starting Network Monitoring Dashboard...\n")
            f.write("python3 network_dashboard.py\n")
        os.chmod(os.path.join('portable', 'run_dashboard.sh'), 0o755)
        print("Created run_dashboard.sh")
    
    # Create a requirements.txt file
    with open(os.path.join('portable', 'requirements.txt'), 'w') as f:
        f.write("numpy\n")
        f.write("matplotlib\n")
        f.write("kamene\n")
    print("Created requirements.txt")
    
    # Create an installation guide
    with open(os.path.join('portable', 'INSTALL.txt'), 'w') as f:
        f.write("Network Monitoring Dashboard - Installation Guide\n")
        f.write("==============================================\n\n")
        f.write("Prerequisites:\n")
        f.write("- Python 3.8 or higher\n")
        f.write("- Pip (Python package manager)\n\n")
        f.write("Installation Steps:\n")
        f.write("1. Install required Python packages:\n")
        f.write("   pip install -r requirements.txt\n\n")
        f.write("2. Run the dashboard:\n")
        f.write("   - On Windows: Double-click run_dashboard.bat\n")
        f.write("   - On Linux/Mac: Use terminal to run ./run_dashboard.sh\n\n")
        f.write("Note: For capturing real network packets, the application needs to be run with\n")
        f.write("administrator/root privileges.\n")
    print("Created INSTALL.txt")
    
    # Create a zip file
    shutil.make_archive('NetworkMonitoringDashboard', 'zip', 'portable')
    print(f"Portable package created: {os.path.abspath('NetworkMonitoringDashboard.zip')}")
    
    return True

if __name__ == "__main__":
    create_portable_package()