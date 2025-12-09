#!/usr/bin/env python3
"""
Aegis OS Installer Build Script
Compiles both freemium and licensed installers to Windows .exe files

Requirements:
- Python 3.8+
- PyInstaller (auto-installed if missing)

Usage:
    Double-click this file or run: python build-all-installers.py

Output:
    dist/AegisInstallerFreemium.exe
    dist/AegisInstallerLicensed.exe
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime


INSTALLERS = [
    {
        "name": "Freemium Installer",
        "script": "aegis-installer-freemium.py",
        "spec": "aegis-installer-freemium.spec",
        "output": "AegisInstallerFreemium.exe",
        "description": "Free edition with 30-day premium trial"
    },
    {
        "name": "Licensed Installer", 
        "script": "aegis-installer-licensed.py",
        "spec": "aegis-installer-licensed.spec",
        "output": "AegisInstallerLicensed.exe",
        "description": "Paid editions with RSA license verification"
    }
]

DELAY_SHORT = 0.5
DELAY_MEDIUM = 1.0
DELAY_LONG = 1.5


def slow_print(text, delay=0.03):
    """Print text character by character for visual effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def print_step(text):
    """Print a step with a small delay"""
    print(text)
    time.sleep(DELAY_SHORT)


def print_header():
    print()
    print("=" * 64)
    slow_print("  AEGIS OS INSTALLER BUILD SYSTEM", delay=0.02)
    print("=" * 64)
    time.sleep(DELAY_SHORT)
    print(f"  Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Python:     {sys.version.split()[0]}")
    print(f"  Platform:   {sys.platform}")
    print("=" * 64)
    print()
    time.sleep(DELAY_MEDIUM)


def print_location_info():
    """Show where files will be created"""
    script_dir = Path(__file__).parent.resolve()
    dist_dir = script_dir / 'dist'
    
    print("-" * 64)
    print("  BUILD LOCATIONS")
    print("-" * 64)
    time.sleep(DELAY_SHORT)
    print()
    print(f"  Script location:")
    print(f"    {script_dir}")
    time.sleep(DELAY_SHORT)
    print()
    print(f"  Output folder (where .exe files will be saved):")
    print(f"    {dist_dir}")
    time.sleep(DELAY_SHORT)
    print()
    print(f"  Source files to compile:")
    for installer in INSTALLERS:
        src = script_dir / installer["script"]
        exists = "✓" if src.exists() else "✗"
        print(f"    {exists} {installer['script']}")
        print(f"        → {installer['output']}")
        time.sleep(DELAY_SHORT)
    print()
    print("-" * 64)
    print()
    time.sleep(DELAY_MEDIUM)


def install_pyinstaller():
    """Install PyInstaller using pip"""
    print()
    print("  → Downloading and installing PyInstaller...")
    print("    This may take a minute...")
    time.sleep(DELAY_SHORT)
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
            capture_output=True,
            text=True
        )
        time.sleep(DELAY_SHORT)
        
        if result.returncode == 0:
            print("  ✓ PyInstaller installed successfully!")
            time.sleep(DELAY_SHORT)
            return True
        else:
            print("  ✗ Failed to install PyInstaller")
            if result.stderr:
                for line in result.stderr.split('\n')[:3]:
                    if line.strip():
                        print(f"    {line}")
            return False
    except Exception as e:
        print(f"  ✗ Error installing PyInstaller: {e}")
        return False


def check_requirements():
    print("[STEP 1 of 5] Checking Requirements")
    print("-" * 64)
    time.sleep(DELAY_SHORT)
    
    print("  Checking for PyInstaller...")
    time.sleep(DELAY_MEDIUM)
    
    try:
        import PyInstaller
        print(f"  ✓ PyInstaller {PyInstaller.__version__} is installed")
        time.sleep(DELAY_SHORT)
    except ImportError:
        print("  ✗ PyInstaller not found on this system")
        time.sleep(DELAY_SHORT)
        
        if not install_pyinstaller():
            return False
        
        print("  Verifying installation...")
        time.sleep(DELAY_SHORT)
        
        try:
            import PyInstaller
            print(f"  ✓ PyInstaller {PyInstaller.__version__} ready to use")
        except ImportError:
            print("  ✗ PyInstaller still not available")
            return False
    
    time.sleep(DELAY_SHORT)
    print()
    print("  Checking source files...")
    time.sleep(DELAY_SHORT)
    
    script_dir = Path(__file__).parent
    
    for installer in INSTALLERS:
        script_path = script_dir / installer["script"]
        time.sleep(DELAY_SHORT)
        if not script_path.exists():
            print(f"  ✗ Missing: {installer['script']}")
            return False
        print(f"  ✓ Found: {installer['script']}")
    
    print()
    time.sleep(DELAY_SHORT)
    return True


