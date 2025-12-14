#!/usr/bin/env python3
"""
Aegis OS Build System v1.0.0 - Arch Linux Based
Generates bootable ISO images for all Aegis OS editions using archiso

Based on SteamOS architecture - Arch Linux with custom packages and configuration.

Supports two modes:
- Simulation Mode: For development/testing (works on Replit)
- Real Build Mode: Full ISO build on Arch Linux systems with root access

Usage:
    python3 build-aegis.py --edition freemium [--simulate] [--verbose]
    python3 build-aegis.py --edition freemium --real-build
    python3 build-aegis.py --check-deps
    python3 build-aegis.py --list-editions
    python3 build-aegis.py --edition all --simulate
"""

import os
import sys
import json
import shutil
import hashlib
import argparse
import subprocess
import platform
import py_compile
import compileall
import glob as globlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple, Any

VERSION = "1.0.0"
KERNEL_VERSION = "6.12"
ARCH_RELEASE = "2024.12.01"
BUILD_TIMESTAMP = datetime.now(timezone.utc).isoformat()

BUILD_DIR = Path(__file__).parent
OUTPUT_DIR = BUILD_DIR / "output"
LOGS_DIR = BUILD_DIR / "logs"
WORK_DIR = BUILD_DIR / "work"
ARCHISO_DIR = BUILD_DIR / "archiso"
PACKAGES_DIR = ARCHISO_DIR / "packages"
PROFILES_DIR = ARCHISO_DIR / "profiles"
AIROOTFS_DIR = ARCHISO_DIR / "airootfs"
OVERLAYS_DIR = BUILD_DIR / "overlays"

ARCH_MIRROR = "https://geo.mirror.pkgbuild.com"

REQUIRED_TOOLS = {
    "pacstrap": {
        "package": "arch-install-scripts",
        "description": "Bootstrap Arch Linux system",
        "required": True
    },
    "mkarchiso": {
        "package": "archiso",
        "description": "Create Arch Linux ISOs",
        "required": True
    },
    "mksquashfs": {
        "package": "squashfs-tools",
        "description": "Create squashfs filesystem",
        "required": True
    },
    "xorriso": {
        "package": "libisoburn",
        "description": "Create bootable ISO images",
        "required": True
    },
    "mkinitcpio": {
        "package": "mkinitcpio",
        "description": "Create initial ramdisk",
        "required": True
    },
    "grub-mkimage": {
        "package": "grub",
        "description": "GRUB bootloader tools",
        "required": True
    },
    "rsync": {
        "package": "rsync",
        "description": "Fast file copy with permissions",
        "required": True
    },
    "gpg": {
        "package": "gnupg",
        "description": "GPG signing tool",
        "required": False
    }
}

