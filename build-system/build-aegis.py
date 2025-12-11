#!/usr/bin/env python3
"""
Aegis OS Build System v2.0.0
Generates bootable ISO images for all Aegis OS editions

Supports two modes:
- Simulation Mode: For development/testing (works on Replit)
- Real Build Mode: Full ISO build on Linux systems with root access

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

VERSION = "2.0.0"
KERNEL_VERSION = "6.8.0-45-generic"
UBUNTU_CODENAME = "noble"
UBUNTU_VERSION = "24.04"
BUILD_TIMESTAMP = datetime.now(timezone.utc).isoformat()

BUILD_DIR = Path(__file__).parent
OUTPUT_DIR = BUILD_DIR / "output"
LOGS_DIR = BUILD_DIR / "logs"
WORK_DIR = BUILD_DIR / "work"
CONFIGS_DIR = BUILD_DIR / "configs"
MANIFEST_DIR = BUILD_DIR / "manifests"
OVERLAYS_DIR = BUILD_DIR / "overlays"

UBUNTU_MIRROR = "http://archive.ubuntu.com/ubuntu"

REQUIRED_TOOLS = {
    "debootstrap": {
        "package": "debootstrap",
        "description": "Bootstrap a Debian-based system",
        "required": True
    },
    "mksquashfs": {
        "package": "squashfs-tools",
        "description": "Create squashfs filesystem",
        "required": True
    },
    "xorriso": {
        "package": "xorriso",
        "description": "Create bootable ISO images",
        "required": True
    },
    "genisoimage": {
        "package": "genisoimage",
        "description": "Alternative ISO creation tool",
        "required": False
    },
    "isolinux": {
        "package": "isolinux",
        "description": "Boot loader for ISO images",
        "required": True,
        "check_path": "/usr/lib/ISOLINUX/isohdpfx.bin"
    },
    "syslinux": {
        "package": "syslinux",
        "description": "Lightweight boot loader",
        "required": False
    },
    "grub-mkimage": {
        "package": "grub-pc-bin",
        "description": "GRUB bootloader tools",
        "required": False
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
        "base": "ubuntu-minimal",
        "ubuntu_base": UBUNTU_CODENAME,
        "kernel": f"linux-image-{KERNEL_VERSION}",
        "desktop": "xfce4",
        "overlay_name": "freemium",
        "tier": "free",
        "packages": [
            f"linux-image-{KERNEL_VERSION}",
            "linux-headers-generic",
            "xfce4",
            "xfce4-terminal",
            "xfce4-screenshooter",
            "xfce4-taskmanager",
            "xfce4-power-manager",
            "xfce4-notifyd",
            "thunar",
            "thunar-archive-plugin",
            "thunar-volman",
            "firefox",
            "vim",
            "nano",
            "htop",
            "wget",
            "curl",
            "git",
            "network-manager",
            "network-manager-gnome",
            "pulseaudio",
            "pavucontrol",
            "file-roller",
            "evince",
            "gnome-calculator",
            "gnome-screenshot",
            "fonts-ubuntu",
            "fonts-liberation",
            "plymouth",
            "plymouth-theme-spinner",
            "casper",
            "lupin-casper",
            "grub-efi-amd64-signed",
            "shim-signed",
        ],
        "systemd_services": [
            "aegis-security-suite.service",
        ],
        "size_mb": 1500,
        "description": "Basic Linux with XFCE desktop - Free edition"
    },
    "basic": {
        "name": "Aegis OS Basic",
        "version": VERSION,
        "codename": "basic",
        "base": "ubuntu-desktop",
        "ubuntu_base": UBUNTU_CODENAME,
        "kernel": f"linux-image-{KERNEL_VERSION}",
        "desktop": "xfce4",
        "overlay_name": "basic",
        "tier": "basic",
        "packages": [
            f"linux-image-{KERNEL_VERSION}",
            "linux-headers-generic",
            "xfce4",
            "xfce4-goodies",
            "lightdm",
            "lightdm-gtk-greeter",
            "thunar",
            "thunar-archive-plugin",
            "thunar-media-tags-plugin",
            "build-essential",
            "git",
            "cmake",
            "gcc",
            "g++",
            "make",
            "autoconf",
            "automake",
            "python3",
            "python3-pip",
            "python3-venv",
            "python3-dev",
            "nodejs",
            "npm",
            "docker.io",
            "docker-compose",
            "libreoffice",
            "gimp",
            "inkscape",
            "vlc",
            "audacity",
            "gparted",
            "synaptic",
            "bleachbit",
            "firewalld",
            "fail2ban",
            "clamav",
            "clamav-daemon",
            "rkhunter",
            "lynis",
            "firefox",
            "chromium-browser",
            "thunderbird",
            "transmission-gtk",
            "network-manager",
            "network-manager-gnome",
            "pulseaudio",
            "pavucontrol",
            "fonts-ubuntu",
            "fonts-liberation",
            "fonts-noto",
            "casper",
            "lupin-casper",
            "grub-efi-amd64-signed",
            "shim-signed",
        ],
        "systemd_services": [
            "aegis-backup-suite.service",
            "aegis-security-suite.service",
        ],
        "extra_packages": 150,
        "size_mb": 3500,
        "description": "Professional productivity suite with development tools"
    },
    "workplace": {
        "name": "Aegis OS Workplace",
        "version": VERSION,
        "codename": "workplace",
        "base": "ubuntu-desktop",
        "ubuntu_base": UBUNTU_CODENAME,
        "kernel": f"linux-image-{KERNEL_VERSION}",
        "desktop": "xfce4",
        "overlay_name": "workplace",
        "tier": "professional",
        "packages": [
            f"linux-image-{KERNEL_VERSION}",
            "linux-headers-generic",
            "xfce4",
            "xfce4-goodies",
            "lightdm",
            "lightdm-gtk-greeter",
            "thunar",
            "thunar-archive-plugin",
            "libreoffice",
            "libreoffice-gnome",
            "libreoffice-gtk3",
            "libreoffice-pdfimport",
            "libreoffice-writer",
            "libreoffice-calc",
            "libreoffice-impress",
            "libreoffice-draw",
            "libreoffice-math",
            "libreoffice-base",
            "thunderbird",
            "thunderbird-gnome-support",
            "gimp",
            "gimp-data-extras",
            "inkscape",
            "scribus",
            "evince",
            "okular",
            "calibre",
            "firefox",
            "chromium-browser",
            "remmina",
            "remmina-plugin-rdp",
            "remmina-plugin-vnc",
            "network-manager",
            "network-manager-gnome",
            "network-manager-openvpn",
            "network-manager-openvpn-gnome",
            "cups",
            "cups-pdf",
            "system-config-printer",
            "hplip",
            "simple-scan",
            "gnome-calendar",
            "gnome-contacts",
            "evolution",
            "evolution-ews",
            "fonts-ubuntu",
            "fonts-liberation",
            "fonts-noto",
            "fonts-dejavu",
            "fonts-open-sans",
            "casper",
            "lupin-casper",
            "grub-efi-amd64-signed",
            "shim-signed",
        ],
        "systemd_services": [
            "aegis-enterprise-suite.service",
            "aegis-it-management.service",
        ],
        "size_mb": 3000,
        "description": "Professional productivity workstation for office environments"
    },
    "gamer": {
        "name": "Aegis OS Gamer",
        "version": VERSION,
        "codename": "gamer",
        "base": "ubuntu-desktop",
        "ubuntu_base": UBUNTU_CODENAME,
        "kernel": f"linux-image-{KERNEL_VERSION}",
        "desktop": "xfce4",
        "overlay_name": "gamer",
        "tier": "gamer",
        "packages": [
            f"linux-image-{KERNEL_VERSION}",
            "linux-headers-generic",
            "xfce4",
            "xfce4-goodies",
            "lightdm",
            "steam-installer",
            "lutris",
            "wine64",
            "wine32",
            "winetricks",
            "playonlinux",
            "gamemode",
            "obs-studio",
            "mesa-vulkan-drivers",
            "vulkan-tools",
            "libvulkan1",
            "nvidia-driver-550",
            "nvidia-settings",
            "nvidia-prime",
            "libnvidia-gl-550",
            "retroarch",
            "retroarch-assets",
            "libretro-core-info",
            "dolphin-emu",
            "pcsx2",
            "ppsspp",
            "desmume",
            "mgba-qt",
            "snes9x",
            "mupen64plus-qt",
            "mesa-utils",
            "vulkan-utils",
            "cpufrequtils",
            "lm-sensors",
            "psensor",
            "hardinfo",
            "neofetch",
            "htop",
            "iotop",
            "firefox",
            "chromium-browser",
            "network-manager",
            "pulseaudio",
            "pipewire",
            "pavucontrol",
            "fonts-ubuntu",
            "casper",
            "lupin-casper",
            "grub-efi-amd64-signed",
            "shim-signed",
        ],
        "systemd_services": [
            "aegis-gamer-performance.service",
        ],
        "gaming_optimized": True,
        "size_mb": 4500,
        "description": "Ultimate gaming performance with Steam, Lutris, and Wine/Proton"
    },
    "ai": {
        "name": "Aegis OS AI Developer",
        "version": VERSION,
        "codename": "ai-dev",
        "base": "ubuntu-desktop",
        "ubuntu_base": UBUNTU_CODENAME,
        "kernel": f"linux-image-{KERNEL_VERSION}",
        "desktop": "xfce4",
        "overlay_name": "aidev",
        "tier": "professional",
        "packages": [
            f"linux-image-{KERNEL_VERSION}",
            "linux-headers-generic",
            "xfce4",
            "xfce4-goodies",
            "lightdm",
            "build-essential",
            "git",
            "cmake",
            "gcc",
            "g++",
            "python3",
            "python3-pip",
            "python3-venv",
            "python3-dev",
            "python3-numpy",
            "python3-scipy",
            "python3-pandas",
            "python3-matplotlib",
            "python3-sklearn",
            "python3-opencv",
            "python3-h5py",
            "jupyter-notebook",
            "jupyter-core",
            "ipython3",
            "nvidia-cuda-toolkit",
            "nvidia-cuda-dev",
            "nvidia-driver-550",
            "nvidia-settings",
            "spyder",
            "postgresql",
            "postgresql-client",
            "redis-server",
            "redis-tools",
            "docker.io",
            "docker-compose",
            "nodejs",
            "npm",
            "firefox",
            "chromium-browser",
            "network-manager",
            "pulseaudio",
            "fonts-ubuntu",
            "casper",
            "lupin-casper",
            "grub-efi-amd64-signed",
            "shim-signed",
        ],
        "systemd_services": [
            "aegis-inference-engine.service",
            "aegis-ml-studio.service",
        ],
        "ml_frameworks": ["tensorflow", "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm", "huggingface-transformers"],
        "size_mb": 6000,
        "description": "Complete AI/ML development platform with CUDA support"
    },
    "gamer-ai": {
        "name": "Aegis OS Gamer+AI",
        "version": VERSION,
        "codename": "gamer-ai",
        "base": "ubuntu-desktop",
        "ubuntu_base": UBUNTU_CODENAME,
        "kernel": f"linux-image-{KERNEL_VERSION}",
        "desktop": "xfce4",
        "overlay_name": "gamer-ai",
        "tier": "ultimate",
        "packages": [
            f"linux-image-{KERNEL_VERSION}",
            "linux-headers-generic",
            "xfce4",
            "xfce4-goodies",
            "lightdm",
            "steam-installer",
            "lutris",
            "wine64",
            "wine32",
            "winetricks",
            "gamemode",
            "obs-studio",
            "mesa-vulkan-drivers",
            "vulkan-tools",
            "nvidia-driver-550",
            "nvidia-settings",
            "retroarch",
            "dolphin-emu",
            "pcsx2",
            "ppsspp",
            "build-essential",
            "git",
            "cmake",
            "python3",
            "python3-pip",
            "python3-venv",
            "python3-dev",
            "python3-numpy",
            "python3-scipy",
            "python3-pandas",
            "python3-matplotlib",
            "python3-sklearn",
            "python3-opencv",
            "jupyter-notebook",
            "nvidia-cuda-toolkit",
            "nvidia-cuda-dev",
            "spyder",
            "docker.io",
            "docker-compose",
            "firefox",
            "chromium-browser",
            "network-manager",
            "pulseaudio",
            "pipewire",
            "pavucontrol",
            "fonts-ubuntu",
            "casper",
            "lupin-casper",
            "grub-efi-amd64-signed",
            "shim-signed",
        ],
        "systemd_services": [
            "aegis-ai-gaming.service",
            "aegis-performance-ai.service",
        ],
        "gaming_optimized": True,
        "ml_frameworks": ["tensorflow", "pytorch", "keras", "scikit-learn"],
        "size_mb": 7000,
        "description": "Ultimate gaming and AI development combo - Stream, play, and develop"
    },
    "server": {
        "name": "Aegis OS Server",
        "version": VERSION,
        "codename": "server",
        "base": "ubuntu-server",
        "ubuntu_base": UBUNTU_CODENAME,
        "kernel": f"linux-image-{KERNEL_VERSION}",
        "desktop": None,
        "overlay_name": "server",
        "tier": "enterprise",
        "packages": [
            f"linux-image-{KERNEL_VERSION}",
            "linux-headers-generic",
            "openssh-server",
            "openssh-client",
            "ufw",
            "fail2ban",
            "nginx",
            "apache2",
            "postgresql",
            "postgresql-client",
            "postgresql-contrib",
            "mysql-server",
            "mysql-client",
            "redis-server",
            "redis-tools",
            "memcached",
            "docker.io",
            "docker-compose",
            "containerd",
            "prometheus",
            "prometheus-node-exporter",
            "logrotate",
            "rsyslog",
            "cron",
            "at",
            "certbot",
            "python3-certbot-nginx",
            "python3-certbot-apache",
            "aide",
            "auditd",
            "apparmor",
            "apparmor-utils",
            "clamav",
            "clamav-daemon",
            "rkhunter",
            "lynis",
            "curl",
            "wget",
            "htop",
            "iotop",
            "vim",
            "nano",
            "git",
            "rsync",
            "unzip",
            "zip",
            "tar",
            "casper",
            "lupin-casper",
            "grub-efi-amd64-signed",
            "shim-signed",
        ],
        "systemd_services": [
            "aegis-monitoring.service",
            "aegis-server-security.service",
        ],
        "enterprise_ready": True,
        "size_mb": 3000,
        "description": "Enterprise-grade server deployment with security hardening"
    }
}


def get_file_checksum(filepath: Path, algorithm: str = 'sha256') -> Optional[str]:
    """Calculate file checksum"""
    hash_func = hashlib.new(algorithm)
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except FileNotFoundError:
        return None


def is_replit_environment() -> bool:
    """Check if running on Replit platform"""
    return bool(os.environ.get('REPL_ID') or os.environ.get('REPLIT_DEPLOYMENT') or 
                os.environ.get('REPL_SLUG') or os.environ.get('REPLIT'))


def has_root_privileges() -> bool:
    """Check if running with root privileges or can use sudo"""
    if os.geteuid() == 0:
        return True
    try:
        result = subprocess.run(
            ['sudo', '-n', 'true'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_tool_available(tool_name: str, tool_info: Dict) -> bool:
    """Check if a specific tool is available"""
    if shutil.which(tool_name):
        return True
    if 'check_path' in tool_info and os.path.exists(tool_info['check_path']):
        return True
    return False


def check_build_dependencies(verbose: bool = False) -> Tuple[bool, List[str], List[str], List[str]]:
    """
    Check all build dependencies and return detailed status.
    Returns: (all_required_available, missing_required, missing_optional, available)
    """
    missing_required = []
    missing_optional = []
    available = []
    
    for tool_name, tool_info in REQUIRED_TOOLS.items():
        is_available = check_tool_available(tool_name, tool_info)
        
        if is_available:
            available.append(tool_name)
            if verbose:
                print(f"  ✓ {tool_name}: available")
        else:
            if tool_info['required']:
                missing_required.append(tool_info['package'])
                if verbose:
                    print(f"  ✗ {tool_name}: MISSING (required) - install: {tool_info['package']}")
            else:
                missing_optional.append(tool_info['package'])
                if verbose:
                    print(f"  ○ {tool_name}: missing (optional) - install: {tool_info['package']}")
    
    all_required_available = len(missing_required) == 0
    return all_required_available, missing_required, missing_optional, available


def check_build_environment(verbose: bool = False) -> Dict[str, Any]:
    """
    Comprehensive check of the build environment.
    Returns: dict with environment status
    """
    env_status = {
        'is_linux': platform.system() == 'Linux',
        'is_replit': is_replit_environment(),
        'has_root': has_root_privileges(),
        'all_deps_available': False,
        'missing_required_deps': [],
        'missing_optional_deps': [],
        'available_deps': [],
        'can_real_build': False,
        'simulation_reason': None
    }
    
    if verbose:
        print("\n" + "=" * 60)
        print("BUILD ENVIRONMENT CHECK")
        print("=" * 60)
        print(f"\nSystem: {platform.system()} ({platform.platform()})")
        print(f"Python: {platform.python_version()}")
        print(f"User: {os.environ.get('USER', 'unknown')} (UID: {os.getuid()})")
        print()
    
    if verbose:
        print("Environment Detection:")
        print(f"  Linux system: {'Yes' if env_status['is_linux'] else 'No'}")
        print(f"  Replit platform: {'Yes' if env_status['is_replit'] else 'No'}")
        print(f"  Root privileges: {'Yes' if env_status['has_root'] else 'No'}")
        print()
    
    if verbose:
        print("Build Dependencies:")
    
    deps = check_build_dependencies(verbose=verbose)
    env_status['all_deps_available'] = deps[0]
    env_status['missing_required_deps'] = deps[1]
    env_status['missing_optional_deps'] = deps[2]
    env_status['available_deps'] = deps[3]
    
    if env_status['is_replit']:
        env_status['simulation_reason'] = 'Running on Replit platform'
    elif not env_status['is_linux']:
        env_status['simulation_reason'] = f'Not running on Linux (detected: {platform.system()})'
    elif not env_status['has_root']:
        env_status['simulation_reason'] = 'No root privileges (run with sudo)'
    elif not env_status['all_deps_available']:
        env_status['simulation_reason'] = f"Missing dependencies: {', '.join(env_status['missing_required_deps'])}"
    else:
        env_status['can_real_build'] = True
    
    if verbose:
        print()
        if env_status['can_real_build']:
            print("✓ REAL BUILD AVAILABLE")
            print("  All requirements met for creating bootable ISOs")
        else:
            print("⚠ SIMULATION MODE RECOMMENDED")
            print(f"  Reason: {env_status['simulation_reason']}")
        
        if env_status['missing_required_deps']:
            print()
            print("To enable real builds, install missing dependencies:")
            print(f"  sudo apt install {' '.join(env_status['missing_required_deps'])}")
        
        print()
    
    return env_status


def should_simulate(force_simulate: bool = False, force_real: bool = False) -> Tuple[bool, str]:
    """
    Determine if build should run in simulation mode.
    """
    if force_simulate:
        return True, "Simulation explicitly requested"
    
    env = check_build_environment(verbose=False)
    
    if force_real:
        if env['is_replit']:
            return True, "Cannot do real build on Replit (no root access)"
        elif not env['is_linux']:
            return True, f"Cannot do real build on {platform.system()} (requires Linux)"
        elif not env['has_root']:
            print("\033[93mWarning: Real build requested but no root privileges.\033[0m")
            print("Run with: sudo python3 build-aegis.py --real-build --edition <edition>")
            return True, "No root privileges for real build"
        elif not env['all_deps_available']:
            print(f"\033[93mWarning: Real build requested but missing dependencies.\033[0m")
            print(f"Install: sudo apt install {' '.join(env['missing_required_deps'])}")
            return True, f"Missing dependencies: {', '.join(env['missing_required_deps'])}"
        else:
            return False, "Real build (all requirements met)"
    
    if env['can_real_build']:
        return False, "Auto-detected: Real build available"
    else:
        return True, env['simulation_reason']


class ProgressReporter:
    """Progress reporting for long operations"""
    
    def __init__(self, total_steps: int, description: str = ""):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, step: Optional[int] = None, message: str = ""):
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        percent = (self.current_step / self.total_steps) * 100
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        bar_width = 40
        filled = int(bar_width * self.current_step / self.total_steps)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        status = f"\r[{bar}] {percent:5.1f}% ({self.current_step}/{self.total_steps})"
        if message:
            status += f" - {message}"
        
        print(status, end='', flush=True)
        
        if self.current_step >= self.total_steps:
            print()
    
    def finish(self):
        self.update(self.total_steps, "Complete!")


class AegisBuilder:
    """Main build class for Aegis OS"""
    
    def __init__(self, edition: str, simulate: bool = False, force_real: bool = False, 
                 verbose: bool = False, gpg_key: Optional[str] = None):
        self.edition = edition
        self.config = EDITIONS[edition]
        self.verbose = verbose
        self.force_real = force_real
        self.gpg_key = gpg_key
        
        should_sim, sim_reason = should_simulate(force_simulate=simulate, force_real=force_real)
        self.simulate = should_sim
        self.simulation_reason = sim_reason
        
        self.work_dir = WORK_DIR / edition
        self.chroot_dir = self.work_dir / "chroot"
        self.iso_dir = self.work_dir / "iso"
        self.squashfs_dir = self.work_dir / "squashfs"
        self.iso_path = OUTPUT_DIR / f"aegis-{edition}-{VERSION}.iso"
        self.manifest = {}
        self.build_start_time = None
        self.mounted_points = []
        self.cleanup_handlers = []
        
        for d in [OUTPUT_DIR, LOGS_DIR, MANIFEST_DIR, self.work_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        self.log_file = LOGS_DIR / f"build-{edition}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        
    def log(self, message: str, level: str = "INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = ""
        if self.simulate:
            prefix = "[SIM] "
        log_msg = f"[{timestamp}] [{level}] {prefix}{message}"
        
        if level == "ERROR":
            print(f"\033[91m{log_msg}\033[0m")
        elif level == "WARN":
            print(f"\033[93m{log_msg}\033[0m")
        elif level == "SUCCESS":
            print(f"\033[92m{log_msg}\033[0m")
        elif level == "PROGRESS":
            print(f"\033[94m{log_msg}\033[0m")
        else:
            print(log_msg)
            
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")
    
    def run_command(self, cmd, shell: bool = False, check: bool = True, 
                    capture: bool = True, sudo: bool = False, 
                    timeout: Optional[int] = None) -> str:
        """Execute shell command with logging and error handling"""
        if sudo and os.geteuid() != 0:
            if isinstance(cmd, str):
                cmd = f"sudo {cmd}"
            else:
                cmd = ["sudo"] + cmd
        
        if self.verbose:
            self.log(f"Running: {cmd}")
        
        if self.simulate:
            self.log(f"[SIMULATED] Would run: {cmd}")
            return ""
            
        try:
            if isinstance(cmd, str) and not shell:
                cmd = cmd.split()
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=capture,
                text=True,
                check=check,
                timeout=timeout
            )
            if result.stdout and self.verbose:
                self.log(f"Output: {result.stdout[:500]}")
            return result.stdout if result.stdout else ""
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e.stderr}", "ERROR")
            raise
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {cmd}", "ERROR")
            raise
    
    def chroot_run(self, cmd: str, timeout: int = 600) -> str:
        """Run command in chroot environment"""
        if self.simulate:
            self.log(f"[SIMULATED CHROOT] {cmd}")
            return ""
        return self.run_command(
            f"chroot {self.chroot_dir} /bin/bash -c '{cmd}'", 
            shell=True,
            timeout=timeout
        )
    
    def mount_chroot_filesystems(self):
        """Mount required filesystems for chroot"""
        if self.simulate:
            self.log("[SIMULATED] Would mount chroot filesystems")
            return
        
        mounts = [
            ("proc", "proc", "-t proc"),
            ("sys", "sys", "-t sysfs"),
            ("dev", "/dev", "--bind"),
            ("dev/pts", "/dev/pts", "--bind"),
            ("run", "/run", "--bind"),
        ]
        
        for target, source, opts in mounts:
            mount_point = self.chroot_dir / target
            mount_point.mkdir(parents=True, exist_ok=True)
            try:
                self.run_command(f"mount {opts} {source} {mount_point}", shell=True)
                self.mounted_points.append(mount_point)
            except Exception as e:
                self.log(f"Warning: Failed to mount {target}: {e}", "WARN")
    
    def unmount_chroot_filesystems(self):
        """Unmount chroot filesystems safely"""
        if self.simulate:
            return
        
        for mount_point in reversed(self.mounted_points):
            try:
                self.run_command(f"umount -l {mount_point}", shell=True, check=False)
            except Exception:
                pass
        self.mounted_points = []
    
    def cleanup(self):
        """Cleanup resources on exit"""
        self.log("Cleaning up resources...")
        self.unmount_chroot_filesystems()
        
        for handler in self.cleanup_handlers:
            try:
                handler()
            except Exception as e:
                self.log(f"Cleanup handler failed: {e}", "WARN")
    
    def check_dependencies(self) -> bool:
        """Verify build dependencies are installed"""
        self.log("Checking build dependencies...")
        
        if self.simulate:
            self.log("Running in SIMULATION MODE - dependency check skipped")
            packages = [info['package'] for info in REQUIRED_TOOLS.values() if info['required']]
            self.log(f"Full build requires: sudo apt install {' '.join(packages)}")
            return True
        
        all_ok, missing_req, missing_opt, available = check_build_dependencies(verbose=self.verbose)
        
        if missing_req:
            self.log(f"Missing required tools: {', '.join(missing_req)}", "ERROR")
            self.log(f"Install with: sudo apt install {' '.join(missing_req)}")
            return False
        
        if missing_opt:
            self.log(f"Note: Optional tools not installed: {', '.join(missing_opt)}", "WARN")
        
        self.log("All required dependencies satisfied", "SUCCESS")
        return True
    
    def create_base_system(self) -> Path:
        """Create base Ubuntu system using debootstrap"""
        self.log(f"Creating base system for {self.edition}...", "PROGRESS")
        
        if self.chroot_dir.exists():
            self.log("Removing existing chroot directory...")
            if not self.simulate:
                shutil.rmtree(self.chroot_dir, ignore_errors=True)
        
        self.chroot_dir.mkdir(parents=True, exist_ok=True)
        
        if self.simulate:
            dirs = ["bin", "boot", "boot/grub", "dev", "etc", "etc/apt", 
                   "etc/default", "etc/skel/.config", "etc/aegis", "home", 
                   "lib", "lib64", "lib/modules", "media", "mnt", "opt", 
                   "proc", "root", "run", "sbin", "srv", "sys", "tmp", 
                   "usr", "usr/bin", "usr/lib", "usr/share", "usr/local/bin",
                   "usr/share/applications", "var", "var/lib", "var/log",
                   "var/lib/aegis", "var/cache/apt/archives",
                   "etc/systemd/system", "etc/xdg"]
            for d in dirs:
                (self.chroot_dir / d).mkdir(parents=True, exist_ok=True)
                
            self._create_simulated_files()
        else:
            self.log(f"Running debootstrap for {UBUNTU_CODENAME}...")
            self.log("This may take 10-30 minutes depending on network speed...", "PROGRESS")
            
            self.run_command(
                f"debootstrap --arch=amd64 --variant=minbase "
                f"--include=apt-transport-https,ca-certificates,gnupg,locales "
                f"{UBUNTU_CODENAME} {self.chroot_dir} {UBUNTU_MIRROR}",
                shell=True,
                timeout=3600
            )
            
            sources_list = f"""deb {UBUNTU_MIRROR} {UBUNTU_CODENAME} main restricted universe multiverse