def analyze_code():
    print("[STEP 2 of 5] Analyzing Source Code")
    print("-" * 64)
    time.sleep(DELAY_SHORT)
    
    script_dir = Path(__file__).parent
    
    for installer in INSTALLERS:
        script_path = script_dir / installer["script"]
        print()
        print(f"  Analyzing: {installer['script']}")
        time.sleep(DELAY_SHORT)
        
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.count('\n') + 1
            classes = content.count('class ')
            functions = content.count('def ')
            imports = content.count('import ')
        
        print(f"    → Lines of code:  {lines:,}")
        time.sleep(0.3)
        print(f"    → Classes:        {classes}")
        time.sleep(0.3)
        print(f"    → Functions:      {functions}")
        time.sleep(0.3)
        print(f"    → Imports:        {imports}")
        time.sleep(0.3)
        print(f"    → Description:    {installer['description']}")
        time.sleep(DELAY_SHORT)
    
    print()
    print("  ✓ Code analysis complete")
    print()
    time.sleep(DELAY_SHORT)
    return True


def create_icon_if_missing():
    print("[STEP 3 of 5] Checking Resources")
    print("-" * 64)
    time.sleep(DELAY_SHORT)
    
    print("  Looking for application icon...")
    time.sleep(DELAY_MEDIUM)
    
    icon_path = Path(__file__).parent.parent / "aegis-icon.ico"
    
    if icon_path.exists():
        print(f"  ✓ Icon found: aegis-icon.ico")
    else:
        print(f"  ! Icon not found, creating placeholder...")
        time.sleep(DELAY_SHORT)
        with open(icon_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x20\x00')
            f.write(b'\x68\x04\x00\x00\x16\x00\x00\x00')
            f.write(b'\x00' * 1128)
        print("  ✓ Placeholder icon created")
    
    time.sleep(DELAY_SHORT)
    print()
    return True


def clean_build_dirs():
    print("[STEP 4 of 5] Preparing Build Environment")
    print("-" * 64)
    time.sleep(DELAY_SHORT)
    
    script_dir = Path(__file__).parent
    
    print("  Cleaning previous build files...")
    time.sleep(DELAY_SHORT)
    
    for dirname in ['build', '__pycache__']:
        dirpath = script_dir / dirname
        if dirpath.exists():
            shutil.rmtree(dirpath)
            print(f"    → Removed: {dirname}/")
            time.sleep(0.3)
    
    dist_dir = script_dir / 'dist'
    dist_dir.mkdir(exist_ok=True)
    
    print()
    print("  ✓ Build environment ready")
    print(f"  ✓ Output folder created: dist/")
    print()
    time.sleep(DELAY_SHORT)
    return True


def build_installers():
    print("[STEP 5 of 5] Compiling Installers")
    print("-" * 64)
    print()
    time.sleep(DELAY_SHORT)
    
    script_dir = Path(__file__).parent
    results = []
    
    for i, installer in enumerate(INSTALLERS, 1):
        print(f"  [{i}/{len(INSTALLERS)}] Building: {installer['name']}")
        print(f"      Source: {installer['script']}")
        print(f"      Output: {installer['output']}")
        print()
        time.sleep(DELAY_SHORT)
        
        script_path = script_dir / installer["script"]
        
        print("      Building standalone executable...")
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', installer["output"].replace('.exe', ''),
            '--distpath', str(script_dir / 'dist'),
            '--workpath', str(script_dir / 'build'),
            '--noconfirm',
            '--clean',
        ]
        
        if 'licensed' in installer["script"].lower():
            cmd.extend([
                '--hidden-import', 'cryptography',
                '--hidden-import', 'cryptography.hazmat.primitives',
                '--hidden-import', 'cryptography.hazmat.primitives.hashes',
                '--hidden-import', 'cryptography.hazmat.primitives.serialization',
                '--hidden-import', 'cryptography.hazmat.primitives.asymmetric.padding',
                '--hidden-import', 'cryptography.hazmat.backends',
                '--collect-all', 'cryptography',
            ])
        
        cmd.append(str(script_path))
        
        time.sleep(DELAY_SHORT)
        print("      Compiling... (this may take 1-2 minutes)")
        print()
        
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
                print(f"      ✓ SUCCESS!")
                print(f"        File: {installer['output']}")
                print(f"        Size: {size_mb:.1f} MB")
                results.append((installer["name"], True, size_mb, installer["output"]))
            else:
                print(f"      ✗ FAILED")
                if result.stderr:
                    print("      Error details:")
                    for line in result.stderr.split('\n')[:5]:
                        if line.strip():
                            print(f"        {line}")
                results.append((installer["name"], False, 0, installer["output"]))
                
        except Exception as e:
            print(f"      ✗ Error: {str(e)}")
            results.append((installer["name"], False, 0, installer["output"]))
        
        print()
        time.sleep(DELAY_MEDIUM)
    
    return results