EDITIONS = {
    "freemium": {
        "name": "Aegis OS Freemium",
        "version": VERSION,
        "codename": "freemium",
        "base": "arch",
        "kernel": f"linux",
        "desktop": "xfce4",
        "tier": "free",
        "price": "Free",
        "iso_size_gb": 3.5,
        "packages": ["base.txt", "xfce.txt", "freemium.txt"],
        "description": "Free edition with 30-day premium trial. Perfect for trying Aegis OS.",
        "features": [
            "XFCE Desktop (Windows 10 style)",
            "Firefox Browser",
            "LibreOffice Suite",
            "VLC Media Player",
            "Basic Security Tools",
            "30-day Premium Trial"
        ]
    },
    "basic": {
        "name": "Aegis OS Basic",
        "version": VERSION,
        "codename": "basic",
        "base": "arch",
        "kernel": "linux",
        "desktop": "xfce4",
        "tier": "pro",
        "price": "$69",
        "iso_size_gb": 5.0,
        "packages": ["base.txt", "xfce.txt", "basic.txt"],
        "description": "Professional edition with development tools and productivity apps.",
        "features": [
            "All Freemium Features",
            "VS Code & Development Tools",
            "Docker & Container Support",
            "Advanced Security Suite",
            "Cloud Sync & Backup",
            "24/7 Email Support"
        ]
    },
    "gamer": {
        "name": "Aegis OS Gamer",
        "version": VERSION,
        "codename": "gamer",
        "base": "arch",
        "kernel": "linux-zen",
        "desktop": "xfce4",
        "tier": "pro",
        "price": "$69",
        "iso_size_gb": 6.5,
        "packages": ["base.txt", "xfce.txt", "gamer.txt"],
        "description": "SteamOS-inspired gaming powerhouse with Proton and Wine.",
        "features": [
            "Steam & Lutris Pre-installed",
            "Proton-GE & Wine-GE Support",
            "MangoHUD & GameScope",
            "NVIDIA/AMD Driver Optimized",
            "Controller Support",
            "Game Performance Tuner"
        ]
    },
    "workplace": {
        "name": "Aegis OS Workplace",
        "version": VERSION,
        "codename": "workplace",
        "base": "arch",
        "kernel": "linux-lts",
        "desktop": "xfce4",
        "tier": "pro",
        "price": "$49",
        "iso_size_gb": 5.5,
        "packages": ["base.txt", "xfce.txt", "workplace.txt"],
        "description": "Enterprise productivity with Microsoft 365 compatibility.",
        "features": [
            "Microsoft Teams & Zoom",
            "Office 365 Compatibility",
            "VPN Client Support",
            "Remote Desktop",
            "Document Scanner & OCR",
            "Enterprise Security"
        ]
    },
    "aidev": {
        "name": "Aegis OS AI Developer",
        "version": VERSION,
        "codename": "aidev",
        "base": "arch",
        "kernel": "linux",
        "desktop": "xfce4",
        "tier": "pro",
        "price": "$89",
        "iso_size_gb": 8.0,
        "packages": ["base.txt", "xfce.txt", "aidev.txt"],
        "description": "Complete AI/ML development environment with CUDA support.",
        "features": [
            "CUDA & cuDNN Pre-configured",
            "JupyterLab & VS Code",
            "PyTorch & TensorFlow Ready",
            "Docker & Kubernetes",
            "Cloud CLI Tools",
            "GPU Monitoring"
        ]
    },
    "gamer-ai": {
        "name": "Aegis OS Gamer+AI",
        "version": VERSION,
        "codename": "gamer-ai",
        "base": "arch",
        "kernel": "linux-zen",
        "desktop": "xfce4",
        "tier": "pro",
        "price": "$129",
        "iso_size_gb": 10.0,
        "packages": ["base.txt", "xfce.txt", "gamer-ai.txt"],
        "description": "Ultimate hybrid: Gaming performance + AI development.",
        "features": [
            "All Gamer Features",
            "All AI Developer Features",
            "AI-Powered Upscaling",
            "Real-time Translation",
            "Smart Streaming",
            "Neural Network Gaming"
        ]
    },
    "server": {
        "name": "Aegis OS Server",
        "version": VERSION,
        "codename": "server",
        "base": "arch",
        "kernel": "linux-lts",
        "desktop": None,
        "tier": "enterprise",
        "price": "$129",
        "iso_size_gb": 4.0,
        "packages": ["base.txt", "server.txt"],
        "description": "Enterprise server with XDR security and container orchestration.",
        "features": [
            "Docker & Kubernetes",
            "XDR Security Suite",
            "Prometheus & Grafana",
            "Automated Backups",
            "High Availability",
            "Enterprise Support"
        ]
    }
}


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log(message: str, level: str = "info") -> None:
    """Print formatted log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "info": Colors.CYAN,
        "success": Colors.GREEN,
        "warning": Colors.WARNING,
        "error": Colors.FAIL,
        "header": Colors.HEADER + Colors.BOLD
    }
    color = colors.get(level, Colors.CYAN)
    prefix = {
        "info": "[*]",
        "success": "[+]",
        "warning": "[!]",
        "error": "[X]",
        "header": "[=]"
    }.get(level, "[*]")
    
    print(f"{color}{prefix} [{timestamp}] {message}{Colors.END}")


def run_command(cmd: List[str], check: bool = True, 
                capture_output: bool = False, 
                cwd: Optional[Path] = None,
                timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """Run shell command with optional output capture"""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True,
            cwd=cwd,
            timeout=timeout
        )
        return result
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {' '.join(cmd)}", "error")
        if e.stderr:
            log(f"Error: {e.stderr}", "error")
        raise
    except subprocess.TimeoutExpired:
        log(f"Command timed out: {' '.join(cmd)}", "error")
        raise


def check_root() -> bool:
    """Check if running as root"""
    return os.geteuid() == 0


def check_arch_linux() -> bool:
    """Check if running on Arch Linux"""
    if os.path.exists("/etc/arch-release"):
        return True
    try:
        result = run_command(["pacman", "--version"], capture_output=True, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_dependencies() -> Dict[str, bool]:
    """Check if required tools are installed"""
    results = {}
    for tool, info in REQUIRED_TOOLS.items():
        if "check_path" in info:
            results[tool] = os.path.exists(info["check_path"])
        else:
            try:
                result = run_command(["which", tool], capture_output=True, check=False)
                results[tool] = result.returncode == 0
            except Exception:
                results[tool] = False
    return results


def calculate_sha256(filepath: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha256.update(chunk)
    return sha256.hexdigest().upper()


def get_package_list(edition: str) -> List[str]:
    """Get combined package list for an edition"""
    edition_info = EDITIONS.get(edition)
    if not edition_info:
        return []
    
    packages = []
    for pkg_file in edition_info.get("packages", []):
        pkg_path = PACKAGES_DIR / pkg_file
        if pkg_path.exists():
            with open(pkg_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        packages.append(line)
    
    return list(set(packages))


class AegisBuilder:
    """Main build system class for Aegis OS"""
    
    def __init__(self, edition: str, simulate: bool = True, verbose: bool = False):
        self.edition = edition
        self.edition_info = EDITIONS.get(edition, {})
        self.simulate = simulate
        self.verbose = verbose
        self.work_dir = WORK_DIR / edition
        self.profile_dir = self.work_dir / "profile"
        self.output_file = OUTPUT_DIR / f"aegis-{edition}.iso"
        
    def prepare_directories(self) -> None:
        """Create necessary build directories"""
        log(f"Preparing directories for {self.edition}...")
        
        for directory in [OUTPUT_DIR, LOGS_DIR, self.work_dir, self.profile_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        log("Directories prepared", "success")
    
    def create_profile(self) -> None:
        """Create archiso profile for the edition"""
        log(f"Creating archiso profile for {self.edition}...")
        
        profile_airootfs = self.profile_dir / "airootfs"
        profile_airootfs.mkdir(parents=True, exist_ok=True)
        
        packages = get_package_list(self.edition)
        packages_file = self.profile_dir / "packages.x86_64"
        with open(packages_file, 'w') as f:
            for pkg in sorted(packages):
                f.write(f"{pkg}\n")
        
        log(f"Package list created with {len(packages)} packages", "success")
        
        shutil.copy(ARCHISO_DIR / "profiledef.sh", self.profile_dir / "profiledef.sh")
        shutil.copy(ARCHISO_DIR / "pacman.conf", self.profile_dir / "pacman.conf")
        
        if AIROOTFS_DIR.exists():
            shutil.copytree(AIROOTFS_DIR, profile_airootfs, dirs_exist_ok=True)
        
        self._create_branding()
        self._create_aegis_tools()
        
        log("Profile created", "success")
    
    def _create_branding(self) -> None:
        """Create Aegis OS branding files"""
        etc_dir = self.profile_dir / "airootfs" / "etc"
        etc_dir.mkdir(parents=True, exist_ok=True)
        
        os_release = etc_dir / "os-release"
        with open(os_release, 'w') as f:
            f.write(f'''NAME="Aegis OS"
PRETTY_NAME="Aegis OS {self.edition_info.get('name', self.edition)}"
ID=aegis
ID_LIKE=arch
VERSION="{VERSION}"
VERSION_ID="{VERSION}"
VERSION_CODENAME="{self.edition}"
BUILD_ID="{BUILD_TIMESTAMP[:10]}"
HOME_URL="https://aegis-os.com"
DOCUMENTATION_URL="https://docs.aegis-os.com"
SUPPORT_URL="https://support.aegis-os.com"
BUG_REPORT_URL="https://github.com/aegis-os/aegis/issues"
LOGO=aegis-logo
''')
        
        issue = etc_dir / "issue"
        with open(issue, 'w') as f:
            f.write(f'''
    ___              _         ____  ____
   /   | ___  ____ _(_)____   / __ \\/ __/
  / /| |/ _ \\/ __ `/ / ___/  / / / /\\ \\  
 / ___ /  __/ /_/ / (__  )  / /_/ /___/ /
/_/  |_\\___/\\__, /_/____/   \\____//____/ 
           /____/                        

Aegis OS {self.edition_info.get('name', self.edition)} - v{VERSION}
Based on Arch Linux - Rolling Release

''')
        
        motd = etc_dir / "motd"
        with open(motd, 'w') as f:
            f.write(f'''
Welcome to Aegis OS {self.edition_info.get('name', self.edition)}!

Edition: {self.edition_info.get('name', self.edition)}
Price: {self.edition_info.get('price', 'Free')}
Base: Arch Linux (Rolling Release)

For help, visit: https://docs.aegis-os.com
''')
    
    def _create_aegis_tools(self) -> None:
        """Create Aegis OS custom tools"""
        bin_dir = self.profile_dir / "airootfs" / "usr" / "local" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        
        aegis_info = bin_dir / "aegis-info"
        with open(aegis_info, 'w') as f:
            f.write(f'''#!/bin/bash
echo "Aegis OS {self.edition_info.get('name', self.edition)}"
echo "Version: {VERSION}"
echo "Edition: {self.edition}"
echo "Base: Arch Linux"
echo "Kernel: $(uname -r)"
echo "Build: {BUILD_TIMESTAMP[:10]}"
''')
        os.chmod(aegis_info, 0o755)
        
        aegis_update = bin_dir / "aegis-update"
        with open(aegis_update, 'w') as f:
            f.write('''#!/bin/bash
echo "Updating Aegis OS..."
sudo pacman -Syu --noconfirm
echo "Update complete!"
''')
        os.chmod(aegis_update, 0o755)
        
        aegis_gaming = bin_dir / "aegis-gaming-mode"
        with open(aegis_gaming, 'w') as f:
            f.write('''#!/bin/bash
# Aegis Gaming Mode - Optimize system for gaming
echo "Activating Gaming Mode..."

# Set CPU governor to performance
if command -v cpupower &> /dev/null; then
    sudo cpupower frequency-set -g performance
fi

# Enable GameMode
if command -v gamemoded &> /dev/null; then
    gamemoded -r &
    echo "GameMode daemon started"
fi

# Disable compositor if XFCE
if pgrep -x "xfwm4" > /dev/null; then
    xfconf-query -c xfwm4 -p /general/use_compositing -s false
    echo "Compositor disabled"
fi

echo "Gaming Mode active!"
echo "Run 'aegis-gaming-mode --off' to disable"
''')
        os.chmod(aegis_gaming, 0o755)
    
    def build_iso(self) -> Optional[Path]:
        """Build the ISO image"""
        if self.simulate:
            return self._simulate_build()
        else:
            return self._real_build()
    
    def _simulate_build(self) -> Path:
        """Simulate ISO build for testing"""
        log(f"SIMULATION: Building {self.edition} ISO...", "header")
        
        self.prepare_directories()
        self.create_profile()
        
        iso_content = f"""AEGIS OS ISO SIMULATION