deb {UBUNTU_MIRROR} {UBUNTU_CODENAME}-updates main restricted universe multiverse
deb {UBUNTU_MIRROR} {UBUNTU_CODENAME}-security main restricted universe multiverse
deb {UBUNTU_MIRROR} {UBUNTU_CODENAME}-backports main restricted universe multiverse
"""
            (self.chroot_dir / "etc/apt/sources.list").write_text(sources_list)
            
            self._create_real_system_files()
        
        self.log("Base system created", "SUCCESS")
        return self.chroot_dir
    
    def _create_simulated_files(self):
        """Create simulated system files for demo mode"""
        release_content = f"""{self.config['name']} {VERSION}
Edition: {self.edition.upper()}
Codename: {self.config['codename']}
Kernel: {KERNEL_VERSION}
Build Date: {BUILD_TIMESTAMP}
Build System: Aegis Build System v{VERSION}
Base: Ubuntu {UBUNTU_VERSION} ({UBUNTU_CODENAME})
Build Mode: SIMULATION
"""
        (self.chroot_dir / "etc/aegis-release").write_text(release_content)
        
        os_release = f"""NAME="{self.config['name']}"
VERSION="{VERSION}"
ID=aegis
ID_LIKE=ubuntu debian
PRETTY_NAME="{self.config['name']} {VERSION}"
VERSION_ID="{VERSION}"
HOME_URL="https://aegis-os.io"
SUPPORT_URL="https://aegis-os.io/support"
BUG_REPORT_URL="https://aegis-os.io/bugs"
AEGIS_EDITION="{self.edition}"
AEGIS_TIER="{self.config.get('tier', 'free')}"
"""
        (self.chroot_dir / "etc/os-release").write_text(os_release)
        
        (self.chroot_dir / "etc/hostname").write_text(
            self.config['name'].replace(" ", "-").lower() + "\n"
        )
        
        fstab = """# /etc/fstab: static file system information.
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
UUID=ROOTFS     /               ext4    errors=remount-ro 0       1
UUID=SWAP       none            swap    sw              0       0
"""
        (self.chroot_dir / "etc/fstab").write_text(fstab)
        
        (self.chroot_dir / f"lib/modules/{KERNEL_VERSION}").mkdir(parents=True, exist_ok=True)
        
        (self.chroot_dir / "boot/vmlinuz").write_bytes(b'\x00' * 1024)
        (self.chroot_dir / "boot/initrd.img").write_bytes(b'\x00' * 2048)
    
    def _create_real_system_files(self):
        """Create Aegis-specific system files for real build"""
        release_content = f"""{self.config['name']} {VERSION}
