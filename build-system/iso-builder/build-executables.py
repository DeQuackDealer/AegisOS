#!/usr/bin/env python3
"""
Aegis OS ISO Builder - Executable Build Script
Builds standalone executables for Windows distribution.

Usage:
    python build-executables.py [options]

Options:
    --freemium-only     Build only the freemium builder
    --licensed-only     Build only the licensed builder
    --sign CERT         Sign executables with code signing certificate
    --output DIR        Output directory for executables (default: dist/)
    --clean             Clean build artifacts before building
    --no-upx            Disable UPX compression
    --debug             Build with debug console enabled
"""

import os
import sys
import subprocess
import shutil
import argparse
import time
from pathlib import Path
from datetime import datetime


VERSION = "2.0.0"
BUILD_DIR = Path(__file__).parent
DIST_DIR = BUILD_DIR / "dist"
BUILD_ARTIFACTS = BUILD_DIR / "build"


def print_banner():
    """Print build script banner."""
    print("=" * 60)
    print("  Aegis OS ISO Builder - Executable Build System")
    print(f"  Version: {VERSION}")
    print(f"  Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()


def check_pyinstaller() -> bool:
    """Check if PyInstaller is installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ PyInstaller found: {version}")
            return True
    except Exception:
        pass
    
    print("✗ PyInstaller not found")
    print("  Install with: pip install pyinstaller")
    return False


def check_dependencies() -> bool:
    """Check all build dependencies."""
    print("Checking build dependencies...")
    print()
    
    all_ok = True
    
    if not check_pyinstaller():
        all_ok = False
    
    try:
        import tkinter
        print("✓ Tkinter available")
    except ImportError:
        print("✗ Tkinter not available")
        all_ok = False
    
    try:
        import cryptography
        print(f"✓ Cryptography available: {cryptography.__version__}")
    except ImportError:
        print("⚠ Cryptography not available (required for licensed builder)")
    
    spec_freemium = BUILD_DIR / "pyinstaller-freemium.spec"
    spec_licensed = BUILD_DIR / "pyinstaller-licensed.spec"
    
    if spec_freemium.exists():
        print(f"✓ Freemium spec file found")
    else:
        print(f"✗ Freemium spec file missing: {spec_freemium}")
        all_ok = False
    
    if spec_licensed.exists():
        print(f"✓ Licensed spec file found")
    else:
        print(f"✗ Licensed spec file missing: {spec_licensed}")
        all_ok = False
    
    core_module = BUILD_DIR / "aegis_builder_core.py"
    if core_module.exists():
        print(f"✓ Core module found")
    else:
        print(f"✗ Core module missing: {core_module}")
        all_ok = False
    
    print()
    return all_ok


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning build artifacts...")
    
    if BUILD_ARTIFACTS.exists():
        shutil.rmtree(BUILD_ARTIFACTS)
        print(f"  Removed: {BUILD_ARTIFACTS}")
    
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print(f"  Removed: {DIST_DIR}")
    
    print()


def build_executable(spec_file: Path, name: str, debug: bool = False, no_upx: bool = False) -> tuple[bool, Path | None]:
    """
    Build an executable from a spec file.
    
    Args:
        spec_file: Path to the .spec file
        name: Display name for logging
        debug: Enable debug console
        no_upx: Disable UPX compression
    
    Returns:
        (success, exe_path) tuple
    """
    print(f"Building {name}...")
    print(f"  Spec file: {spec_file}")
    
    start_time = time.time()
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--workpath", str(BUILD_ARTIFACTS / name.replace(" ", "_")),
        "--distpath", str(DIST_DIR),
    ]
    
    if no_upx:
        cmd.append("--noupx")
    
    if debug:
        pass
    
    cmd.append(str(spec_file))
    
    print(f"  Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(BUILD_DIR),
            capture_output=False,
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            exe_name = spec_file.stem.replace("pyinstaller-", "Aegis") 
            if "freemium" in spec_file.name.lower():
                exe_path = DIST_DIR / "AegisBuilderFreemium.exe"
            else:
                exe_path = DIST_DIR / "AegisBuilderLicensed.exe"
            
            if not exe_path.exists():
                for f in DIST_DIR.iterdir():
                    if f.suffix == ".exe":
                        exe_path = f
                        break
            
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print()
                print(f"✓ {name} built successfully!")
                print(f"  Output: {exe_path}")
                print(f"  Size: {size_mb:.2f} MB")
                print(f"  Time: {elapsed:.1f} seconds")
                print()
                return True, exe_path
            else:
                print(f"✗ Executable not found after build")
                return False, None
        else:
            print()
            print(f"✗ {name} build failed!")
            print(f"  Exit code: {result.returncode}")
            print()
            return False, None
            
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False, None


def sign_executable(exe_path: Path, cert_path: str) -> bool:
    """
    Sign an executable with a code signing certificate.
    
    Args:
        exe_path: Path to the executable
        cert_path: Path to the .pfx certificate file
    
    Returns:
        True if signing succeeded
    """
    print(f"Signing: {exe_path.name}")
    
    if sys.platform != "win32":
        print("  ⚠ Code signing only supported on Windows")
        return False
    
    try:
        sdk_paths = [
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
        ]
        
        signtool = None
        for path in sdk_paths:
            if Path(path).exists():
                signtool = path
                break
        
        if signtool is None:
            result = subprocess.run(["where", "signtool"], capture_output=True, text=True)
            if result.returncode == 0:
                signtool = result.stdout.strip().split("\n")[0]
        
        if signtool is None:
            print("  ✗ signtool.exe not found")
            print("    Install Windows SDK for code signing support")
            return False
        
        cmd = [
            signtool, "sign",
            "/f", cert_path,
            "/tr", "http://timestamp.digicert.com",
            "/td", "sha256",
            "/fd", "sha256",
            "/v",
            str(exe_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ Signed successfully")
            return True
        else:
            print(f"  ✗ Signing failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ✗ Signing error: {e}")
        return False


def verify_executable(exe_path: Path) -> bool:
    """Verify an executable was built correctly."""
    print(f"Verifying: {exe_path.name}")
    
    if not exe_path.exists():
        print("  ✗ File not found")
        return False
    
    size = exe_path.stat().st_size
    if size < 1024 * 1024:
        print(f"  ⚠ Executable seems too small: {size} bytes")
    
    with open(exe_path, "rb") as f:
        header = f.read(2)
        if header != b"MZ":
            print("  ✗ Not a valid Windows executable")
            return False
    
    print("  ✓ Valid Windows PE executable")
    return True


def print_summary(results: dict):
    """Print build summary."""
    print()
    print("=" * 60)
    print("  BUILD SUMMARY")
    print("=" * 60)
    print()
    
    for name, (success, path) in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {name}: {status}")
        if success and path:
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"    File: {path.name}")
            print(f"    Size: {size_mb:.2f} MB")
    
    print()
    
    total = len(results)
    passed = sum(1 for s, _ in results.values() if s)
    
    if passed == total:
        print(f"All {total} builds completed successfully!")
        print(f"Output directory: {DIST_DIR}")
    else:
        print(f"{passed}/{total} builds succeeded")
        print("Check the output above for error details.")
    
    print()


def main():
    """Main build entry point."""
    parser = argparse.ArgumentParser(
        description="Build Aegis OS ISO Builder executables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--freemium-only", action="store_true",
                        help="Build only the freemium builder")
    parser.add_argument("--licensed-only", action="store_true",
                        help="Build only the licensed builder")
    parser.add_argument("--sign", metavar="CERT",
                        help="Sign executables with code signing certificate (.pfx)")
    parser.add_argument("--output", metavar="DIR",
                        help="Output directory for executables")
    parser.add_argument("--clean", action="store_true",
                        help="Clean build artifacts before building")
    parser.add_argument("--no-upx", action="store_true",
                        help="Disable UPX compression")
    parser.add_argument("--debug", action="store_true",
                        help="Build with debug console enabled")
    
    args = parser.parse_args()
    
    print_banner()
    
    global DIST_DIR
    if args.output:
        DIST_DIR = Path(args.output)
    
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        sys.exit(1)
    
    if args.clean:
        clean_build()
    
    results = {}
    
    if not args.licensed_only:
        spec = BUILD_DIR / "pyinstaller-freemium.spec"
        success, path = build_executable(spec, "Freemium Builder", args.debug, args.no_upx)
        results["Freemium Builder"] = (success, path)
        
        if success and args.sign:
            sign_executable(path, args.sign)
        
        if success:
            verify_executable(path)
    
    if not args.freemium_only:
        spec = BUILD_DIR / "pyinstaller-licensed.spec"
        success, path = build_executable(spec, "Licensed Builder", args.debug, args.no_upx)
        results["Licensed Builder"] = (success, path)
        
        if success and args.sign:
            sign_executable(path, args.sign)
        
        if success:
            verify_executable(path)
    
    print_summary(results)
    
    all_success = all(s for s, _ in results.values())
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
