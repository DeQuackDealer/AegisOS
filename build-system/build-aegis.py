#!/usr/bin/env python3
"""
Aegis OS Build System v1.5.0
Generates bootable ISO images for all Aegis OS editions

Supports two modes:
- Simulation Mode: For development/testing (works on Replit)
- Production Mode: Full ISO build on Linux systems with root access

Usage:
    python3 build-aegis.py --edition freemium [--simulate] [--verbose]
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


def is_simulation_mode():
    """Detect if running in simulation mode (Replit or non-Linux)"""
    if os.environ.get('REPL_ID') or os.environ.get('REPLIT_DEPLOYMENT'):
        return True
    if platform.system() != 'Linux':
        return True
    if os.geteuid() != 0:
        return True
    return False


class AegisBuilder:
    """Main build class for Aegis OS"""
    
    def __init__(self, edition, simulate=False, verbose=False):
        self.edition = edition
        self.config = EDITIONS[edition]
        self.simulate = simulate or is_simulation_mode()
        self.verbose = verbose
        self.work_dir = WORK_DIR / edition
        self.chroot_dir = self.work_dir / "chroot"
        self.iso_dir = self.work_dir / "iso"
        self.squashfs_dir = self.work_dir / "squashfs"
        self.iso_path = OUTPUT_DIR / f"aegis-{edition}-{VERSION}.iso"
        self.manifest = {}
        self.build_start_time = None
        
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
    
    def run_command(self, cmd, shell=False, check=True, capture=True):
        """Execute shell command with logging"""
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
    
    def check_dependencies(self):
        """Verify build dependencies are installed"""
        self.log("Checking build dependencies...")
        
        required_tools = {
            "debootstrap": "debootstrap",
            "mksquashfs": "squashfs-tools",
            "xorriso": "xorriso",
            "isolinux": "isolinux",
            "syslinux": "syslinux",
            "genisoimage": "genisoimage"
        }
        
        if self.simulate:
            self.log("Running in SIMULATION MODE - dependency check skipped")
            self.log("Full build requires: sudo apt install " + " ".join(required_tools.values()))
            return True
        
        missing = []
        for tool, package in required_tools.items():
            if shutil.which(tool) is None:
                missing.append(package)
        
        if missing:
            self.log(f"Missing tools: {', '.join(missing)}", "ERROR")
            self.log(f"Install with: sudo apt install {' '.join(missing)}")
            return False
        
        self.log("All dependencies satisfied", "SUCCESS")
        return True
    
    def create_base_system(self):
        """Create base Ubuntu system using debootstrap"""
        self.log(f"Creating base system for {self.edition}...")
        
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
            self.run_command(
                f"debootstrap --arch=amd64 {UBUNTU_CODENAME} {self.chroot_dir} {UBUNTU_MIRROR}"
            )
            
            sources_list = f"""
deb {UBUNTU_MIRROR} {UBUNTU_CODENAME} main restricted universe multiverse
deb {UBUNTU_MIRROR} {UBUNTU_CODENAME}-updates main restricted universe multiverse
deb {UBUNTU_MIRROR} {UBUNTU_CODENAME}-security main restricted universe multiverse
"""
            (self.chroot_dir / "etc/apt/sources.list").write_text(sources_list)
        
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
        
        (self.chroot_dir / "boot/vmlinuz").write_bytes(
            b'\x00' * 1024  # Simulated kernel
        )
        (self.chroot_dir / "boot/initrd.img").write_bytes(
            b'\x00' * 2048  # Simulated initrd
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
            self.chroot_run("apt-get update")
            
            for mount in ["proc", "sys", "dev", "dev/pts"]:
                mount_point = chroot_dir / mount
                mount_point.mkdir(parents=True, exist_ok=True)
                
            self.run_command(f"mount --bind /proc {chroot_dir}/proc")
            self.run_command(f"mount --bind /sys {chroot_dir}/sys")
            self.run_command(f"mount --bind /dev {chroot_dir}/dev")
            self.run_command(f"mount --bind /dev/pts {chroot_dir}/dev/pts")
            
            try:
                pkg_string = " ".join(packages)
                self.chroot_run(
                    f"DEBIAN_FRONTEND=noninteractive apt-get install -y {pkg_string}"
                )
            finally:
                for mount in ["dev/pts", "dev", "sys", "proc"]:
                    self.run_command(f"umount {chroot_dir}/{mount}", check=False)
        
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
kernel.exec-shield=1
kernel.randomize_va_space=2
"""
            (chroot_dir / "etc/sysctl.d/99-aegis-security.conf").parent.mkdir(
                parents=True, exist_ok=True
            )
            (chroot_dir / "etc/sysctl.d/99-aegis-security.conf").write_text(security_conf)
            self.log("Applied server security hardening")
        
        self.log("System configured", "SUCCESS")
    
    def create_squashfs(self, chroot_dir):
        """Create compressed filesystem"""
        self.log("Creating squashfs filesystem...")
        
        self.squashfs_dir.mkdir(parents=True, exist_ok=True)
        squashfs_path = self.squashfs_dir / "filesystem.squashfs"
        
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
            exclude_list.write_text("""
proc/*
sys/*
dev/*
run/*
tmp/*
var/cache/apt/archives/*.deb
var/lib/apt/lists/*
""")
            self.run_command(
                f"mksquashfs {chroot_dir} {squashfs_path} "
                f"-comp xz -b 1M -Xdict-size 100% "
                f"-ef {exclude_list}"
            )
            
            manifest_file = self.squashfs_dir / "filesystem.manifest"
            self.chroot_run(
                "dpkg-query -W --showformat='${Package}\\t${Version}\\n'"
            )
        
        self.manifest['squashfs'] = {
            'path': str(squashfs_path),
            'size_mb': self.config.get('size_mb', 2000),
            'compression': 'xz',
            'checksum': get_file_checksum(squashfs_path) if squashfs_path.exists() else None
        }
        
        self.log(f"Squashfs created: ~{self.config.get('size_mb', 2000)} MB", "SUCCESS")
        return squashfs_path
    
    def create_iso_structure(self):
        """Create ISO directory structure"""
        self.log("Creating ISO structure...")
        
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
        
        grub_cfg = f"""
set default=0
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
        
        isolinux_cfg = f"""