Edition: {self.edition.upper()}
Codename: {self.config['codename']}
Kernel: {KERNEL_VERSION}
Build Date: {BUILD_TIMESTAMP}
Build System: Aegis Build System v{VERSION}
Base: Ubuntu {UBUNTU_VERSION} ({UBUNTU_CODENAME})
Build Mode: PRODUCTION
"""
        (self.chroot_dir / "etc/aegis-release").write_text(release_content)
        
        os_release = f"""NAME="{self.config['name']}"
VERSION="{VERSION}"
ID=aegis
ID_LIKE=ubuntu debian
PRETTY_NAME="{self.config['name']} {VERSION}"
VERSION_ID="{VERSION}"
HOME_URL="https://aegis-os.io"
SUPPORT_URL="https://aegis-os.io/support"
BUG_REPORT_URL="https://aegis-os.io/bugs"
AEGIS_EDITION="{self.edition}"
AEGIS_TIER="{self.config.get('tier', 'free')}"
"""
        (self.chroot_dir / "etc/os-release").write_text(os_release)
        
        (self.chroot_dir / "etc/hostname").write_text(
            self.config['name'].replace(" ", "-").lower() + "\n"
        )
    
    def apply_overlays(self):
        """Apply common, pro (for paid editions), pro-productivity, and edition-specific overlays
        
        Overlay order for paid editions: common -> pro -> pro-productivity -> edition
        Overlay order for freemium: common -> freemium
        
        This ensures all paid editions get:
        - Pro baseline features (cross-device, creative suite) 
        - Pro productivity (office, video conferencing, DaVinci Resolve)
        - Edition-specific specializations
        """
        self.log("Applying overlays...", "PROGRESS")
        
        common_overlay = OVERLAYS_DIR / "common"
        pro_overlay = OVERLAYS_DIR / "pro"
        pro_productivity_overlay = OVERLAYS_DIR / "pro-productivity"
        edition_overlay = OVERLAYS_DIR / self.config.get('overlay_name', self.edition)
        
        overlays_applied = []
        is_paid_edition = self.config.get('tier', 'free') != 'free'
        
        if common_overlay.exists():
            self.log(f"Applying common overlay from {common_overlay}")
            self._apply_overlay(common_overlay)
            overlays_applied.append("common")
        else:
            self.log(f"Warning: Common overlay not found at {common_overlay}", "WARN")
        
        if is_paid_edition and pro_overlay.exists():
            self.log(f"Applying Pro baseline overlay from {pro_overlay}")
            self._apply_overlay(pro_overlay)
            overlays_applied.append("pro")
        elif is_paid_edition:
            self.log(f"Warning: Pro overlay not found at {pro_overlay}", "WARN")
        
        if is_paid_edition and pro_productivity_overlay.exists():
            self.log(f"Applying Pro productivity overlay from {pro_productivity_overlay}")
            self._apply_overlay(pro_productivity_overlay)
            overlays_applied.append("pro-productivity")
        
        if edition_overlay.exists():
            self.log(f"Applying edition overlay from {edition_overlay}")
            self._apply_overlay(edition_overlay)
            overlays_applied.append(self.config.get('overlay_name', self.edition))
        else:
            self.log(f"Warning: Edition overlay not found at {edition_overlay}", "WARN")
        
        self._make_scripts_executable()
        
        self.manifest['overlays'] = {
            'applied': overlays_applied,
            'common_path': str(common_overlay),
            'pro_path': str(pro_overlay) if is_paid_edition else None,
            'edition_path': str(edition_overlay),
            'is_paid_edition': is_paid_edition,
            'applied_at': datetime.now(timezone.utc).isoformat()
        }
        
        self.log(f"Overlays applied: {', '.join(overlays_applied)}", "SUCCESS")
    
    def _apply_overlay(self, overlay_path: Path):
        """Apply a single overlay directory to chroot"""
        if self.simulate:
            self.log(f"[SIMULATED] Would rsync {overlay_path}/ to {self.chroot_dir}/")
            for root, dirs, files in os.walk(overlay_path):
                for file in files:
                    src = Path(root) / file
                    rel_path = src.relative_to(overlay_path)
                    dst = self.chroot_dir / rel_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy2(src, dst)
                    except Exception as e:
                        self.log(f"Warning: Failed to copy {src}: {e}", "WARN")
            return
        
        if shutil.which('rsync'):
            self.run_command(
                f"rsync -avP --chmod=D755,F644 {overlay_path}/ {self.chroot_dir}/",
                shell=True
            )
        else:
            for root, dirs, files in os.walk(overlay_path):
                for file in files:
                    src = Path(root) / file
                    rel_path = src.relative_to(overlay_path)
                    dst = self.chroot_dir / rel_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    src_stat = src.stat()
                    os.chmod(dst, src_stat.st_mode)
    
    def _make_scripts_executable(self):
        """Make all scripts in usr/local/bin executable"""
        bin_dir = self.chroot_dir / "usr/local/bin"
        
        if not bin_dir.exists():
            return
        
        script_count = 0
        for script in bin_dir.iterdir():
            if script.is_file():
                if self.simulate:
                    self.log(f"[SIMULATED] chmod +x {script}")
                else:
                    os.chmod(script, 0o755)
                script_count += 1
        
        self.log(f"Made {script_count} scripts executable in usr/local/bin")
    
    def run_post_build_hooks(self):
        """Run post-build scripts and configurations"""
        self.log("Running post-build hooks...", "PROGRESS")
        
        self._enable_systemd_services()
        self._compile_python_bytecode()
        self._generate_tier_json()
        self._update_initramfs()
        self._configure_display_manager()
        
        self.log("Post-build hooks completed", "SUCCESS")
    
    def _enable_systemd_services(self):
        """Enable systemd services defined in overlays"""
        services = self.config.get('systemd_services', [])
        
        if not services:
            self.log("No systemd services to enable")
            return
        
        self.log(f"Enabling {len(services)} systemd services...")
        
        for service in services:
            service_path = self.chroot_dir / "etc/systemd/system" / service
            if service_path.exists() or self.simulate:
                if self.simulate:
                    self.log(f"[SIMULATED] systemctl enable {service}")
                else:
                    try:
                        self.mount_chroot_filesystems()
                        self.chroot_run(f"systemctl enable {service}")
                    except Exception as e:
                        self.log(f"Warning: Failed to enable {service}: {e}", "WARN")
                    finally:
                        self.unmount_chroot_filesystems()
            else:
                self.log(f"Warning: Service file not found: {service}", "WARN")
    
    def _compile_python_bytecode(self):
        """Compile Python tools to bytecode for faster startup"""
        self.log("Compiling Python tools to bytecode...")
        
        python_dirs = [
            self.chroot_dir / "usr/share/aegis",
            self.chroot_dir / "usr/local/lib/python3",
        ]
        
        compiled_count = 0
        for py_dir in python_dirs:
            if py_dir.exists():
                if self.simulate:
                    py_files = list(py_dir.rglob("*.py"))
                    self.log(f"[SIMULATED] Would compile {len(py_files)} Python files in {py_dir}")
                    compiled_count += len(py_files)
                else:
                    try:
                        compileall.compile_dir(str(py_dir), quiet=1, force=True)
                        py_files = list(py_dir.rglob("*.py"))
                        compiled_count += len(py_files)
                    except Exception as e:
                        self.log(f"Warning: Failed to compile Python in {py_dir}: {e}", "WARN")
        
        self.log(f"Compiled {compiled_count} Python files to bytecode")
    
    def _generate_tier_json(self):
        """Generate /etc/aegis/tier.json with edition info"""
        self.log("Generating tier.json...")
        
        aegis_dir = self.chroot_dir / "etc/aegis"
        aegis_dir.mkdir(parents=True, exist_ok=True)
        
        tier_info = {
            "edition": self.edition,
            "edition_name": self.config['name'],
            "tier": self.config.get('tier', 'free'),
            "version": VERSION,
            "codename": self.config['codename'],
            "kernel": KERNEL_VERSION,
            "build_date": BUILD_TIMESTAMP,
            "features": {
                "desktop": self.config.get('desktop'),
                "gaming_optimized": self.config.get('gaming_optimized', False),
                "enterprise_ready": self.config.get('enterprise_ready', False),
                "ml_frameworks": self.config.get('ml_frameworks', []),
            },
            "services": self.config.get('systemd_services', []),
            "license_required": self.config.get('tier', 'free') != 'free',
            "support_url": "https://aegis-os.io/support",
            "documentation_url": "https://aegis-os.io/docs"
        }
        
        tier_json_path = aegis_dir / "tier.json"
        with open(tier_json_path, 'w') as f:
            json.dump(tier_info, f, indent=2)
        
        self.log(f"Generated tier.json: {tier_json_path}")
    
    def _update_initramfs(self):
        """Update initramfs after overlay application"""
        self.log("Updating initramfs...")
        
        if self.simulate:
            self.log("[SIMULATED] Would run update-initramfs -u")
            return
        
        try:
            self.mount_chroot_filesystems()
            self.chroot_run("update-initramfs -u -k all", timeout=600)
        except Exception as e:
            self.log(f"Warning: Failed to update initramfs: {e}", "WARN")
        finally:
            self.unmount_chroot_filesystems()
    
    def _configure_display_manager(self):
        """Configure display manager for desktop editions"""
        if not self.config.get('desktop'):
            return
        
        self.log("Configuring display manager...")
        
        lightdm_conf = """[Seat:*]