def print_summary(results):
    print()
    print("=" * 64)
    slow_print("  BUILD COMPLETE", delay=0.03)
    print("=" * 64)
    print()
    time.sleep(DELAY_SHORT)
    
    success_count = sum(1 for _, success, _, _ in results if success)
    total_count = len(results)
    
    print("  Results:")
    print()
    for name, success, size, filename in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        size_str = f"({size:.1f} MB)" if success else ""
        print(f"    {status}: {name} {size_str}")
        time.sleep(DELAY_SHORT)
    
    print()
    print("-" * 64)
    print(f"  Total: {success_count}/{total_count} installers built successfully")
    print("-" * 64)
    
    if success_count > 0:
        script_dir = Path(__file__).parent
        dist_dir = script_dir / 'dist'
        abs_path = dist_dir.resolve()
        
        print()
        time.sleep(DELAY_SHORT)
        print("=" * 64)
        slow_print("  YOUR .EXE FILES ARE HERE:", delay=0.02)
        print("=" * 64)
        print()
        print(f"  {abs_path}")
        print()
        time.sleep(DELAY_MEDIUM)
        
        print("  Files ready for distribution:")
        print()
        for _, success, size, filename in results:
            if success:
                full_path = dist_dir / filename
                print(f"    → {filename}")
                print(f"      {full_path}")
                print()
                time.sleep(DELAY_SHORT)
        
        print("-" * 64)
        print("  These .exe files can be:")
        print("    • Copied to USB drives")
        print("    • Uploaded to your website")
        print("    • Shared with customers")
        print("-" * 64)
    
    print()
    print("=" * 64)
    print()
    time.sleep(DELAY_SHORT)
    
    return success_count == total_count


def main():
    try:
        print_header()
        print_location_info()
        
        if not check_requirements():
            print()
            print("!" * 64)
            print("  BUILD ABORTED: Missing requirements")
            print("!" * 64)
            return 1
        
        if not analyze_code():
            print("  BUILD ABORTED: Code analysis failed")
            return 1
        
        if not create_icon_if_missing():
            print("  BUILD ABORTED: Resource check failed")
            return 1
        
        if not clean_build_dirs():
            print("  BUILD ABORTED: Could not prepare build environment")
            return 1
        
        results = build_installers()
        
        if print_summary(results):
            return 0
        else:
            return 1
    
    except KeyboardInterrupt:
        print()
        print("  Build cancelled by user.")
        return 1
    
    except Exception as e:
        print()
        print("=" * 64)
        print("  BUILD ERROR")
        print("=" * 64)
        print(f"  {type(e).__name__}: {e}")
        print("=" * 64)
        return 1


if __name__ == "__main__":
    exit_code = 0
    try:
        exit_code = main()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        exit_code = 1
    finally:
        print()
        print("=" * 64)
        print()
        input("  Press ENTER to close this window...")
    sys.exit(exit_code)