Edition: {self.edition_info.get('name', self.edition)}
Version: {VERSION}
Base: Arch Linux
Build: {BUILD_TIMESTAMP}
Packages: {len(get_package_list(self.edition))}

This is a simulated ISO for development testing.
Real builds require Arch Linux with archiso installed.
"""
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w') as f:
            f.write(iso_content)
        
        checksum = calculate_sha256(self.output_file)
        
        manifest = {
            "edition": self.edition,
            "name": self.edition_info.get("name"),
            "version": VERSION,
            "base": "arch",
            "kernel": self.edition_info.get("kernel", "linux"),
            "build_date": BUILD_TIMESTAMP,
            "iso_file": self.output_file.name,
            "sha256": checksum,
            "size_bytes": self.output_file.stat().st_size,
            "simulated": True,
            "packages_count": len(get_package_list(self.edition))
        }
        
        manifest_file = OUTPUT_DIR / f"aegis-{self.edition}.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        log(f"Simulated ISO created: {self.output_file}", "success")
        log(f"SHA256: {checksum[:32]}...", "info")
        
        return self.output_file
    
    def _real_build(self) -> Optional[Path]:
        """Perform actual ISO build using archiso"""
        log(f"REAL BUILD: Building {self.edition} ISO...", "header")
        
        if not check_root():
            log("Real builds require root privileges", "error")
            log("Run with: sudo python3 build-aegis.py --edition {self.edition} --real-build", "info")
            return None
        
        if not check_arch_linux():
            log("Real builds require Arch Linux", "error")
            return None
        
        deps = check_dependencies()
        missing = [t for t, available in deps.items() if not available and REQUIRED_TOOLS[t]["required"]]
        if missing:
            log(f"Missing required tools: {', '.join(missing)}", "error")
            log("Install with: sudo pacman -S archiso arch-install-scripts", "info")
            return None
        
        self.prepare_directories()
        self.create_profile()
        
        log("Running mkarchiso...", "info")
        cmd = [
            "mkarchiso",
            "-v",
            "-w", str(self.work_dir / "archiso-work"),
            "-o", str(OUTPUT_DIR),
            str(self.profile_dir)
        ]
        
        try:
            run_command(cmd, timeout=3600)
        except Exception as e:
            log(f"mkarchiso failed: {e}", "error")
            return None
        
        iso_files = list(OUTPUT_DIR.glob("aegis-os-*.iso"))
        if iso_files:
            latest_iso = max(iso_files, key=lambda x: x.stat().st_mtime)
            final_name = OUTPUT_DIR / f"aegis-{self.edition}.iso"
            shutil.move(latest_iso, final_name)
            
            checksum = calculate_sha256(final_name)
            
            manifest = {
                "edition": self.edition,
                "name": self.edition_info.get("name"),
                "version": VERSION,
                "base": "arch",
                "kernel": self.edition_info.get("kernel", "linux"),
                "build_date": BUILD_TIMESTAMP,
                "iso_file": final_name.name,
                "sha256": checksum,
                "size_bytes": final_name.stat().st_size,
                "simulated": False,
                "packages_count": len(get_package_list(self.edition))
            }
            
            manifest_file = OUTPUT_DIR / f"aegis-{self.edition}.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            checksum_file = OUTPUT_DIR / f"aegis-{self.edition}.iso.sha256"
            with open(checksum_file, 'w') as f:
                f.write(f"{checksum}  aegis-{self.edition}.iso\n")
            
            log(f"ISO created: {final_name}", "success")
            log(f"SHA256: {checksum}", "success")
            return final_name
        
        log("No ISO file produced", "error")
        return None


def build_all_editions(simulate: bool = True, verbose: bool = False) -> Dict[str, bool]:
    """Build all editions"""
    results = {}
    
    for edition in EDITIONS:
        log(f"\n{'='*60}", "header")
        log(f"Building {EDITIONS[edition]['name']}", "header")
        log(f"{'='*60}", "header")
        
        try:
            builder = AegisBuilder(edition, simulate=simulate, verbose=verbose)
            result = builder.build_iso()
            results[edition] = result is not None
        except Exception as e:
            log(f"Build failed for {edition}: {e}", "error")
            results[edition] = False
    
    return results


def generate_master_manifest() -> None:
    """Generate master manifest with all editions"""
    manifest = {
        "project": "Aegis OS",
        "version": VERSION,
        "base": "Arch Linux",
        "build_date": BUILD_TIMESTAMP,
        "editions": {}
    }
    
    for edition, info in EDITIONS.items():
        iso_file = OUTPUT_DIR / f"aegis-{edition}.iso"
        edition_manifest = OUTPUT_DIR / f"aegis-{edition}.json"
        
        if edition_manifest.exists():
            with open(edition_manifest, 'r') as f:
                manifest["editions"][edition] = json.load(f)
        else:
            manifest["editions"][edition] = {
                "name": info["name"],
                "version": VERSION,
                "price": info.get("price", "Free"),
                "features": info.get("features", []),
                "description": info.get("description", ""),
                "iso_file": f"aegis-{edition}.iso",
                "sha256": "BUILD_REQUIRED",
                "built": False
            }
    
    master_file = OUTPUT_DIR / "manifest.json"
    with open(master_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    log(f"Master manifest generated: {master_file}", "success")


def main():
    parser = argparse.ArgumentParser(
        description="Aegis OS Build System v1.0.0 - Arch Linux Based",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 build-aegis.py --edition freemium --simulate
    python3 build-aegis.py --edition gamer --simulate --verbose
    python3 build-aegis.py --edition all --simulate
    sudo python3 build-aegis.py --edition freemium --real-build
    python3 build-aegis.py --check-deps
    python3 build-aegis.py --list-editions
        """
    )
    
    parser.add_argument("--edition", "-e", type=str,
                       help="Edition to build (or 'all')")
    parser.add_argument("--simulate", "-s", action="store_true", default=True,
                       help="Simulation mode (default)")
    parser.add_argument("--real-build", "-r", action="store_true",
                       help="Perform actual ISO build")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--check-deps", action="store_true",
                       help="Check build dependencies")
    parser.add_argument("--list-editions", action="store_true",
                       help="List available editions")
    parser.add_argument("--generate-manifest", action="store_true",
                       help="Generate master manifest")
    
    args = parser.parse_args()
    
    log("Aegis OS Build System v1.0.0 - Arch Linux Based", "header")
    log(f"Build timestamp: {BUILD_TIMESTAMP}", "info")
    
    if args.check_deps:
        log("\nChecking dependencies...", "info")
        deps = check_dependencies()
        for tool, available in deps.items():
            status = "success" if available else "error"
            symbol = "✓" if available else "✗"
            req = "(required)" if REQUIRED_TOOLS[tool]["required"] else "(optional)"
            log(f"  {symbol} {tool} - {REQUIRED_TOOLS[tool]['description']} {req}", status)
        
        is_arch = check_arch_linux()
        log(f"\n  {'✓' if is_arch else '✗'} Arch Linux detected", 
            "success" if is_arch else "warning")
        return
    
    if args.list_editions:
        log("\nAvailable editions:", "info")
        for edition, info in EDITIONS.items():
            log(f"\n  {Colors.BOLD}{edition}{Colors.END}", "header")
            log(f"    Name: {info['name']}", "info")
            log(f"    Price: {info.get('price', 'Free')}", "info")
            log(f"    Kernel: {info.get('kernel', 'linux')}", "info")
            log(f"    Desktop: {info.get('desktop', 'None')}", "info")
            log(f"    Description: {info.get('description', '')[:60]}...", "info")
        return
    
    if args.generate_manifest:
        generate_master_manifest()
        return
    
    if not args.edition:
        parser.print_help()
        return
    
    simulate = not args.real_build
    
    if args.edition.lower() == "all":
        results = build_all_editions(simulate=simulate, verbose=args.verbose)
        
        log("\n" + "="*60, "header")
        log("BUILD SUMMARY", "header")
        log("="*60, "header")
        
        for edition, success in results.items():
            status = "success" if success else "error"
            symbol = "✓" if success else "✗"
            log(f"  {symbol} {EDITIONS[edition]['name']}", status)
        
        generate_master_manifest()
    else:
        if args.edition not in EDITIONS:
            log(f"Unknown edition: {args.edition}", "error")
            log(f"Available: {', '.join(EDITIONS.keys())}", "info")
            return
        
        builder = AegisBuilder(args.edition, simulate=simulate, verbose=args.verbose)
        result = builder.build_iso()
        
        if result:
            generate_master_manifest()
            log("\nBuild completed successfully!", "success")
        else:
            log("\nBuild failed!", "error")
            sys.exit(1)


if __name__ == "__main__":
    main()