autologin-user=aegis
autologin-user-timeout=0
user-session=xfce
greeter-session=lightdm-gtk-greeter
"""
        
        lightdm_dir = self.chroot_dir / "etc/lightdm/lightdm.conf.d"
        lightdm_dir.mkdir(parents=True, exist_ok=True)
        (lightdm_dir / "50-aegis.conf").write_text(lightdm_conf)
        
        self.log("Display manager configured")
    
    def install_packages(self, chroot_dir: Path):
        """Install edition-specific packages plus Pro baseline packages for paid editions"""
        self.log(f"Installing packages for {self.edition}...", "PROGRESS")
        
        packages = list(self.config['packages'])
        is_paid_edition = self.config.get('tier', 'free') != 'free'
        pro_packages = []
        
        if is_paid_edition:
            package_lists = [
                ("pro", OVERLAYS_DIR / "pro" / "etc" / "aegis" / "pro-packages.list"),
                ("pro-productivity", OVERLAYS_DIR / "pro-productivity" / "etc" / "aegis" / "productivity-packages.list"),
            ]
            
            if self.edition == "workplace":
                package_lists.append(("workplace", OVERLAYS_DIR / "workplace" / "etc" / "aegis" / "workplace-packages.list"))
            elif self.edition in ["gamer", "gamer_ai"]:
                package_lists.append(("gamer", OVERLAYS_DIR / "gamer" / "etc" / "aegis" / "gamer-packages.list"))
            elif self.edition == "basic":
                package_lists.append(("basic", OVERLAYS_DIR / "basic" / "etc" / "aegis" / "basic-packages.list"))
            
            for list_name, pkg_file in package_lists:
                if pkg_file.exists():
                    self.log(f"Loading {list_name} packages from {pkg_file}")
                    count = 0
                    with open(pkg_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                pro_packages.append(line)
                                count += 1
                    self.log(f"Added {count} {list_name} packages")
            
            packages = list(set(packages + pro_packages))
        
        pkg_list = chroot_dir / "var/lib/aegis/packages.list"
        pkg_list.parent.mkdir(parents=True, exist_ok=True)
        
        with open(pkg_list, 'w') as f:
            for pkg in sorted(packages):
                f.write(f"{pkg}\n")
        
        self.manifest['packages'] = {
            'count': len(packages),
            'edition_packages': len(self.config['packages']),
            'pro_packages': len(pro_packages) if is_paid_edition else 0,
            'list': sorted(packages),
            'installed_at': datetime.now(timezone.utc).isoformat()
        }
        
        if self.simulate:
            self.log(f"[SIMULATED] Would install {len(packages)} packages:")
            for pkg in packages[:10]:
                self.log(f"  - {pkg}")
            if len(packages) > 10:
                self.log(f"  ... and {len(packages) - 10} more")
        else:
            self.mount_chroot_filesystems()
            
            try:
                self.log("Updating package lists...")
                self.chroot_run("apt-get update", timeout=300)
                
                self.log("Upgrading base system...")
                self.chroot_run("DEBIAN_FRONTEND=noninteractive apt-get upgrade -y", timeout=600)
                
                self.log(f"Installing {len(packages)} packages...")
                self.log("This may take 30-60 minutes depending on edition size...", "PROGRESS")
                
                progress = ProgressReporter(len(packages), "Installing packages")
                batch_size = 20
                
                for i in range(0, len(packages), batch_size):
                    batch = packages[i:i+batch_size]
                    pkg_string = " ".join(batch)
                    
                    try:
                        self.chroot_run(
                            f"DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends {pkg_string}",
                            timeout=1800
                        )
                        progress.update(min(i + batch_size, len(packages)), 
                                       f"Batch {i//batch_size + 1} complete")
                    except Exception as e:
                        self.log(f"Warning: Some packages in batch failed: {e}", "WARN")
                        for pkg in batch:
                            try:
                                self.chroot_run(
                                    f"DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends {pkg}",
                                    timeout=300
                                )
                            except Exception:
                                self.log(f"Warning: Failed to install {pkg}", "WARN")
                
                progress.finish()
                
                self.log("Cleaning up package cache...")
                self.chroot_run("apt-get clean")
                self.chroot_run("rm -rf /var/lib/apt/lists/*")
                
            finally:
                self.unmount_chroot_filesystems()
        
        self.log(f"Package installation complete ({len(packages)} packages)", "SUCCESS")
    
    def configure_system(self, chroot_dir: Path):
        """Apply system configurations"""
        self.log("Configuring system...", "PROGRESS")
        
        hostname = self.config['name'].replace(" ", "-").lower()
        issue = f"\\n \\l\\n{self.config['name']} {VERSION}\\n"
        motd = f"""
