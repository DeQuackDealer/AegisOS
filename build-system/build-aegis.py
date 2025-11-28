#!/usr/bin/env python3
"""
Aegis OS Build System v1.5.0
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
from pathlib import Path
from datetime import datetime, timezone

VERSION = "1.5.0"
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
            "code",
            "libreoffice",
            "gimp",
            "inkscape",
            "vlc",
            "audacity",
            "kdenlive",
            "gparted",
            "synaptic",
            "bleachbit",
            "virtualbox",
            "qemu-system-x86",
            "virt-manager",
            "libvirt-daemon-system",
            "firewalld",
            "fail2ban",
            "clamav",
            "clamav-daemon",
            "rkhunter",
            "lynis",
            "aide",
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
            "gimp-plugin-registry",
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
            "ttf-mscorefonts-installer",
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
            "pavucontrol",
            "fonts-ubuntu",
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
            "nvidia-cudnn",
            "nvidia-driver-550",
            "nvidia-settings",
            "libnvinfer8",
            "libnvinfer-dev",
            "code",
            "spyder",
            "postgresql",
            "postgresql-client",
            "redis-server",
            "redis-tools",
            "mongodb-org",
            "docker.io",
            "docker-compose",
            "nodejs",
            "npm",
            "firefox",
            "chromium-browser",
            "network-manager",
            "pulseaudio",
            "fonts-ubuntu",
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
            "nvidia-cudnn",
            "code",
            "spyder",
            "docker.io",
            "docker-compose",
            "firefox",
            "chromium-browser",
            "network-manager",
            "pulseaudio",
            "pavucontrol",
            "fonts-ubuntu",
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
            "grafana",
            "nagios4",
            "nagios-plugins",
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
        ],
        "enterprise_ready": True,
        "size_mb": 3000,
        "description": "Enterprise-grade server deployment with security hardening"
    }
}


def get_file_checksum(filepath, algorithm='sha256'):
    """Calculate file checksum"""
    hash_func = hashlib.new(algorithm)
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except FileNotFoundError:
        return None


def is_replit_environment():
    """Check if running on Replit platform"""
    return bool(os.environ.get('REPL_ID') or os.environ.get('REPLIT_DEPLOYMENT') or 
                os.environ.get('REPL_SLUG') or os.environ.get('REPLIT'))


def has_root_privileges():
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


def check_tool_available(tool_name, tool_info):
    """Check if a specific tool is available"""
    if shutil.which(tool_name):
        return True
    if 'check_path' in tool_info and os.path.exists(tool_info['check_path']):
        return True
    return False


def check_build_dependencies(verbose=False):
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


def check_build_environment(verbose=False):
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


def should_simulate(force_simulate=False, force_real=False):
    """
    Determine if build should run in simulation mode.
    
    Args:
        force_simulate: User explicitly requested simulation
        force_real: User explicitly requested real build
    
    Returns:
        (simulate: bool, reason: str)
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


