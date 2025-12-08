#!/usr/bin/env python3
"""
Aegis OS Installer Build Script
Compiles both freemium and licensed installers to Windows .exe files

Requirements:
- Python 3.8+
- PyInstaller: pip install pyinstaller

Usage:
    python build-all-installers.py

Output:
    dist/AegisInstallerFreemium.exe
    dist/AegisInstallerLicensed.exe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


INSTALLERS = [
    {
        "name": "Freemium Installer",
        "script": "aegis-installer-freemium.py",
        "spec": "aegis-installer-freemium.spec",
        "output": "AegisInstallerFreemium.exe"
    },
    {
        "name": "Licensed Installer", 
        "script": "aegis-installer-licensed.py",
        "spec": "aegis-installer-licensed.spec",
        "output": "AegisInstallerLicensed.exe"
    }
]


def print_header():
    print()
    print("=" * 60)
    print("  AEGIS OS INSTALLER BUILD SYSTEM")
    print("=" * 60)
    print(f"  Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()


def check_requirements():
    print("[1/4] Checking requirements...")
    
    try:
        import PyInstaller
        print(f"  ✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("  ✗ PyInstaller not found!")
        print()
        print("  Install with: pip install pyinstaller")
        return False
    
    script_dir = Path(__file__).parent
    
    for installer in INSTALLERS:
        script_path = script_dir / installer["script"]
        if not script_path.exists():
            print(f"  ✗ Missing: {installer['script']}")
            return False
        print(f"  ✓ Found: {installer['script']}")
    
    print()
    return True


def create_icon_if_missing():
    print("[2/4] Checking icon file...")
    
    icon_path = Path(__file__).parent.parent / "aegis-icon.ico"
    
    if icon_path.exists():
        print(f"  ✓ Icon found: {icon_path}")
    else:
        print(f"  ! Creating placeholder icon: {icon_path}")
        with open(icon_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x20\x00')
            f.write(b'\x68\x04\x00\x00\x16\x00\x00\x00')
            f.write(b'\x00' * 1128)
        print("  ✓ Placeholder icon created")
    
    print()
    return True


def clean_build_dirs():
    print("[3/4] Cleaning build directories...")
    
    script_dir = Path(__file__).parent
    
    for dirname in ['build', '__pycache__']:
        dirpath = script_dir / dirname
        if dirpath.exists():
            shutil.rmtree(dirpath)
            print(f"  ✓ Removed: {dirname}/")
    
    dist_dir = script_dir / 'dist'
    dist_dir.mkdir(exist_ok=True)
    print(f"  ✓ Output directory: {dist_dir}/")
    
    print()
    return True


def build_installers():
    print("[4/4] Building installers...")
    print()
    
    script_dir = Path(__file__).parent
    results = []
    
    for i, installer in enumerate(INSTALLERS, 1):
        print(f"  [{i}/{len(INSTALLERS)}] Building {installer['name']}...")
        
        spec_path = script_dir / installer["spec"]
        
        if spec_path.exists():
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--distpath', str(script_dir / 'dist'),
                '--workpath', str(script_dir / 'build'),
                '--noconfirm',
                '--clean',
                str(spec_path)
            ]
        else:
            script_path = script_dir / installer["script"]
            icon_path = script_dir.parent / "aegis-icon.ico"
            
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',
                '--windowed',
                '--name', installer["output"].replace('.exe', ''),
                '--distpath', str(script_dir / 'dist'),
                '--workpath', str(script_dir / 'build'),
                '--noconfirm',
                '--clean',
                str(script_path)
            ]
            
            if icon_path.exists():
                cmd.extend(['--icon', str(icon_path)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(script_dir)
            )
            
            output_path = script_dir / 'dist' / installer["output"]
            
            if result.returncode == 0 and output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"      ✓ Success: {installer['output']} ({size_mb:.1f} MB)")
                results.append((installer["name"], True, size_mb))
            else:
                print(f"      ✗ Failed: {installer['output']}")
                if result.stderr:
                    for line in result.stderr.split('\n')[:5]:
                        if line.strip():
                            print(f"        {line}")
                results.append((installer["name"], False, 0))
                
        except Exception as e:
            print(f"      ✗ Error: {str(e)}")
            results.append((installer["name"], False, 0))
        
        print()
    
    return results


def print_summary(results):
    print("=" * 60)
    print("  BUILD SUMMARY")
    print("=" * 60)
    print()
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for name, success, size in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        size_str = f"({size:.1f} MB)" if success else ""
        print(f"  {status}: {name} {size_str}")
    
    print()
    print("-" * 60)
    print(f"  Total: {success_count}/{total_count} installers built successfully")
    
    if success_count == total_count:
        print()
        print("  Output files are in: build-system/installers/dist/")
        print()
        print("  Ready for distribution!")
    
    print("=" * 60)
    print()
    
    return success_count == total_count


def main():
    print_header()
    
    if not check_requirements():
        print("Build aborted: Missing requirements")
        return 1
    
    if not create_icon_if_missing():
        print("Build aborted: Icon creation failed")
        return 1
    
    if not clean_build_dirs():
        print("Build aborted: Failed to clean directories")
        return 1
    
    results = build_installers()
    
    if print_summary(results):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