================================================================================
                    Welcome to {self.config['name']}!
================================================================================

{self.config['description']}

Version:     {VERSION}
Kernel:      {KERNEL_VERSION}
Build Date:  {BUILD_TIMESTAMP}

Documentation: https://aegis-os.io/docs
Support:       https://aegis-os.io/support

================================================================================
"""
        
        (chroot_dir / "etc/hostname").write_text(hostname + "\n")
        (chroot_dir / "etc/issue").write_text(issue)
        (chroot_dir / "etc/motd").write_text(motd)
        
        if self.config.get('desktop'):
            desktop_config = chroot_dir / "etc/skel/.config"
            desktop_config.mkdir(parents=True, exist_ok=True)
            
            autostart = desktop_config / "autostart"
            autostart.mkdir(parents=True, exist_ok=True)
            
            welcome_desktop = """[Desktop Entry]
Type=Application
Name=Welcome to Aegis OS
Exec=aegis-welcome
Icon=aegis-logo
Terminal=false
Categories=System;
"""
            (autostart / "aegis-welcome.desktop").write_text(welcome_desktop)
            
            self.log(f"Configured {self.config['desktop']} desktop")
        
        if self.config.get('gaming_optimized'):
            sysctl_gaming = """# Aegis OS Gaming Optimizations
vm.swappiness=10
vm.vfs_cache_pressure=50
net.core.netdev_max_backlog=16384
kernel.sched_autogroup_enabled=0
kernel.sched_min_granularity_ns=1000000
kernel.sched_wakeup_granularity_ns=500000
vm.dirty_ratio=10
vm.dirty_background_ratio=5
"""
            (chroot_dir / "etc/sysctl.d/99-aegis-gaming.conf").parent.mkdir(
                parents=True, exist_ok=True
            )
            (chroot_dir / "etc/sysctl.d/99-aegis-gaming.conf").write_text(sysctl_gaming)
            self.log("Applied gaming optimizations")
        
        if self.config.get('enterprise_ready'):
            security_conf = """# Aegis OS Server Security
