#!/usr/bin/env python3
"""
Compile Aegis Media Creator to Windows .exe
Requires: pip install pyinstaller
"""

import os
import sys
import shutil
from pathlib import Path

def create_exe():
    """Create Windows executable using PyInstaller"""
    
    print("=" * 60)
    print("  AEGIS MEDIA CREATOR - EXE COMPILER")
    print("=" * 60)
    print()
    
    # Check for PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller not found!")
        print("Install with: pip install pyinstaller")
        return False
    
    # Create icon if not exists
    icon_path = Path("aegis-icon.ico")
    if not icon_path.exists():
        print("Creating application icon...")
        # Create a simple .ico file (placeholder)
        with open(icon_path, 'wb') as f:
            # Minimal ICO header
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x20\x00')
            f.write(b'\x68\x04\x00\x00\x16\x00\x00\x00')
            # Add some data for the icon
            f.write(b'\x00' * 1128)
    
    # PyInstaller command
    script = "aegis-media-creator.py"
    
    # Build command
    cmd = [
        'pyinstaller',
        '--onefile',  # Single exe file
        '--windowed',  # No console window
        '--name', 'AegisMediaCreator',
        '--icon', str(icon_path),
        '--add-data', f'{icon_path};.',  # Include icon
        '--distpath', 'dist',
        '--workpath', 'build',
        '--specpath', 'build',
        '--noconfirm',  # Overwrite without asking
        '--clean',  # Clean temporary files
        script
    ]
    
    print(f"Compiling {script} to .exe...")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    # Run PyInstaller
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        exe_path = Path('dist') / 'AegisMediaCreator.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"SUCCESS: Created {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            print()
            print("Distribution ready!")
            print(f"Upload {exe_path} to your website for users to download.")
            return True
        else:
            print("ERROR: .exe not found after compilation")
            return False
    else:
        print("ERROR: Compilation failed!")
        print(result.stderr)
        return False

if __name__ == "__main__":
    success = create_exe()
    sys.exit(0 if success else 1)