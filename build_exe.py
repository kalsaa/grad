#!/usr/bin/env python3
"""
Build script to create an executable for the Network Monitoring Dashboard
"""

import os
import sys
import subprocess
import shutil

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building Network Monitoring Dashboard executable...")
    
    # Define the PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=NetworkMonitoringDashboard',
        '--windowed',  # No console window
        '--onefile',   # Create a single executable file
        '--icon=generated-icon.png',  # Icon for the executable
        '--add-data=assets:assets',   # Include assets folder
        'network_dashboard.py'        # Main script
    ]
    
    # Run PyInstaller
    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        
        # Show the location of the executable
        if os.path.exists('dist/NetworkMonitoringDashboard'):
            print(f"Executable created at: {os.path.abspath('dist/NetworkMonitoringDashboard')}")
        elif os.path.exists('dist/NetworkMonitoringDashboard.exe'):
            print(f"Executable created at: {os.path.abspath('dist/NetworkMonitoringDashboard.exe')}")
        else:
            print("Executable should be located in the dist/ directory")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False

if __name__ == "__main__":
    build_executable()