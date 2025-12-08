#!/usr/bin/env python3
"""
Aegis OS Installer Build Script for Windows
Automates PyInstaller builds for freemium and licensed installers
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

VERSION = "2.0.0"
COMPANY = "Aegis OS"
COPYRIGHT = f"Copyright (c) {datetime.now().year} Aegis OS"

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / "resources"
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"

INSTALLERS = {
    "freemium": {
        "spec_file": "pyinstaller-freemium.spec",
        "source_file": "aegis-installer-freemium.py",
        "output_name": "AegisInstallerFreemium.exe",
        "description": "Aegis OS Freemium Installer"
    },
    "licensed": {
        "spec_file": "pyinstaller-licensed.spec",
        "source_file": "aegis-installer-licensed.py",
        "output_name": "AegisInstallerLicensed.exe",
        "description": "Aegis OS Licensed Installer"
    }
}


def print_header():
    print("=" * 60)
    print("  Aegis OS Installer Build System")
    print(f"  Version: {VERSION}")
    print("=" * 60)
    print()


def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"[CHECK] Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("[WARN]  Python 3.11+ recommended for best results")
        return False
    
    print("[OK]    Python version is compatible")
    return True


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"[OK]    PyInstaller version: {version}")
            return True
        else:
            print("[ERROR] PyInstaller not found")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to check PyInstaller: {e}")
        return False


def check_cryptography():
    """Check if cryptography library is installed"""
    try:
        import cryptography
        print(f"[OK]    Cryptography version: {cryptography.__version__}")
        return True
    except ImportError:
        print("[WARN]  Cryptography not installed (needed for licensed installer)")
        return False


def check_upx():
    """Check if UPX is available for compression"""
    try:
        result = subprocess.run(["upx", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK]    UPX compression available")
            return True
    except FileNotFoundError:
        pass
    
    print("[INFO]  UPX not found (optional, for smaller executables)")
    return False


def check_icon():
    """Check if icon file exists"""
    icon_path = RESOURCES_DIR / "aegis-icon.ico"
    if icon_path.exists():
        print(f"[OK]    Icon file found: {icon_path}")
        return True
    else:
        print(f"[WARN]  Icon file not found: {icon_path}")
        print("        Build will continue without custom icon")
        return False


def check_source_files():
    """Check if source Python files exist"""
    all_found = True
    for name, config in INSTALLERS.items():
        source_path = SCRIPT_DIR / config["source_file"]
        if source_path.exists():
            print(f"[OK]    Source found: {config['source_file']}")
        else:
            print(f"[ERROR] Source not found: {config['source_file']}")
            all_found = False
    return all_found


def check_spec_files():
    """Check if spec files exist"""
    all_found = True
    for name, config in INSTALLERS.items():
        spec_path = SCRIPT_DIR / config["spec_file"]
        if spec_path.exists():
            print(f"[OK]    Spec file found: {config['spec_file']}")
        else:
            print(f"[WARN]  Spec file not found: {config['spec_file']}")
            print(f"        Will use fallback spec: aegis-installer-{name}.spec")
    return all_found


def run_checks():
    """Run all pre-build checks"""
    print("Running pre-build checks...")
    print("-" * 40)
    
    checks = [
        ("Python", check_python()),
        ("PyInstaller", check_pyinstaller()),
        ("Cryptography", check_cryptography()),
        ("UPX", check_upx()),
        ("Icon", check_icon()),
        ("Source Files", check_source_files()),
        ("Spec Files", check_spec_files()),
    ]
    
    print("-" * 40)
    
    critical_passed = all([
        checks[0][1],  # Python
        checks[1][1],  # PyInstaller
        checks[5][1],  # Source Files
    ])
    
    if not critical_passed:
        print("[FAIL] Critical checks failed. Cannot proceed.")
        return False
    
    print("[OK]   All critical checks passed")
    return True


def clean_build():
    """Clean previous build artifacts"""
    print("\nCleaning previous builds...")
    
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"[OK]    Removed: {BUILD_DIR}")
    
    # Don't remove dist entirely, just the specific exe files
    for config in INSTALLERS.values():
        exe_path = DIST_DIR / config["output_name"]
        if exe_path.exists():
            exe_path.unlink()
            print(f"[OK]    Removed: {exe_path}")


def build_installer(name, config, use_upx=True):
    """Build a single installer"""
    print(f"\n{'=' * 40}")
    print(f"Building: {config['description']}")
    print(f"{'=' * 40}")
    
    # Determine which spec file to use
    spec_file = SCRIPT_DIR / config["spec_file"]
    if not spec_file.exists():
        # Fallback to old naming convention
        fallback_spec = SCRIPT_DIR / f"aegis-installer-{name}.spec"
        if fallback_spec.exists():
            spec_file = fallback_spec
            print(f"[INFO]  Using fallback spec: {fallback_spec.name}")
        else:
            print(f"[ERROR] No spec file found for {name}")
            return False
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]
    
    if not use_upx:
        cmd.append("--noupx")
    
    print(f"[CMD]   {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(SCRIPT_DIR),
            capture_output=False
        )
        
        if result.returncode == 0:
            output_path = DIST_DIR / config["output_name"]
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"\n[OK]    Built successfully: {output_path}")
                print(f"[INFO]  Size: {size_mb:.2f} MB")
                return True
            else:
                print(f"\n[ERROR] Build completed but output not found: {output_path}")
                return False
        else:
            print(f"\n[ERROR] Build failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Build exception: {e}")
        return False


def sign_executable(exe_path, cert_path, password):
    """Sign executable with code signing certificate"""
    print(f"\nSigning: {exe_path}")
    
    if not Path(exe_path).exists():
        print(f"[ERROR] Executable not found: {exe_path}")
        return False
    
    if not Path(cert_path).exists():
        print(f"[ERROR] Certificate not found: {cert_path}")
        return False
    
    cmd = [
        "signtool", "sign",
        "/f", cert_path,
        "/p", password,
        "/fd", "SHA256",
        "/tr", "http://timestamp.digicert.com",
        "/td", "SHA256",
        str(exe_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK]    Signed successfully")
            return True
        else:
            print(f"[ERROR] Signing failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("[ERROR] signtool not found. Install Windows SDK.")
        return False
    except Exception as e:
        print(f"[ERROR] Signing exception: {e}")
        return False


def print_summary(results):
    """Print build summary"""
    print("\n" + "=" * 60)
    print("  BUILD SUMMARY")
    print("=" * 60)
    
    for name, success in results.items():
        status = "[OK]   " if success else "[FAIL] "
        config = INSTALLERS[name]
        output = DIST_DIR / config["output_name"]
        print(f"{status} {config['description']}")
        if success and output.exists():
            size_mb = output.stat().st_size / (1024 * 1024)
            print(f"        {output} ({size_mb:.2f} MB)")
    
    print("=" * 60)
    
    if all(results.values()):
        print("\nAll builds completed successfully!")
        print(f"\nOutput directory: {DIST_DIR}")
    else:
        print("\nSome builds failed. Check the output above for details.")


def main():
    parser = argparse.ArgumentParser(
        description="Build Aegis OS Windows Installers"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Clean build artifacts before building"
    )
    parser.add_argument(
        "--freemium-only", action="store_true",
        help="Build only the freemium installer"
    )
    parser.add_argument(
        "--licensed-only", action="store_true",
        help="Build only the licensed installer"
    )
    parser.add_argument(
        "--no-upx", action="store_true",
        help="Disable UPX compression"
    )
    parser.add_argument(
        "--sign", action="store_true",
        help="Sign executables after building"
    )
    parser.add_argument(
        "--cert", type=str,
        help="Path to code signing certificate (.pfx)"
    )
    parser.add_argument(
        "--password", type=str,
        help="Certificate password"
    )
    
    args = parser.parse_args()
    
    print_header()
    
    # Change to script directory
    os.chdir(SCRIPT_DIR)
    
    # Run checks
    if not run_checks():
        sys.exit(1)
    
    # Clean if requested
    if args.clean:
        clean_build()
    
    # Ensure dist directory exists
    DIST_DIR.mkdir(exist_ok=True)
    
    # Determine which installers to build
    to_build = []
    if args.freemium_only:
        to_build = ["freemium"]
    elif args.licensed_only:
        to_build = ["licensed"]
    else:
        to_build = list(INSTALLERS.keys())
    
    # Build installers
    results = {}
    for name in to_build:
        config = INSTALLERS[name]
        success = build_installer(name, config, use_upx=not args.no_upx)
        results[name] = success
        
        # Sign if requested
        if success and args.sign and args.cert:
            exe_path = DIST_DIR / config["output_name"]
            sign_executable(exe_path, args.cert, args.password or "")
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