class AegisBuilder:
    """Main build class for Aegis OS"""
    
    def __init__(self, edition, simulate=False, force_real=False, verbose=False):
        self.edition = edition
        self.config = EDITIONS[edition]
        self.verbose = verbose
        self.force_real = force_real
        
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
        
        for d in [OUTPUT_DIR, LOGS_DIR, MANIFEST_DIR, self.work_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        self.log_file = LOGS_DIR / f"build-{edition}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        
    def log(self, message, level="INFO"):
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
        else:
            print(log_msg)
            
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")
    
    def run_command(self, cmd, shell=False, check=True, capture=True, sudo=False):
        """Execute shell command with logging"""
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
                check=check
            )
            if result.stdout and self.verbose:
                self.log(f"Output: {result.stdout[:500]}")
            return result.stdout if result.stdout else ""
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e.stderr}", "ERROR")
            raise
    
    def chroot_run(self, cmd):
        """Run command in chroot environment"""
        if self.simulate:
            self.log(f"[SIMULATED CHROOT] {cmd}")
            return ""
        return self.run_command(f"chroot {self.chroot_dir} /bin/bash -c '{cmd}'", shell=True)
    
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
        """Unmount chroot filesystems"""
        if self.simulate:
            return
        
        for mount_point in reversed(self.mounted_points):
            try:
                self.run_command(f"umount {mount_point}", shell=True, check=False)
            except Exception:
                try:
                    self.run_command(f"umount -l {mount_point}", shell=True, check=False)
                except Exception:
                    pass
        self.mounted_points = []
    
    def check_dependencies(self):
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
    
    def create_base_system(self):
        """Create base Ubuntu system using debootstrap"""
        self.log(f"Creating base system for {self.edition}...")
        
        if self.chroot_dir.exists():
            self.log("Removing existing chroot directory...")
            if not self.simulate:
                shutil.rmtree(self.chroot_dir, ignore_errors=True)
        
        self.chroot_dir.mkdir(parents=True, exist_ok=True)
        
        if self.simulate:
            dirs = ["bin", "boot", "boot/grub", "dev", "etc", "etc/apt", 
                   "etc/default", "etc/skel/.config", "home", "lib", "lib64", 
                   "lib/modules", "media", "mnt", "opt", "proc", "root", "run", 
                   "sbin", "srv", "sys", "tmp", "usr", "usr/bin", "usr/lib",
                   "usr/share", "usr/local/bin", "var", "var/lib", "var/log",
                   "var/lib/aegis", "var/cache/apt/archives"]
            for d in dirs:
                (self.chroot_dir / d).mkdir(parents=True, exist_ok=True)
                
            self._create_simulated_files()
        else:
            self.log(f"Running debootstrap for {UBUNTU_CODENAME}...")
            self.log("This may take 10-30 minutes depending on network speed...")
            
            self.run_command(
                f"debootstrap --arch=amd64 --variant=minbase {UBUNTU_CODENAME} {self.chroot_dir} {UBUNTU_MIRROR}",
                shell=True
            )
            
            sources_list = f"""deb {UBUNTU_MIRROR} {UBUNTU_CODENAME} main restricted universe multiverse
deb {UBUNTU_MIRROR} {UBUNTU_CODENAME}-updates main restricted universe multiverse
deb {UBUNTU_MIRROR} {UBUNTU_CODENAME}-security main restricted universe multiverse
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
"""
        (self.chroot_dir / "etc/os-release").write_text(os_release)
        
        (self.chroot_dir / "etc/hostname").write_text(
            self.config['name'].replace(" ", "-").lower() + "\n"
        )
    
    def install_packages(self, chroot_dir):
        """Install edition-specific packages"""
        self.log(f"Installing packages for {self.edition}...")
        
        packages = self.config['packages']
        
        pkg_list = chroot_dir / "var/lib/aegis/packages.list"
        pkg_list.parent.mkdir(parents=True, exist_ok=True)
        
        with open(pkg_list, 'w') as f:
            for pkg in packages:
                f.write(f"{pkg}\n")
        
        self.manifest['packages'] = {
            'count': len(packages),
            'list': packages,
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
                self.chroot_run("apt-get update")
                
                self.log("Upgrading base system...")
                self.chroot_run("DEBIAN_FRONTEND=noninteractive apt-get upgrade -y")
                
                self.log(f"Installing {len(packages)} packages...")
                self.log("This may take 30-60 minutes depending on edition size...")
                
                batch_size = 20
                for i in range(0, len(packages), batch_size):
                    batch = packages[i:i+batch_size]
                    pkg_string = " ".join(batch)
                    self.log(f"Installing batch {i//batch_size + 1}/{(len(packages) + batch_size - 1)//batch_size}...")
                    
                    try:
                        self.chroot_run(
                            f"DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends {pkg_string}"
                        )
                    except Exception as e:
                        self.log(f"Warning: Some packages in batch failed: {e}", "WARN")
                        for pkg in batch:
                            try:
                                self.chroot_run(
                                    f"DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends {pkg}"
                                )
                            except Exception:
                                self.log(f"Warning: Failed to install {pkg}", "WARN")
                
                self.log("Cleaning up package cache...")
                self.chroot_run("apt-get clean")
                self.chroot_run("rm -rf /var/lib/apt/lists/*")
                
            finally:
                self.unmount_chroot_filesystems()
        
        self.log(f"Package installation complete ({len(packages)} packages)", "SUCCESS")
    
    def configure_system(self, chroot_dir):
        """Apply system configurations"""
        self.log("Configuring system...")
        
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
    
    def create_squashfs(self, chroot_dir):
        """Create compressed filesystem"""
        self.log("Creating squashfs filesystem...")
        
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
""")
            
            self.log("Compressing filesystem with mksquashfs (this may take a while)...")
            
            self.run_command(
                f"mksquashfs {chroot_dir} {squashfs_path} "
                f"-comp xz -b 1M -Xdict-size 100% "
                f"-ef {exclude_list} -noappend",
                shell=True
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
            "isolinux",
            "casper",
            "EFI/boot",
            ".disk",
            "preseed",
            "pool/main"
        ]
        for d in dirs:
            (self.iso_dir / d).mkdir(parents=True, exist_ok=True)
        
        grub_cfg = f"""set default=0
set timeout=10

menuentry "{self.config['name']}" {{
    linux /casper/vmlinuz boot=casper quiet splash ---
    initrd /casper/initrd
}}

menuentry "{self.config['name']} (Safe Mode)" {{
    linux /casper/vmlinuz boot=casper nomodeset ---
    initrd /casper/initrd
}}

menuentry "Check disc for defects" {{
    linux /casper/vmlinuz boot=casper integrity-check ---
    initrd /casper/initrd
}}

menuentry "Memory test" {{
    linux16 /boot/memtest86+.bin
}}
"""
        (self.iso_dir / "boot/grub/grub.cfg").write_text(grub_cfg)
        
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

LABEL live
  MENU LABEL Start {self.config['name']}
  KERNEL /casper/vmlinuz
  APPEND initrd=/casper/initrd boot=casper quiet splash ---

LABEL live-safe
  MENU LABEL Start {self.config['name']} (Safe Graphics)
  KERNEL /casper/vmlinuz
  APPEND initrd=/casper/initrd boot=casper nomodeset ---

LABEL memtest
  MENU LABEL Memory Test
  KERNEL /boot/memtest86+.bin

LABEL hd
  MENU LABEL Boot from first hard disk
  LOCALBOOT 0x80
"""
        (self.iso_dir / "isolinux/isolinux.cfg").write_text(isolinux_cfg)
        
        disk_info = f"{self.config['name']} {VERSION} \"{self.config['codename']}\" - Release amd64"
        (self.iso_dir / ".disk/info").write_text(disk_info)
        (self.iso_dir / ".disk/base_installable").touch()
        (self.iso_dir / ".disk/cd_type").write_text("full_cd/single")
        
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
1. Boot from this ISO
2. Select "Start {self.config['name']}" from the menu
3. Follow the on-screen installer

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
    
    def copy_boot_files(self, casper_dir):
        """Copy kernel and initrd to casper directory"""
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
        """Copy isolinux boot files"""
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
            "vesamenu.c32"
        ]
        
        for filename in required_files:
            for path in isolinux_paths:
                src = Path(path) / filename
                if src.exists():
                    shutil.copy2(src, self.iso_dir / "isolinux" / filename)
                    break
    
    def create_iso(self, squashfs_path):
        """Generate bootable ISO"""
        self.log("Creating ISO image...")
        
        self.create_iso_structure()
        
        casper_dir = self.iso_dir / "casper"
        if squashfs_path.exists():
            shutil.copy2(squashfs_path, casper_dir / "filesystem.squashfs")
        
        self.copy_boot_files(casper_dir)
        
        if self.simulate:
            self.iso_path.parent.mkdir(parents=True, exist_ok=True)
            size_bytes = self.config.get('size_mb', 2000) * 1024
            self.iso_path.write_bytes(b'AEGIS-ISO-SIMULATED' + b'\x00' * min(size_bytes, 4096))
            self.log(f"[SIMULATED] ISO created: {self.iso_path}")
        else:
            self.copy_isolinux_files()
            
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
                self.log("Warning: isohdpfx.bin not found, ISO may not be bootable", "WARN")
                isohdpfx = "/usr/lib/ISOLINUX/isohdpfx.bin"
            
            self.log("Running xorriso to create bootable ISO...")
            
            xorriso_cmd = f"""xorriso -as mkisofs \
    -iso-level 3 \
    -full-iso9660-filenames \
    -volid "AEGIS_{self.edition.upper()}" \
    -output "{self.iso_path}" \
    -eltorito-boot isolinux/isolinux.bin \
    -eltorito-catalog isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -isohybrid-mbr {isohdpfx} \
    "{self.iso_dir}" """
            
            try:
                self.run_command(xorriso_cmd, shell=True)
            except subprocess.CalledProcessError:
                self.log("xorriso failed, trying genisoimage...", "WARN")
                
                genisoimage_cmd = f"""genisoimage \
    -o "{self.iso_path}" \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R -V "AEGIS_{self.edition.upper()}" \
    "{self.iso_dir}" """
                
                self.run_command(genisoimage_cmd, shell=True)
            
            if self.iso_path.exists():
                actual_size = self.iso_path.stat().st_size
                if actual_size == 0:
                    raise RuntimeError("ISO creation failed: file is empty")
                self.log(f"ISO created: {actual_size / (1024*1024):.1f} MB", "SUCCESS")
            else:
                raise RuntimeError("ISO creation failed: file not created")
        
        self.log(f"ISO created: {self.iso_path}", "SUCCESS")
        return self.iso_path
    
    def generate_manifest(self):
        """Generate build manifest with checksums and file listings"""
        self.log("Generating build manifest...")
        
        build_duration = None
        if self.build_start_time:
            build_duration = (datetime.now() - self.build_start_time).total_seconds()
        
        iso_size_bytes = 0
        iso_size_mb = self.config.get('size_mb', 2000)
        iso_checksum_sha256 = None
        iso_checksum_md5 = None
        
        if self.iso_path.exists():
            iso_size_bytes = self.iso_path.stat().st_size
            iso_size_mb = round(iso_size_bytes / (1024 * 1024), 2)
            iso_checksum_sha256 = get_file_checksum(self.iso_path)
            iso_checksum_md5 = get_file_checksum(self.iso_path, 'md5')
        
        self.manifest.update({
            'build_info': {
                'version': VERSION,
                'edition': self.edition,
                'edition_name': self.config['name'],
                'codename': self.config['codename'],
                'kernel': KERNEL_VERSION,
                'ubuntu_base': f"{UBUNTU_VERSION} ({UBUNTU_CODENAME})",
                'build_timestamp': BUILD_TIMESTAMP,
                'build_duration_seconds': build_duration,
                'simulation_mode': self.simulate,
                'simulation_reason': self.simulation_reason if self.simulate else None,
                'build_system': f"Aegis Build System v{VERSION}",
                'build_host': platform.node(),
                'build_platform': platform.platform()
            },
            'iso_info': {
                'filename': self.iso_path.name,
                'path': str(self.iso_path),
                'size_bytes': iso_size_bytes,
                'size_mb': iso_size_mb,
                'checksum_sha256': iso_checksum_sha256,
                'checksum_md5': iso_checksum_md5,
                'is_bootable': not self.simulate and iso_size_bytes > 1024 * 1024
            },
            'edition_info': {
                'description': self.config['description'],
                'desktop': self.config.get('desktop'),
                'gaming_optimized': self.config.get('gaming_optimized', False),
                'enterprise_ready': self.config.get('enterprise_ready', False),
                'ml_frameworks': self.config.get('ml_frameworks', [])
            },
            'file_listing': []
        })
        
        if self.iso_dir.exists():
            for file in self.iso_dir.rglob('*'):
                if file.is_file():
                    file_size = file.stat().st_size
                    self.manifest['file_listing'].append({
                        'path': str(file.relative_to(self.iso_dir)),
                        'size': file_size,
                        'checksum': get_file_checksum(file) if file_size < 10*1024*1024 else None
                    })
        
        manifest_path = MANIFEST_DIR / f"manifest-{self.edition}-{VERSION}.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        
        checksum_path = OUTPUT_DIR / f"aegis-{self.edition}-{VERSION}.sha256"
        if self.iso_path.exists() and iso_checksum_sha256:
            checksum_path.write_text(f"{iso_checksum_sha256}  {self.iso_path.name}\n")
        
        self.log(f"Manifest saved: {manifest_path}", "SUCCESS")
        return manifest_path
    
    def build(self):
        """Main build process"""
        self.build_start_time = datetime.now()
        
        self.log("=" * 70)
        self.log(f"AEGIS OS BUILD SYSTEM v{VERSION}")
        self.log("=" * 70)
        self.log(f"Edition: {self.config['name']}")
        self.log(f"Description: {self.config['description']}")
        self.log(f"Kernel: {KERNEL_VERSION}")
        self.log(f"Target Size: ~{self.config.get('size_mb', 2000)} MB")
        
        if self.simulate:
            self.log("=" * 70)
            self.log("SIMULATION MODE ACTIVE", "WARN")
            self.log(f"Reason: {self.simulation_reason}")
            self.log("=" * 70)
            self.log("For real build on Ubuntu 24.04:")
            self.log("  sudo apt install debootstrap squashfs-tools xorriso isolinux syslinux")
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
            self.configure_system(chroot_dir)
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
            
            if self.simulate:
                self.log("")
                self.log("NOTE: This was a simulation. The ISO is a placeholder.", "WARN")
                self.log("For a real bootable ISO, run on Linux with:")
                self.log(f"  sudo python3 {__file__} --edition {self.edition} --real-build")
            else:
                self.log("")
                self.log("The ISO is ready for use!", "SUCCESS")
                self.log("You can burn it to a USB drive with:")
                self.log(f"  sudo dd if={iso_path} of=/dev/sdX bs=4M status=progress")
            
            return True
            
        except Exception as e:
            self.log(f"Build failed: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            return False
        finally:
            self.unmount_chroot_filesystems()


def list_editions():
    """Print available editions"""
    print("\n" + "=" * 70)
    print("AEGIS OS EDITIONS")
    print("=" * 70 + "\n")
    
    for edition_id, config in EDITIONS.items():
        print(f"  {edition_id:12} - {config['name']}")
        print(f"               {config['description']}")
        print(f"               Size: ~{config.get('size_mb', 2000)} MB")
        if config.get('desktop'):
            print(f"               Desktop: {config['desktop']}")
        if config.get('gaming_optimized'):
            print(f"               [Gaming Optimized]")
        if config.get('enterprise_ready'):
            print(f"               [Enterprise Ready]")
        if config.get('ml_frameworks'):
            print(f"               ML Frameworks: {len(config['ml_frameworks'])}")
        print()


def check_deps_command():
    """Run dependency check as standalone command"""
    print("\n" + "=" * 60)
    print("AEGIS OS BUILD SYSTEM - DEPENDENCY CHECK")
    print("=" * 60 + "\n")
    
    env = check_build_environment(verbose=True)
    
    print("=" * 60)
    if env['can_real_build']:
        print("\n✓ System is ready for REAL builds!")
        print("  Run: sudo python3 build-aegis.py --edition <edition> --real-build")
        return 0
    else:
        print(f"\n⚠ System requires simulation mode")
        print(f"  Reason: {env['simulation_reason']}")
        
        if env['missing_required_deps']:
            print("\n  To enable real builds:")
            print(f"  sudo apt install {' '.join(env['missing_required_deps'])}")
        
        if not env['has_root'] and env['is_linux']:
            print("\n  Also run with sudo for real builds:")
            print("  sudo python3 build-aegis.py --edition <edition> --real-build")
        
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description=f"Aegis OS Build System v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Check build dependencies:
    python3 build-aegis.py --check-deps
    
  Build freemium edition (auto-detect mode):
    python3 build-aegis.py --edition freemium
    
  Force simulation mode:
    python3 build-aegis.py --edition freemium --simulate
    
  Force real build (requires root and dependencies):
    sudo python3 build-aegis.py --edition freemium --real-build
    
  Build all editions (simulation):
    python3 build-aegis.py --edition all --simulate
    
  List available editions:
    python3 build-aegis.py --list-editions

For real builds on Ubuntu 24.04, first install dependencies:
  sudo apt install debootstrap squashfs-tools xorriso isolinux syslinux genisoimage
"""
    )
    
    parser.add_argument(
        "--edition",
        choices=list(EDITIONS.keys()) + ["all"],
        help="Edition to build (or 'all' for all editions)"
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Force simulation mode (no actual system changes)"
    )
    parser.add_argument(
        "--real-build", "--no-simulation",
        dest="real_build",
        action="store_true",
        help="Force real build mode (requires root and dependencies)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--list-editions",
        action="store_true",
        help="List all available editions"
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check build dependencies and system requirements"
    )
    
    args = parser.parse_args()
    
    if args.check_deps:
        return check_deps_command()
    
    if args.list_editions:
        list_editions()
        return 0
    
    if not args.edition:
        parser.print_help()
        return 1
    
    if args.simulate and args.real_build:
        print("Error: Cannot specify both --simulate and --real-build")
        return 1
    
    print()
    print("=" * 70)
    print(f"AEGIS OS BUILD SYSTEM v{VERSION}")
    print("=" * 70)
    print(f"Build Timestamp: {BUILD_TIMESTAMP}")
    print(f"Kernel Version:  {KERNEL_VERSION}")
    print(f"Ubuntu Base:     {UBUNTU_VERSION} ({UBUNTU_CODENAME})")
    print()
    
    if args.edition == "all":
        editions = list(EDITIONS.keys())
    else:
        editions = [args.edition]
    
    results = {}
    for edition in editions:
        print(f"\n{'#' * 70}")
        print(f"# Building: {edition}")
        print(f"{'#' * 70}\n")
        
        builder = AegisBuilder(
            edition, 
            simulate=args.simulate, 
            force_real=args.real_build,
            verbose=args.verbose
        )
        success = builder.build()
        results[edition] = success
    
    print("\n" + "=" * 70)
    print("BUILD SUMMARY")
    print("=" * 70)
    for edition, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        color = "\033[92m" if success else "\033[91m"
        print(f"  {edition:15} [{color}{status}\033[0m]")
    print("=" * 70)
    
    all_success = all(results.values())
    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