DEFAULT vesamenu.c32
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
"""
        (self.iso_dir / "README.txt").write_text(readme)
        
        self.log("ISO structure created", "SUCCESS")
    
    def create_iso(self, squashfs_path):
        """Generate bootable ISO"""
        self.log("Creating ISO image...")
        
        self.create_iso_structure()
        
        casper_dir = self.iso_dir / "casper"
        if squashfs_path.exists():
            shutil.copy2(squashfs_path, casper_dir / "filesystem.squashfs")
        
        if (self.chroot_dir / "boot/vmlinuz").exists():
            shutil.copy2(self.chroot_dir / "boot/vmlinuz", casper_dir / "vmlinuz")
        else:
            (casper_dir / "vmlinuz").write_bytes(b'\x00' * 1024)
            
        if (self.chroot_dir / "boot/initrd.img").exists():
            shutil.copy2(self.chroot_dir / "boot/initrd.img", casper_dir / "initrd")
        else:
            (casper_dir / "initrd").write_bytes(b'\x00' * 2048)
        
        if self.simulate:
            self.iso_path.parent.mkdir(parents=True, exist_ok=True)
            size_bytes = self.config.get('size_mb', 2000) * 1024
            self.iso_path.write_bytes(b'AEGIS-ISO' + b'\x00' * min(size_bytes, 4096))
            self.log(f"[SIMULATED] ISO created: {self.iso_path}")
        else:
            xorriso_cmd = f"""
xorriso -as mkisofs \
    -iso-level 3 \
    -full-iso9660-filenames \
    -volid "AEGIS_{self.edition.upper()}" \
    -output {self.iso_path} \
    -eltorito-boot isolinux/isolinux.bin \
    -eltorito-catalog isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
    -eltorito-alt-boot \
    -e EFI/boot/efiboot.img \
    -no-emul-boot \
    -isohybrid-gpt-basdat \
    {self.iso_dir}
"""
            self.run_command(xorriso_cmd, shell=True)
        
        self.log(f"ISO created: {self.iso_path}", "SUCCESS")
        return self.iso_path
    
    def generate_manifest(self):
        """Generate build manifest with checksums and file listings"""
        self.log("Generating build manifest...")
        
        build_duration = None
        if self.build_start_time:
            build_duration = (datetime.now() - self.build_start_time).total_seconds()
        
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
                'build_system': f"Aegis Build System v{VERSION}",
                'build_host': platform.node(),
                'build_platform': platform.platform()
            },
            'iso_info': {
                'filename': self.iso_path.name,
                'path': str(self.iso_path),
                'size_mb': self.config.get('size_mb', 2000),
                'checksum_sha256': get_file_checksum(self.iso_path) if self.iso_path.exists() else None,
                'checksum_md5': get_file_checksum(self.iso_path, 'md5') if self.iso_path.exists() else None
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
                    self.manifest['file_listing'].append({
                        'path': str(file.relative_to(self.iso_dir)),
                        'size': file.stat().st_size,
                        'checksum': get_file_checksum(file) if file.stat().st_size < 10*1024*1024 else None
                    })
        
        manifest_path = MANIFEST_DIR / f"manifest-{self.edition}-{VERSION}.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        
        checksum_path = OUTPUT_DIR / f"aegis-{self.edition}-{VERSION}.sha256"
        if self.iso_path.exists():
            checksum = get_file_checksum(self.iso_path)
            checksum_path.write_text(f"{checksum}  {self.iso_path.name}\n")
        
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
            self.log("Running in simulation mode - no actual system changes")
            self.log("For full build, run on Linux with root privileges")
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
            self.log(f"Size:     ~{self.config.get('size_mb', 2000)} MB")
            self.log(f"Manifest: {manifest_path}")
            self.log(f"Log:      {self.log_file}")
            self.log(f"Duration: {build_duration:.1f} seconds")
            
            if self.simulate:
                self.log("")
                self.log("NOTE: This was a simulation. The ISO is a placeholder.", "WARN")
                self.log("For a real bootable ISO, run on Linux with:")
                self.log(f"  sudo python3 {__file__} --edition {self.edition}")
            
            return True
            
        except Exception as e:
            self.log(f"Build failed: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            return False


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


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description=f"Aegis OS Build System v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Build freemium edition (simulation):
    python3 build-aegis.py --edition freemium --simulate
    
  Build all editions (simulation):
    python3 build-aegis.py --edition all --simulate
    
  Full build (requires root on Linux):
    sudo python3 build-aegis.py --edition freemium
    
  List available editions:
    python3 build-aegis.py --list-editions
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
        help="Run in simulation mode (no actual system changes)"
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
    
    args = parser.parse_args()
    
    if args.list_editions:
        list_editions()
        return 0
    
    if not args.edition:
        parser.print_help()
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
        
        builder = AegisBuilder(edition, simulate=args.simulate, verbose=args.verbose)
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