net.ipv4.tcp_syncookies=1
net.ipv4.conf.all.rp_filter=1
net.ipv4.conf.default.rp_filter=1
kernel.randomize_va_space=2
net.ipv4.tcp_timestamps=0
net.ipv4.conf.all.accept_redirects=0
net.ipv4.conf.default.accept_redirects=0
net.ipv4.conf.all.send_redirects=0
net.ipv4.conf.default.send_redirects=0
net.ipv4.icmp_echo_ignore_broadcasts=1
"""
            (chroot_dir / "etc/sysctl.d/99-aegis-security.conf").parent.mkdir(
                parents=True, exist_ok=True
            )
            (chroot_dir / "etc/sysctl.d/99-aegis-security.conf").write_text(security_conf)
            self.log("Applied server security hardening")
        
        fstab = """# /etc/fstab: static file system information.
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
UUID=ROOTFS     /               ext4    errors=remount-ro 0       1
UUID=SWAP       none            swap    sw              0       0
"""
        (chroot_dir / "etc/fstab").write_text(fstab)
        
        self.log("System configured", "SUCCESS")
    
    def create_squashfs(self, chroot_dir: Path) -> Path:
        """Create compressed filesystem"""
        self.log("Creating squashfs filesystem...", "PROGRESS")
        
        self.squashfs_dir.mkdir(parents=True, exist_ok=True)
        squashfs_path = self.squashfs_dir / "filesystem.squashfs"
        
        if squashfs_path.exists():
            squashfs_path.unlink()
        
        if self.simulate:
            size_mb = self.config.get('size_mb', 2000)
            simulated_size = size_mb * 1024 * 100
            squashfs_path.write_bytes(b'\x00' * min(simulated_size, 1024 * 1024))
            
            manifest_file = self.squashfs_dir / "filesystem.manifest"
            manifest_content = "\n".join([
                f"{pkg}\t1.0-1" for pkg in self.config['packages']
            ])
            manifest_file.write_text(manifest_content)
            
            size_file = self.squashfs_dir / "filesystem.size"
            size_file.write_text(str(size_mb * 1024 * 1024))
            
            self.log(f"[SIMULATED] Created squashfs (~{size_mb} MB)")
        else:
            exclude_list = self.work_dir / "exclude.list"
            exclude_list.write_text("""proc/*
sys/*
dev/*
run/*
tmp/*
var/cache/apt/archives/*.deb
var/lib/apt/lists/*
boot/vmlinuz*
boot/initrd*
lost+found
""")
            
            self.log("Compressing filesystem with mksquashfs (this may take a while)...", "PROGRESS")
            
            self.run_command(
                f"mksquashfs {chroot_dir} {squashfs_path} "
                f"-comp xz -b 1M -Xdict-size 100% "
                f"-ef {exclude_list} -noappend -progress",
                shell=True,
                timeout=7200
            )
            
            manifest_file = self.squashfs_dir / "filesystem.manifest"
            try:
                self.mount_chroot_filesystems()
                manifest_output = self.chroot_run(
                    "dpkg-query -W --showformat='${Package}\\t${Version}\\n'"
                )
                manifest_file.write_text(manifest_output)
            finally:
                self.unmount_chroot_filesystems()
            
            actual_size = squashfs_path.stat().st_size
            size_file = self.squashfs_dir / "filesystem.size"
            size_file.write_text(str(actual_size))
            
            self.log(f"Squashfs created: {actual_size / (1024*1024):.1f} MB", "SUCCESS")
        
        actual_size_mb = squashfs_path.stat().st_size / (1024*1024) if squashfs_path.exists() else self.config.get('size_mb', 2000)
        
        self.manifest['squashfs'] = {
            'path': str(squashfs_path),
            'size_bytes': squashfs_path.stat().st_size if squashfs_path.exists() else 0,
            'size_mb': round(actual_size_mb, 2),
            'compression': 'xz',
            'checksum': get_file_checksum(squashfs_path) if squashfs_path.exists() else None
        }
        
        return squashfs_path
    
    def create_iso_structure(self):
        """Create ISO directory structure"""
        self.log("Creating ISO structure...")
        
        if self.iso_dir.exists():
            shutil.rmtree(self.iso_dir, ignore_errors=True)
        
        self.iso_dir.mkdir(parents=True, exist_ok=True)
        
        dirs = [
            "boot/grub",
            "boot/grub/x86_64-efi",
            "isolinux",
            "casper",
            "EFI/boot",
            "EFI/ubuntu",
            ".disk",
            "preseed",
            "pool/main"
        ]
        for d in dirs:
            (self.iso_dir / d).mkdir(parents=True, exist_ok=True)
        
        grub_cfg = f"""set default=0
set timeout=10
set gfxmode=auto
set gfxpayload=keep
insmod all_video
insmod gfxterm
insmod png

terminal_output gfxterm

menuentry "{self.config['name']}" {{
    linux /casper/vmlinuz boot=casper quiet splash ---
    initrd /casper/initrd
}}

menuentry "{self.config['name']} (Safe Mode)" {{
    linux /casper/vmlinuz boot=casper nomodeset ---
    initrd /casper/initrd
}}

menuentry "{self.config['name']} (Recovery)" {{
    linux /casper/vmlinuz boot=casper single ---
    initrd /casper/initrd
}}

menuentry "Check disc for defects" {{
    linux /casper/vmlinuz boot=casper integrity-check ---
    initrd /casper/initrd
}}

menuentry "Memory test" {{
    linux16 /boot/memtest86+.bin
}}

menuentry "Boot from first hard disk" {{
    set root=(hd0)
    chainloader +1
}}
"""
        (self.iso_dir / "boot/grub/grub.cfg").write_text(grub_cfg)
        
        grub_efi_cfg = grub_cfg
        (self.iso_dir / "EFI/boot/grub.cfg").write_text(grub_efi_cfg)
        
        isolinux_cfg = f"""DEFAULT vesamenu.c32
TIMEOUT 100
PROMPT 0

MENU TITLE {self.config['name']} {VERSION}
MENU BACKGROUND splash.png
MENU COLOR border 0 #00000000 #00000000 none
MENU COLOR title 1 #ffffffff #00000000 none
MENU COLOR sel 7 #ffffffff #76a1d0ff all
MENU COLOR hotsel 7 #ffffffff #76a1d0ff all
MENU COLOR tabmsg 0 #ffffffff #00000000 none
MENU RESOLUTION 800 600

LABEL live
  MENU LABEL ^Start {self.config['name']}
  MENU DEFAULT
  KERNEL /casper/vmlinuz
  APPEND initrd=/casper/initrd boot=casper quiet splash ---

LABEL live-safe
  MENU LABEL Start {self.config['name']} (^Safe Graphics)
  KERNEL /casper/vmlinuz
  APPEND initrd=/casper/initrd boot=casper nomodeset ---

LABEL live-recovery
  MENU LABEL Start {self.config['name']} (^Recovery Mode)
  KERNEL /casper/vmlinuz
  APPEND initrd=/casper/initrd boot=casper single ---

LABEL check
  MENU LABEL ^Check disc for defects
  KERNEL /casper/vmlinuz
  APPEND initrd=/casper/initrd boot=casper integrity-check ---

LABEL memtest
  MENU LABEL ^Memory Test
  KERNEL /boot/memtest86+.bin

LABEL hd
  MENU LABEL ^Boot from first hard disk
  LOCALBOOT 0x80
"""
        (self.iso_dir / "isolinux/isolinux.cfg").write_text(isolinux_cfg)
        
        disk_info = f"{self.config['name']} {VERSION} \"{self.config['codename']}\" - Release amd64"
        (self.iso_dir / ".disk/info").write_text(disk_info)
        (self.iso_dir / ".disk/base_installable").touch()
        (self.iso_dir / ".disk/cd_type").write_text("full_cd/single")
        (self.iso_dir / ".disk/release_notes_url").write_text("https://aegis-os.io/release-notes\n")
        
        readme = f"""
{self.config['name']} {VERSION}
{'=' * len(self.config['name'] + ' ' + VERSION)}

{self.config['description']}

System Requirements:
- CPU: 64-bit processor (x86_64)
- RAM: 2 GB minimum, 4 GB recommended
- Storage: {self.config.get('size_mb', 2000) * 2} MB minimum
- Graphics: Any GPU with OpenGL 3.0 support

Quick Start:
1. Boot from this ISO (USB or DVD)
2. Select "Start {self.config['name']}" from the menu
3. Use the desktop or run the installer

Boot Options:
- BIOS: Select the CD/USB drive from your BIOS boot menu
- UEFI: The ISO supports UEFI Secure Boot

Documentation: https://aegis-os.io/docs
Support: https://aegis-os.io/support

Build Information:
- Version: {VERSION}
- Kernel: {KERNEL_VERSION}
- Base: Ubuntu {UBUNTU_VERSION} ({UBUNTU_CODENAME})
- Build Date: {BUILD_TIMESTAMP}
- Build Mode: {'SIMULATION' if self.simulate else 'PRODUCTION'}
"""
        (self.iso_dir / "README.txt").write_text(readme)
        
        self.log("ISO structure created", "SUCCESS")
    
    def copy_boot_files(self, casper_dir: Path):
        """Copy kernel and initrd to casper directory"""
        self.log("Copying boot files...")
        
        if self.simulate:
            (casper_dir / "vmlinuz").write_bytes(b'\x00' * 1024)
            (casper_dir / "initrd").write_bytes(b'\x00' * 2048)
            return
        
        vmlinuz_src = None
        initrd_src = None
        
        for pattern in ["vmlinuz-*", "vmlinuz"]:
            matches = list((self.chroot_dir / "boot").glob(pattern))
            if matches:
                vmlinuz_src = max(matches, key=lambda x: x.stat().st_mtime)
                break
        
        for pattern in ["initrd.img-*", "initrd.img", "initrd-*", "initrd"]:
            matches = list((self.chroot_dir / "boot").glob(pattern))
            if matches:
                initrd_src = max(matches, key=lambda x: x.stat().st_mtime)
                break
        
        if vmlinuz_src and vmlinuz_src.exists():
            shutil.copy2(vmlinuz_src, casper_dir / "vmlinuz")
            self.log(f"Copied kernel: {vmlinuz_src.name}")
        else:
            self.log("Warning: No kernel found, creating placeholder", "WARN")
            (casper_dir / "vmlinuz").write_bytes(b'\x00' * 1024)
        
        if initrd_src and initrd_src.exists():
            shutil.copy2(initrd_src, casper_dir / "initrd")
            self.log(f"Copied initrd: {initrd_src.name}")
        else:
            self.log("Warning: No initrd found, creating placeholder", "WARN")
            (casper_dir / "initrd").write_bytes(b'\x00' * 2048)
    
    def copy_isolinux_files(self):
        """Copy isolinux boot files for BIOS boot"""
        self.log("Copying ISOLINUX files for BIOS boot...")
        
        if self.simulate:
            return
        
        isolinux_paths = [
            "/usr/lib/ISOLINUX",
            "/usr/lib/syslinux/modules/bios",
            "/usr/share/syslinux"
        ]
        
        required_files = [
            "isolinux.bin",
            "ldlinux.c32",
            "libcom32.c32",
            "libutil.c32",
            "vesamenu.c32",
            "libmenu.c32",
            "libgpl.c32",
            "hdt.c32",
        ]
        
        for filename in required_files:
            for path in isolinux_paths:
                src = Path(path) / filename
                if src.exists():
                    shutil.copy2(src, self.iso_dir / "isolinux" / filename)
                    break
    
    def setup_efi_boot(self):
        """Setup EFI boot files for UEFI systems"""
        self.log("Setting up EFI boot...")
        
        if self.simulate:
            (self.iso_dir / "EFI/boot/bootx64.efi").write_bytes(b'\x00' * 1024)
            (self.iso_dir / "EFI/boot/grubx64.efi").write_bytes(b'\x00' * 1024)
            return
        
        efi_sources = [
            ("/usr/lib/shim/shimx64.efi.signed", "EFI/boot/bootx64.efi"),
            ("/usr/lib/shim/shimx64.efi", "EFI/boot/bootx64.efi"),
            ("/usr/lib/grub/x86_64-efi-signed/grubx64.efi.signed", "EFI/boot/grubx64.efi"),
            ("/usr/lib/grub/x86_64-efi/grub.efi", "EFI/boot/grubx64.efi"),
        ]
        
        for src_path, dst_rel in efi_sources:
            src = Path(src_path)
            dst = self.iso_dir / dst_rel
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
                self.log(f"Copied EFI file: {src.name}")
        
        efi_grub_cfg = f"""search --set=root --file /.disk/info
set prefix=($root)/boot/grub
configfile $prefix/grub.cfg
"""
        (self.iso_dir / "EFI/boot/grub.cfg").write_text(efi_grub_cfg)
        
        if shutil.which('grub-mkimage'):
            grub_modules = [
                "part_gpt", "part_msdos", "fat", "iso9660", "ntfs",
                "hfs", "hfsplus", "ext2", "normal", "chain", "boot",
                "configfile", "linux", "linuxefi", "multiboot",
                "search", "search_fs_uuid", "search_fs_file", "search_label",
                "gfxterm", "gfxmenu", "video", "video_bochs", "video_cirrus",
                "all_video", "png", "gzio", "gettext", "font", "echo",
                "ls", "cat", "help", "loopback", "squash4", "test", "true"
            ]
            
            try:
                self.run_command(
                    f"grub-mkimage -O x86_64-efi -o {self.iso_dir}/EFI/boot/grubx64.efi "
                    f"-p /boot/grub {' '.join(grub_modules)}",
                    shell=True
                )
                self.log("Generated GRUB EFI image")
            except Exception as e:
                self.log(f"Warning: Could not generate GRUB EFI image: {e}", "WARN")
        
        self.log("EFI boot setup complete")
    
    def create_efi_image(self) -> Optional[Path]:
        """Create EFI boot image for xorriso"""
        self.log("Creating EFI boot image...")
        
        efi_img_path = self.iso_dir / "boot/grub/efi.img"
        
        if self.simulate:
            efi_img_path.write_bytes(b'\x00' * (4 * 1024 * 1024))
            return efi_img_path
        
        try:
            self.run_command(f"dd if=/dev/zero of={efi_img_path} bs=1M count=4", shell=True)
            self.run_command(f"mkfs.vfat {efi_img_path}", shell=True)
            
            mount_point = self.work_dir / "efi_mount"
            mount_point.mkdir(parents=True, exist_ok=True)
            
            self.run_command(f"mount -o loop {efi_img_path} {mount_point}", shell=True)
            
            (mount_point / "EFI/boot").mkdir(parents=True, exist_ok=True)
            
            for efi_file in (self.iso_dir / "EFI/boot").glob("*"):
                if efi_file.is_file():
                    shutil.copy2(efi_file, mount_point / "EFI/boot" / efi_file.name)
            
            self.run_command(f"umount {mount_point}", shell=True)
            
            self.log("EFI boot image created")
            return efi_img_path
            
        except Exception as e:
            self.log(f"Warning: Could not create EFI image: {e}", "WARN")
            return None
    
    def create_iso(self, squashfs_path: Path) -> Path:
        """Generate bootable hybrid ISO with BIOS and EFI support"""
        self.log("Creating ISO image...", "PROGRESS")
        
        self.create_iso_structure()
        
        casper_dir = self.iso_dir / "casper"
        if squashfs_path.exists():
            shutil.copy2(squashfs_path, casper_dir / "filesystem.squashfs")
        
        manifest_src = self.squashfs_dir / "filesystem.manifest"
        if manifest_src.exists():
            shutil.copy2(manifest_src, casper_dir / "filesystem.manifest")
        
        size_src = self.squashfs_dir / "filesystem.size"
        if size_src.exists():
            shutil.copy2(size_src, casper_dir / "filesystem.size")
        
        self.copy_boot_files(casper_dir)
        
        if self.simulate:
            self.iso_path.parent.mkdir(parents=True, exist_ok=True)
            size_bytes = self.config.get('size_mb', 2000) * 1024
            self.iso_path.write_bytes(b'AEGIS-ISO-SIMULATED' + b'\x00' * min(size_bytes, 4096))
            self.log(f"[SIMULATED] ISO created: {self.iso_path}")
        else:
            self.copy_isolinux_files()
            self.setup_efi_boot()
            
            efi_img = self.create_efi_image()
            
            isohdpfx_paths = [
                "/usr/lib/ISOLINUX/isohdpfx.bin",
                "/usr/share/syslinux/isohdpfx.bin",
                "/usr/lib/syslinux/mbr/isohdpfx.bin"
            ]
            
            isohdpfx = None
            for path in isohdpfx_paths:
                if os.path.exists(path):
                    isohdpfx = path
                    break
            
            if not isohdpfx:
                self.log("Warning: isohdpfx.bin not found, ISO may not be bootable from USB", "WARN")
                isohdpfx = "/usr/lib/ISOLINUX/isohdpfx.bin"
            
            self.log("Running xorriso to create hybrid bootable ISO...")
            
            xorriso_cmd = f"""xorriso -as mkisofs \
    -iso-level 3 \
    -full-iso9660-filenames \
    -joliet \
    -joliet-long \
    -rational-rock \
    -volid "AEGIS_{self.edition.upper()[:11]}" \
    -appid "{self.config['name']} {VERSION}" \
    -publisher "Aegis OS Project" \
    -preparer "Aegis Build System v{VERSION}" \
    -output "{self.iso_path}" \
    -eltorito-boot isolinux/isolinux.bin \
    -eltorito-catalog isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -isohybrid-mbr {isohdpfx}"""
            
            if efi_img and efi_img.exists():
                xorriso_cmd += f""" \
    -eltorito-alt-boot \
    -e boot/grub/efi.img \
    -no-emul-boot \
    -isohybrid-gpt-basdat"""
            
            xorriso_cmd += f""" \
    "{self.iso_dir}" """
            
            try:
                self.run_command(xorriso_cmd, shell=True, timeout=3600)
            except subprocess.CalledProcessError as e:
                self.log(f"xorriso failed: {e}", "WARN")
                self.log("Trying genisoimage as fallback...", "WARN")
                
                genisoimage_cmd = f"""genisoimage \
    -o "{self.iso_path}" \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R -V "AEGIS_{self.edition.upper()[:11]}" \
    "{self.iso_dir}" """
                
                self.run_command(genisoimage_cmd, shell=True, timeout=3600)
                
                if shutil.which('isohybrid') and os.path.exists(isohdpfx):
                    try:
                        self.run_command(f"isohybrid {self.iso_path}", shell=True)
                        self.log("Applied hybrid MBR for USB boot")
                    except Exception:
                        pass
            
            if self.iso_path.exists():
                actual_size = self.iso_path.stat().st_size
                if actual_size == 0:
                    raise RuntimeError("ISO creation failed: file is empty")
                self.log(f"ISO created: {actual_size / (1024*1024):.1f} MB", "SUCCESS")
            else:
                raise RuntimeError("ISO creation failed: file not created")
        
        self.log(f"ISO created: {self.iso_path}", "SUCCESS")
        return self.iso_path
    
    def generate_checksums(self) -> Dict[str, str]:
        """Generate checksums for the ISO file"""
        self.log("Generating checksums...")
        
        checksums = {}
        
        if not self.iso_path.exists():
            self.log("Warning: ISO file not found, skipping checksum generation", "WARN")
            return checksums
        
        for algo in ['sha256', 'sha512', 'md5']:
            checksum = get_file_checksum(self.iso_path, algo)
            if checksum:
                checksums[algo] = checksum
                
                checksum_file = OUTPUT_DIR / f"aegis-{self.edition}-{VERSION}.{algo}"
                checksum_file.write_text(f"{checksum}  {self.iso_path.name}\n")
                self.log(f"Generated {algo.upper()} checksum")
        
        all_checksums_file = OUTPUT_DIR / f"aegis-{self.edition}-{VERSION}.checksums"
        with open(all_checksums_file, 'w') as f:
            f.write(f"# Checksums for {self.iso_path.name}\n")
            f.write(f"# Generated: {BUILD_TIMESTAMP}\n\n")
            for algo, checksum in checksums.items():
                f.write(f"{algo.upper()}: {checksum}\n")
        
        return checksums
    
    def sign_iso(self) -> Optional[Path]:
        """Sign the ISO with GPG if key is available"""
        self.log("Attempting to sign ISO...")
        
        if not self.gpg_key:
            if shutil.which('gpg'):
                try:
                    result = subprocess.run(
                        ['gpg', '--list-secret-keys'],
                        capture_output=True,
                        text=True
                    )
                    if 'sec' not in result.stdout:
                        self.log("No GPG signing key available, skipping signing", "WARN")
                        return None
                except Exception:
                    self.log("GPG not properly configured, skipping signing", "WARN")
                    return None
            else:
                self.log("GPG not installed, skipping signing", "WARN")
                return None
        
        if not self.iso_path.exists():
            self.log("ISO file not found, skipping signing", "WARN")
            return None
        
        sig_path = OUTPUT_DIR / f"{self.iso_path.name}.sig"
        asc_path = OUTPUT_DIR / f"{self.iso_path.name}.asc"
        
        try:
            gpg_cmd = ['gpg', '--armor', '--detach-sign', '-o', str(asc_path)]
            if self.gpg_key:
                gpg_cmd.extend(['--local-user', self.gpg_key])
            gpg_cmd.append(str(self.iso_path))
            
            if self.simulate:
                self.log(f"[SIMULATED] Would run: {' '.join(gpg_cmd)}")
                return None
            
            subprocess.run(gpg_cmd, check=True)
            self.log(f"ISO signed: {asc_path}", "SUCCESS")
            return asc_path
            
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to sign ISO: {e}", "WARN")
            return None
        except Exception as e:
            self.log(f"Signing error: {e}", "WARN")
            return None
    
    def generate_manifest(self) -> Path:
        """Generate comprehensive build manifest with all file hashes"""
        self.log("Generating build manifest...")
        
        build_duration = None
        if self.build_start_time:
            build_duration = (datetime.now() - self.build_start_time).total_seconds()
        
        iso_size_bytes = 0
        iso_size_mb = self.config.get('size_mb', 2000)
        checksums = {}
        
        if self.iso_path.exists():
            iso_size_bytes = self.iso_path.stat().st_size
            iso_size_mb = round(iso_size_bytes / (1024 * 1024), 2)
            checksums = self.generate_checksums()
        
        signature_path = self.sign_iso()
        
        self.manifest.update({
            'build_info': {
                'version': VERSION,
                'edition': self.edition,
                'edition_name': self.config['name'],
                'codename': self.config['codename'],
                'tier': self.config.get('tier', 'free'),
                'kernel': KERNEL_VERSION,
                'ubuntu_base': f"{UBUNTU_VERSION} ({UBUNTU_CODENAME})",
                'build_timestamp': BUILD_TIMESTAMP,
                'build_duration_seconds': build_duration,
                'simulation_mode': self.simulate,
                'simulation_reason': self.simulation_reason if self.simulate else None,
                'build_system': f"Aegis Build System v{VERSION}",
                'build_host': platform.node(),
                'build_platform': platform.platform(),
                'python_version': platform.python_version()
            },
            'iso_info': {
                'filename': self.iso_path.name,
                'path': str(self.iso_path),
                'size_bytes': iso_size_bytes,
                'size_mb': iso_size_mb,
                'checksums': checksums,
                'signature': str(signature_path) if signature_path else None,
                'is_bootable': not self.simulate and iso_size_bytes > 1024 * 1024,
                'boot_modes': ['BIOS', 'UEFI'] if not self.simulate else [],
                'is_hybrid': not self.simulate
            },
            'edition_info': {
                'description': self.config['description'],
                'desktop': self.config.get('desktop'),
                'gaming_optimized': self.config.get('gaming_optimized', False),
                'enterprise_ready': self.config.get('enterprise_ready', False),
                'ml_frameworks': self.config.get('ml_frameworks', []),
                'systemd_services': self.config.get('systemd_services', [])
            },
            'file_listing': []
        })
        
        if self.iso_dir.exists():
            for file in self.iso_dir.rglob('*'):
                if file.is_file():
                    file_size = file.stat().st_size
                    file_entry = {
                        'path': str(file.relative_to(self.iso_dir)),
                        'size': file_size,
                    }
                    if file_size < 10*1024*1024:
                        file_entry['sha256'] = get_file_checksum(file, 'sha256')
                    self.manifest['file_listing'].append(file_entry)
        
        manifest_path = MANIFEST_DIR / f"manifest-{self.edition}-{VERSION}.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        
        self.log(f"Manifest saved: {manifest_path}", "SUCCESS")
        return manifest_path
    
    def build(self) -> bool:
        """Main build process"""
        self.build_start_time = datetime.now()
        
        self.log("=" * 70)
        self.log(f"AEGIS OS BUILD SYSTEM v{VERSION}")
        self.log("=" * 70)
        self.log(f"Edition: {self.config['name']}")
        self.log(f"Tier: {self.config.get('tier', 'free').upper()}")
        self.log(f"Description: {self.config['description']}")
        self.log(f"Kernel: {KERNEL_VERSION}")
        self.log(f"Target Size: ~{self.config.get('size_mb', 2000)} MB")
        
        if self.simulate:
            self.log("=" * 70)
            self.log("SIMULATION MODE ACTIVE", "WARN")
            self.log(f"Reason: {self.simulation_reason}")
            self.log("=" * 70)
            self.log("For real build on Ubuntu 24.04:")
            self.log("  sudo apt install debootstrap squashfs-tools xorriso isolinux syslinux rsync grub-pc-bin shim-signed")
            self.log(f"  sudo python3 {__file__} --edition {self.edition} --real-build")
        else:
            self.log("=" * 70)
            self.log("PRODUCTION BUILD MODE", "SUCCESS")
            self.log("Creating bootable ISO with real content")
            self.log("=" * 70)
        
        self.log("")
        
        try:
            if not self.check_dependencies():
                if not self.simulate:
                    self.log("Build aborted: missing dependencies", "ERROR")
                    return False
            
            chroot_dir = self.create_base_system()
            self.install_packages(chroot_dir)
            self.apply_overlays()
            self.configure_system(chroot_dir)
            self.run_post_build_hooks()
            squashfs_path = self.create_squashfs(chroot_dir)
            iso_path = self.create_iso(squashfs_path)
            manifest_path = self.generate_manifest()
            
            build_duration = (datetime.now() - self.build_start_time).total_seconds()
            
            self.log("")
            self.log("=" * 70)
            self.log("BUILD SUCCESSFUL!", "SUCCESS")
            self.log("=" * 70)
            self.log(f"ISO:      {iso_path}")
            
            if iso_path.exists():
                actual_size = iso_path.stat().st_size / (1024 * 1024)
                self.log(f"Size:     {actual_size:.1f} MB")
            else:
                self.log(f"Size:     ~{self.config.get('size_mb', 2000)} MB (estimated)")
            
            self.log(f"Manifest: {manifest_path}")
            self.log(f"Log:      {self.log_file}")
            self.log(f"Duration: {build_duration:.1f} seconds")
            
            checksums_file = OUTPUT_DIR / f"aegis-{self.edition}-{VERSION}.sha256"
            if checksums_file.exists():
                self.log(f"Checksum: {checksums_file}")
            
            if self.simulate:
                self.log("")
                self.log("NOTE: This was a simulation. The ISO is a placeholder.", "WARN")
                self.log("For a real bootable ISO, run on Linux with:")
                self.log(f"  sudo python3 {__file__} --edition {self.edition} --real-build")
            else:
                self.log("")
                self.log("The ISO is ready for use!", "SUCCESS")
                self.log("Boot modes: BIOS (Legacy) and UEFI")
                self.log("You can burn it to a USB drive with:")
                self.log(f"  sudo dd if={iso_path} of=/dev/sdX bs=4M status=progress oflag=sync")
                self.log("")
                self.log("Or use a tool like balenaEtcher, Rufus, or Ventoy")
            
            return True
            
        except Exception as e:
            self.log(f"Build failed: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            return False
            
        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description=f"Aegis OS Build System v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 build-aegis.py --edition freemium --simulate
  python3 build-aegis.py --edition gamer --real-build --verbose
  python3 build-aegis.py --edition all --simulate
  python3 build-aegis.py --check-deps
  python3 build-aegis.py --list-editions

Editions:
  freemium   - Basic Linux with XFCE desktop (Free)
  basic      - Professional productivity suite
  workplace  - Office workstation environment
  gamer      - Gaming optimized with Steam/Lutris
  ai         - AI/ML development platform
  gamer-ai   - Gaming + AI development combo
  server     - Enterprise server deployment
"""
    )
    
    parser.add_argument('--edition', '-e', 
                       help='Edition to build (or "all")')
    parser.add_argument('--simulate', '-s', action='store_true',
                       help='Run in simulation mode (no root required)')
    parser.add_argument('--real-build', '-r', action='store_true',
                       help='Force real build mode (requires root)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--check-deps', action='store_true',
                       help='Check build dependencies and exit')
    parser.add_argument('--list-editions', action='store_true',
                       help='List available editions and exit')
    parser.add_argument('--gpg-key', 
                       help='GPG key ID for signing ISOs')
    parser.add_argument('--version', action='version', 
                       version=f'Aegis Build System v{VERSION}')
    
    args = parser.parse_args()
    
    if args.check_deps:
        check_build_environment(verbose=True)
        return 0
    
    if args.list_editions:
        print(f"\nAegis OS Build System v{VERSION}")
        print("=" * 60)
        print("\nAvailable Editions:\n")
        for edition_id, config in EDITIONS.items():
            tier = config.get('tier', 'free').upper()
            print(f"  {edition_id:12} [{tier:12}] - {config['name']}")
            print(f"               {config['description']}")
            print(f"               Size: ~{config.get('size_mb', 2000)} MB")
            if config.get('desktop'):
                print(f"               Desktop: {config['desktop']}")
            if config.get('gaming_optimized'):
                print(f"               Gaming optimized: Yes")
            if config.get('ml_frameworks'):
                print(f"               ML Frameworks: {', '.join(config['ml_frameworks'][:3])}...")
            print()
        return 0
    
    if not args.edition:
        parser.print_help()
        return 1
    
    if args.edition.lower() == 'all':
        editions = list(EDITIONS.keys())
    else:
        if args.edition not in EDITIONS:
            print(f"Error: Unknown edition '{args.edition}'")
            print(f"Available editions: {', '.join(EDITIONS.keys())}")
            return 1
        editions = [args.edition]
    
    results = {}
    for edition in editions:
        print(f"\n{'='*70}")
        print(f"Building {EDITIONS[edition]['name']}...")
        print(f"{'='*70}\n")
        
        builder = AegisBuilder(
            edition=edition,
            simulate=args.simulate,
            force_real=args.real_build,
            verbose=args.verbose,
            gpg_key=args.gpg_key
        )
        
        results[edition] = builder.build()
    
    print(f"\n{'='*70}")
    print("BUILD SUMMARY")
    print(f"{'='*70}")
    for edition, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {edition}: {status}")
    
    all_success = all(results.values())
    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
