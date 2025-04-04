#!/usr/bin/env python3
"""
Build script to create a Windows executable for the Network Monitoring Dashboard
"""

import os
import sys
import subprocess
import shutil

def create_spec_file():
    """Create a PyInstaller spec file for Windows"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['network_dashboard.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=['numpy', 'matplotlib', 'matplotlib.backends.backend_tkagg'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NetworkMonitoringDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='generated-icon.png',
)
"""
    
    with open('NetworkMonitoringDashboard.spec', 'w') as spec_file:
        spec_file.write(spec_content)
    
    return True

def build_executable():
    """Build the Windows executable using PyInstaller with the spec file"""
    print("Creating Windows executable specification...")
    create_spec_file()
    
    print("Building Network Monitoring Dashboard Windows executable...")
    
    # Define the PyInstaller command
    cmd = [
        'pyinstaller',
        'NetworkMonitoringDashboard.spec',
        '--clean'
    ]
    
    # Run PyInstaller
    try:
        subprocess.run(cmd, check=True)
        print("Build specification completed!")
        print("The executable would be created in the dist/ directory")
        
        # Since we can't actually generate a Windows executable on Linux,
        # we'll create a batch file that can be run alongside the Python scripts
        create_windows_batch_file()
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False

def create_windows_batch_file():
    """Create a batch file for Windows as a backup/alternative"""
    batch_content = """@echo off
echo Starting Network Monitoring Dashboard...
python network_dashboard.py
pause
"""
    
    with open('NetworkMonitoringDashboard.bat', 'w') as batch_file:
        batch_file.write(batch_content)
    
    print("Created Windows batch file: NetworkMonitoringDashboard.bat")
    
    return True

if __name__ == "__main__":
    build_executable()