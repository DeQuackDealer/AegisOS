#!/usr/bin/env python3
"""
Aegis OS Installer Build Script for Windows
Automates PyInstaller builds for freemium and licensed installers

Features:
- Comprehensive prerequisite checking
- Builds both freemium and licensed installers
- Optional code signing with certificate
- Copies output to dist/ folder
- Detailed build summary with file sizes

Usage:
    python build-windows.py                 # Build all installers
    python build-windows.py --clean         # Clean and rebuild
    python build-windows.py --freemium-only # Build freemium only
    python build-windows.py --licensed-only # Build licensed only
    python build-windows.py --sign --cert path/to/cert.pfx --password mypass
"""

import os
import sys
import shutil
import subprocess
import argparse
import hashlib
from pathlib import Path
from datetime import datetime

VERSION = "2.0.0"
COMPANY = "Aegis OS"
COPYRIGHT = f"Copyright (c) {datetime.now().year} Aegis OS"

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / "resources"
KEYS_DIR = SCRIPT_DIR / "keys"
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"

INSTALLERS = {
    "freemium": {
        "spec_file": "pyinstaller-freemium.spec",
        "source_file": "aegis-installer-freemium.py",
        "output_name": "AegisInstallerFreemium.exe",
        "description": "Aegis OS Freemium Installer",
        "requires_crypto": False
    },
    "licensed": {
        "spec_file": "pyinstaller-licensed.spec",
        "source_file": "aegis-installer-licensed.py",
        "output_name": "AegisInstallerLicensed.exe",
        "description": "Aegis OS Licensed Installer",
        "requires_crypto": True
    }
}


def print_header():
    """Print build system header"""
    print()
    print("=" * 70)
    print("  Aegis OS Installer Build System")
    print(f"  Version: {VERSION}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()


def print_section(title):
    """Print section header"""
    print()
    print("-" * 50)
    print(f"  {title}")
    print("-" * 50)


def check_python():
    """Check Python version"""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"[CHECK] Python version: {version_str}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[ERROR] Python 3.8+ required")
        return False
    elif version.major == 3 and version.minor < 11:
        print("[WARN]  Python 3.11+ recommended for best results")
        return True
    
    print("[OK]    Python version is compatible")
    return True


def check_pyinstaller():
    """Check if PyInstaller is installed and get version"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"[OK]    PyInstaller version: {version}")
            return True
        else:
            print("[ERROR] PyInstaller not found")
            print("        Install with: pip install pyinstaller")
            return False
    except subprocess.TimeoutExpired:
        print("[ERROR] PyInstaller check timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to check PyInstaller: {e}")
        return False


def check_cryptography():
    """Check if cryptography library is installed"""
    try:
        import cryptography
        version = cryptography.__version__
        print(f"[OK]    Cryptography version: {version}")
        
        from cryptography.hazmat.primitives.asymmetric import rsa, padding
        from cryptography.hazmat.primitives import hashes, serialization
        print("[OK]    Cryptography RSA modules available")
        return True
    except ImportError as e:
        print(f"[WARN]  Cryptography not installed: {e}")
        print("        Licensed installer requires cryptography")
        print("        Install with: pip install cryptography")
        return False


def check_upx():
    """Check if UPX is available for compression"""
    try:
        result = subprocess.run(
            ["upx", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"[OK]    UPX available: {version_line}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("[INFO]  UPX not found (optional, for smaller executables)")
    return False


def check_signtool():
    """Check if Windows signtool is available"""
    try:
        result = subprocess.run(
            ["signtool", "/?"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("[OK]    Windows signtool available")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("[INFO]  signtool not found (optional, for code signing)")
    return False


def check_icon():
    """Check if icon file exists"""
    icon_path = RESOURCES_DIR / "aegis-icon.ico"
    if icon_path.exists():
        size = icon_path.stat().st_size
        print(f"[OK]    Icon file found: {icon_path.name} ({size:,} bytes)")
        return True
    else:
        print(f"[WARN]  Icon file not found: {icon_path}")
        print("        Build will continue without custom icon")
        return False


def check_version_info():
    """Check if version_info.txt exists"""
    version_path = SCRIPT_DIR / "version_info.txt"
    if version_path.exists():
        print(f"[OK]    Version info found: {version_path.name}")
        return True
    else:
        print(f"[WARN]  Version info not found: {version_path}")
        print("        Build will continue without embedded version info")
        return False


def check_manifest():
    """Check if manifest.json exists"""
    manifest_path = SCRIPT_DIR / "manifest.json"
    if manifest_path.exists():
        print(f"[OK]    Manifest found: {manifest_path.name}")
        return True
    else:
        print(f"[WARN]  Manifest not found: {manifest_path}")
        return False


def check_public_key():
    """Check if RSA public key exists"""
    key_path = KEYS_DIR / "aegis-public.pem"
    if key_path.exists():
        print(f"[OK]    RSA public key found: {key_path.name}")
        return True
    else:
        print(f"[WARN]  RSA public key not found: {key_path}")
        print("        Licensed installer requires this key")
        return False


def check_source_files():
    """Check if source Python files exist"""
    all_found = True
    for name, config in INSTALLERS.items():
        source_path = SCRIPT_DIR / config["source_file"]
        if source_path.exists():
            size = source_path.stat().st_size
            print(f"[OK]    Source found: {config['source_file']} ({size:,} bytes)")
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
            fallback_spec = SCRIPT_DIR / f"aegis-installer-{name}.spec"
            if fallback_spec.exists():
                print(f"[INFO]  Fallback spec found: {fallback_spec.name}")
            else:
                print(f"[ERROR] No spec file found for {name}")
                all_found = False
    return all_found


def run_checks():
    """Run all pre-build checks"""
    print_section("Pre-Build Checks")
    
    results = {}
    
    results['python'] = check_python()
    results['pyinstaller'] = check_pyinstaller()
    results['cryptography'] = check_cryptography()
    results['upx'] = check_upx()
    results['signtool'] = check_signtool()
    results['icon'] = check_icon()
    results['version_info'] = check_version_info()
    results['manifest'] = check_manifest()
    results['public_key'] = check_public_key()
    results['sources'] = check_source_files()
    results['specs'] = check_spec_files()
    
    print()
    
    critical_passed = all([
        results['python'],
        results['pyinstaller'],
        results['sources'],
    ])
    
    if not critical_passed:
        print("[FAIL] Critical checks failed. Cannot proceed.")
        return False, results
    
    print("[OK]   All critical checks passed")
    return True, results


def clean_build():
    """Clean previous build artifacts"""
    print_section("Cleaning Previous Builds")
    
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"[OK]    Removed build directory: {BUILD_DIR}")
    else:
        print(f"[INFO]  Build directory not found: {BUILD_DIR}")
    
    for config in INSTALLERS.values():
        exe_path = DIST_DIR / config["output_name"]
        if exe_path.exists():
            exe_path.unlink()
            print(f"[OK]    Removed: {config['output_name']}")


def calculate_sha256(file_path):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def build_installer(name, config, use_upx=True, check_results=None):
    """Build a single installer"""
    print_section(f"Building: {config['description']}")
    
    if config['requires_crypto'] and check_results and not check_results.get('cryptography'):
        print("[ERROR] This installer requires cryptography library")
        return False
    
    spec_file = SCRIPT_DIR / config["spec_file"]
    if not spec_file.exists():
        fallback_spec = SCRIPT_DIR / f"aegis-installer-{name}.spec"
        if fallback_spec.exists():
            spec_file = fallback_spec
            print(f"[INFO]  Using fallback spec: {fallback_spec.name}")
        else:
            print(f"[ERROR] No spec file found for {name}")
            return False
    
    print(f"[INFO]  Spec file: {spec_file.name}")
    print(f"[INFO]  Output: {config['output_name']}")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--workpath", str(BUILD_DIR / name),
        "--distpath", str(DIST_DIR),
        str(spec_file)
    ]
    
    if not use_upx:
        cmd.append("--noupx")
    
    print()
    print(f"[CMD]   {' '.join(cmd)}")
    print()
    print("-" * 50)
    
    try:
        start_time = datetime.now()
        
        result = subprocess.run(
            cmd,
            cwd=str(SCRIPT_DIR),
            timeout=600
        )
        
        end_time = datetime.now()
        build_time = (end_time - start_time).total_seconds()
        
        print("-" * 50)
        print()
        
        if result.returncode == 0:
            output_path = DIST_DIR / config["output_name"]
            if output_path.exists():
                size_bytes = output_path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                sha256 = calculate_sha256(output_path)
                
                print(f"[OK]    Build successful!")
                print(f"        Output: {output_path}")
                print(f"        Size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
                print(f"        SHA-256: {sha256[:16]}...{sha256[-16:]}")
                print(f"        Build time: {build_time:.1f} seconds")
                return True
            else:
                print(f"[ERROR] Build completed but output not found: {output_path}")
                return False
        else:
            print(f"[ERROR] Build failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Build timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"[ERROR] Build exception: {e}")
        return False


def sign_executable(exe_path, cert_path, password=None, timestamp_url=None):
    """Sign executable with code signing certificate"""
    print_section(f"Signing: {exe_path.name}")
    
    if not exe_path.exists():
        print(f"[ERROR] Executable not found: {exe_path}")
        return False
    
    cert_path = Path(cert_path)
    if not cert_path.exists():
        print(f"[ERROR] Certificate not found: {cert_path}")
        return False
    
    if timestamp_url is None:
        timestamp_url = "http://timestamp.digicert.com"
    
    cmd = [
        "signtool", "sign",
        "/f", str(cert_path),
        "/fd", "SHA256",
        "/tr", timestamp_url,
        "/td", "SHA256",
    ]
    
    if password:
        cmd.extend(["/p", password])
    
    cmd.append(str(exe_path))
    
    print(f"[CMD]   signtool sign /f {cert_path.name} /fd SHA256 ...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("[OK]    Signed successfully")
            
            verify_cmd = ["signtool", "verify", "/pa", str(exe_path)]
            verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
            if verify_result.returncode == 0:
                print("[OK]    Signature verified")
            
            return True
        else:
            print(f"[ERROR] Signing failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("[ERROR] signtool not found. Install Windows SDK.")
        return False
    except subprocess.TimeoutExpired:
        print("[ERROR] Signing timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Signing exception: {e}")
        return False


def copy_to_output(results):
    """Copy built executables to final output location if needed"""
    pass


def print_summary(results, check_results):
    """Print build summary with file sizes"""
    print()
    print("=" * 70)
    print("  BUILD SUMMARY")
    print("=" * 70)
    print()
    
    total_size = 0
    successful = 0
    failed = 0
    
    for name, success in results.items():
        config = INSTALLERS[name]
        status = "[OK]   " if success else "[FAIL] "
        print(f"{status} {config['description']}")
        
        if success:
            successful += 1
            output = DIST_DIR / config["output_name"]
            if output.exists():
                size_bytes = output.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                sha256 = calculate_sha256(output)
                total_size += size_bytes
                print(f"        File: {output.name}")
                print(f"        Size: {size_mb:.2f} MB")
                print(f"        SHA-256: {sha256}")
        else:
            failed += 1
            if config['requires_crypto'] and not check_results.get('cryptography'):
                print("        Skipped: cryptography library not available")
        print()
    
    print("-" * 70)
    print()
    print(f"  Total installers: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    if total_size > 0:
        print(f"  Total size: {total_size / (1024 * 1024):.2f} MB")
    print()
    print(f"  Output directory: {DIST_DIR}")
    print()
    print("=" * 70)
    
    if all(results.values()):
        print()
        print("All builds completed successfully!")
        print()
    else:
        print()
        print("Some builds failed. Check the output above for details.")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Build Aegis OS Windows Installers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build-windows.py                    # Build all installers
  python build-windows.py --clean            # Clean and rebuild
  python build-windows.py --freemium-only    # Build freemium only
  python build-windows.py --licensed-only    # Build licensed only
  python build-windows.py --no-upx           # Build without compression
  python build-windows.py --sign --cert cert.pfx --password mypass
        """
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
        help="Certificate password (or use AEGIS_SIGN_PASSWORD env var)"
    )
    parser.add_argument(
        "--timestamp-url", type=str,
        default="http://timestamp.digicert.com",
        help="Timestamp server URL for signing"
    )
    parser.add_argument(
        "--skip-checks", action="store_true",
        help="Skip pre-build checks (not recommended)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    print_header()
    
    os.chdir(SCRIPT_DIR)
    
    check_results = {}
    if not args.skip_checks:
        passed, check_results = run_checks()
        if not passed:
            sys.exit(1)
    else:
        print("[WARN] Skipping pre-build checks")
    
    if args.clean:
        clean_build()
    
    DIST_DIR.mkdir(exist_ok=True)
    BUILD_DIR.mkdir(exist_ok=True)
    
    to_build = []
    if args.freemium_only:
        to_build = ["freemium"]
    elif args.licensed_only:
        to_build = ["licensed"]
    else:
        to_build = list(INSTALLERS.keys())
    
    results = {}
    for name in to_build:
        config = INSTALLERS[name]
        success = build_installer(
            name, config,
            use_upx=not args.no_upx,
            check_results=check_results
        )
        results[name] = success
        
        if success and args.sign:
            if args.cert:
                password = args.password or os.environ.get('AEGIS_SIGN_PASSWORD', '')
                exe_path = DIST_DIR / config["output_name"]
                sign_executable(
                    exe_path, args.cert, password,
                    timestamp_url=args.timestamp_url
                )
            else:
                print("[WARN] --sign specified but no --cert provided")
    
    print_summary(results, check_results)
    
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
