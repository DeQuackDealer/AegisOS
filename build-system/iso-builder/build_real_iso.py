#!/usr/bin/env python3
"""
Aegis OS Real ISO Builder
Creates actual bootable Linux ISOs with all Aegis tools.

Usage:
    python build_real_iso.py freemium    # Build Freemium edition
    python build_real_iso.py basic       # Build Basic edition
    python build_real_iso.py all         # Build all editions
"""

import os
import sys
import subprocess
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime

VERSION = "1.0.0"
WORK_DIR = Path(__file__).parent / "work"
OUTPUT_DIR = Path(__file__).parent / "output"
TOOLS_DIR = Path(__file__).parent.parent / "aegis-tools"

UBUNTU_BASE_URL = "https://cdimage.ubuntu.com/ubuntu-base/releases/24.04/release/ubuntu-base-24.04.1-base-amd64.tar.gz"
UBUNTU_BASE_FILE = "ubuntu-base-24.04.1-base-amd64.tar.gz"

EDITIONS = {
    "freemium": {
        "name": "Freemium",
        "description": "Free edition with basic features",
        "packages": ["xfce4", "xfce4-goodies", "firefox", "file-roller"],
        "tools": ["aegis-getting-started", "aegis-system-monitor-lite"]
    },
    "basic": {
        "name": "Basic",
        "description": "Essential productivity tools",
        "packages": ["xfce4", "xfce4-goodies", "firefox", "libreoffice", "vlc", "gimp"],
        "tools": ["aegis-getting-started", "aegis-system-care", "aegis-security-suite", 
                  "aegis-backup-suite", "aegis-media-suite"]
    },
    "gamer": {
        "name": "Gamer",
        "description": "Optimized for gaming",
        "packages": ["xfce4", "xfce4-goodies", "firefox", "steam-installer", "lutris"],
        "tools": ["aegis-game-center", "aegis-performance-tuner", "aegis-stream-deck",
                  "aegis-upscaler", "aegis-game-launcher"]
    },
    "workplace": {
        "name": "Workplace",
        "description": "Enterprise productivity",
        "packages": ["xfce4", "xfce4-goodies", "firefox", "libreoffice", "remmina", "evolution"],
        "tools": ["aegis-workspace-hub", "aegis-it-toolkit", "aegis-document-vault",
                  "aegis-collaboration", "aegis-productivity-tools"]
    },
    "ai_developer": {
        "name": "AI Developer",
        "description": "AI/ML development environment",
        "packages": ["xfce4", "xfce4-goodies", "firefox", "python3-pip", "python3-venv", 
                     "code", "jupyter-notebook"],
        "tools": ["aegis-ml-studio", "aegis-compute-stack", "aegis-model-hub",
                  "aegis-inference-engine", "aegis-data-science"]
    },
    "gamer_ai": {
        "name": "Gamer+AI",
        "description": "Gaming with AI enhancements",
        "packages": ["xfce4", "xfce4-goodies", "firefox", "steam-installer", "lutris",
                     "python3-pip"],
        "tools": ["aegis-game-center", "aegis-performance-tuner", "aegis-ai-gaming",
                  "aegis-neural-upscaling", "aegis-ai-streaming", "aegis-upscaler"]
    },
    "server": {
        "name": "Server",
        "description": "Server and infrastructure",
        "packages": ["openssh-server", "nginx", "docker.io", "fail2ban", "ufw"],
        "tools": ["aegis-server-manager", "aegis-security-daemon", "aegis-monitoring",
                  "aegis-backup-suite", "aegis-it-toolkit"]
    }
}


def run_cmd(cmd, check=True, capture=False, chroot_path=None):
    """Run a shell command."""
    if chroot_path:
        if isinstance(cmd, list):
            cmd = ["chroot", str(chroot_path)] + cmd
        else:
            cmd = f"chroot {chroot_path} {cmd}"
    
    print(f"  → {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    
    if capture:
        result = subprocess.run(cmd, shell=isinstance(cmd, str), 
                               capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result
    else:
        result = subprocess.run(cmd, shell=isinstance(cmd, str))
        if check and result.returncode != 0:
            sys.exit(1)
        return result


def download_base():
    """Download Ubuntu base if not present."""
    base_path = WORK_DIR / UBUNTU_BASE_FILE
    
    if base_path.exists():
        print(f"✓ Ubuntu base already downloaded: {base_path}")
        return base_path
    
    print(f"Downloading Ubuntu base ({UBUNTU_BASE_URL})...")
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    run_cmd(f"curl -L -o {base_path} {UBUNTU_BASE_URL}")
    print(f"✓ Downloaded: {base_path}")
    return base_path


def setup_base_chroot():
    """Setup the base chroot environment."""
    chroot_path = WORK_DIR / "chroot-base"
    
    if chroot_path.exists() and (chroot_path / "bin" / "bash").exists():
        print(f"✓ Base chroot already exists: {chroot_path}")
        return chroot_path
    
    print("Setting up base chroot...")
    
    if chroot_path.exists():
        shutil.rmtree(chroot_path)
    chroot_path.mkdir(parents=True)
    
    base_tar = WORK_DIR / UBUNTU_BASE_FILE
    run_cmd(f"tar -xzf {base_tar} -C {chroot_path}")
    
    resolv_src = Path("/etc/resolv.conf")
    resolv_dst = chroot_path / "etc" / "resolv.conf"
    if resolv_src.exists():
        shutil.copy(resolv_src, resolv_dst)
    
    print("✓ Base chroot extracted")
    return chroot_path


def mount_chroot(chroot_path):
    """Mount necessary filesystems for chroot."""
    mounts = [
        ("proc", "proc", "proc"),
        ("sysfs", "sys", "sysfs"),
        ("devtmpfs", "dev", "devtmpfs"),
        ("devpts", "dev/pts", "devpts"),
    ]
    
    for fstype, target, fs in mounts:
        target_path = chroot_path / target
        target_path.mkdir(parents=True, exist_ok=True)
        result = run_cmd(f"mountpoint -q {target_path}", check=False, capture=True)
        if result.returncode != 0:
            run_cmd(f"mount -t {fs} {fstype} {target_path}", check=False)


def unmount_chroot(chroot_path):
    """Unmount chroot filesystems."""
    for target in ["dev/pts", "dev", "sys", "proc"]:
        target_path = chroot_path / target
        run_cmd(f"umount -lf {target_path}", check=False, capture=True)


def install_base_packages(chroot_path):
    """Install kernel and essential packages in chroot."""
    print("Installing base packages in chroot...")
    
    mount_chroot(chroot_path)
    
    try:
        run_cmd("apt-get update", chroot_path=chroot_path)
        
        base_pkgs = [
            "linux-generic",
            "live-boot",
            "systemd-sysv",
            "dbus",
            "network-manager",
            "sudo",
            "locales",
            "console-setup",
        ]
        
        run_cmd(f"apt-get install -y --no-install-recommends {' '.join(base_pkgs)}", 
                chroot_path=chroot_path)
        
        run_cmd("apt-get clean", chroot_path=chroot_path)
        
        print("✓ Base packages installed")
        
    finally:
        unmount_chroot(chroot_path)


def create_edition_chroot(edition_key):
    """Create edition-specific chroot by cloning base."""
    edition = EDITIONS[edition_key]
    edition_chroot = WORK_DIR / f"chroot-{edition_key}"
    base_chroot = WORK_DIR / "chroot-base"
    
    print(f"\n=== Building {edition['name']} Edition ===")
    
    if edition_chroot.exists():
        print(f"Removing old chroot: {edition_chroot}")
        shutil.rmtree(edition_chroot)
    
    print(f"Cloning base chroot to {edition_chroot}...")
    shutil.copytree(base_chroot, edition_chroot, symlinks=True)
    
    mount_chroot(edition_chroot)
    
    try:
        if edition.get("packages"):
            print(f"Installing edition packages: {', '.join(edition['packages'])}")
            run_cmd("apt-get update", chroot_path=edition_chroot)
            run_cmd(f"apt-get install -y --no-install-recommends {' '.join(edition['packages'])}", 
                    chroot_path=edition_chroot)
        
        tools_dest = edition_chroot / "usr" / "local" / "bin"
        tools_dest.mkdir(parents=True, exist_ok=True)
        
        for tool in edition.get("tools", []):
            tool_src = TOOLS_DIR / f"{tool}.py"
            if tool_src.exists():
                print(f"  Installing tool: {tool}")
                shutil.copy(tool_src, tools_dest / tool)
                (tools_dest / tool).chmod(0o755)
        
        etc_path = edition_chroot / "etc"
        with open(etc_path / "hostname", "w") as f:
            f.write(f"aegis-{edition_key}\n")
        
        with open(etc_path / "os-release", "w") as f:
            f.write(f'''NAME="Aegis OS"
VERSION="{VERSION}"
ID=aegis
ID_LIKE=ubuntu
VERSION_ID="{VERSION}"
PRETTY_NAME="Aegis OS {edition['name']} {VERSION}"
HOME_URL="https://aegis-os.com"
''')
        
        run_cmd("apt-get clean", chroot_path=edition_chroot)
        run_cmd("rm -rf /tmp/* /var/tmp/*", chroot_path=edition_chroot)
        
        print(f"✓ {edition['name']} chroot ready")
        
    finally:
        unmount_chroot(edition_chroot)
    
    return edition_chroot


def create_squashfs(edition_key, chroot_path):
    """Create squashfs from chroot."""
    print(f"Creating squashfs for {edition_key}...")
    
    image_dir = WORK_DIR / f"image-{edition_key}"
    image_dir.mkdir(parents=True, exist_ok=True)
    
    live_dir = image_dir / "casper"
    live_dir.mkdir(exist_ok=True)
    
    squashfs_path = live_dir / "filesystem.squashfs"
    if squashfs_path.exists():
        squashfs_path.unlink()
    
    run_cmd(f"mksquashfs {chroot_path} {squashfs_path} -comp xz -noappend")
    
    kernel_src = list((chroot_path / "boot").glob("vmlinuz-*"))
    initrd_src = list((chroot_path / "boot").glob("initrd.img-*"))
    
    if kernel_src:
        shutil.copy(kernel_src[0], live_dir / "vmlinuz")
    if initrd_src:
        shutil.copy(initrd_src[0], live_dir / "initrd")
    
    print(f"✓ Squashfs created: {squashfs_path}")
    return image_dir


def setup_bootloader(image_dir, edition_key):
    """Setup isolinux bootloader."""
    edition = EDITIONS[edition_key]
    
    isolinux_dir = image_dir / "isolinux"
    isolinux_dir.mkdir(exist_ok=True)
    
    isolinux_files = [
        "/usr/lib/ISOLINUX/isolinux.bin",
        "/usr/lib/syslinux/modules/bios/ldlinux.c32",
        "/usr/lib/syslinux/modules/bios/menu.c32",
        "/usr/lib/syslinux/modules/bios/libutil.c32",
    ]
    
    for src in isolinux_files:
        src_path = Path(src)
        if src_path.exists():
            shutil.copy(src_path, isolinux_dir / src_path.name)
    
    isolinux_cfg = f'''UI menu.c32
PROMPT 0
MENU TITLE Aegis OS {edition['name']} {VERSION}
TIMEOUT 100

LABEL live
    MENU LABEL ^Start Aegis OS {edition['name']}
    MENU DEFAULT
    KERNEL /casper/vmlinuz
    APPEND initrd=/casper/initrd boot=casper quiet splash ---

LABEL live-safe
    MENU LABEL Start Aegis OS (Safe Mode)
    KERNEL /casper/vmlinuz
    APPEND initrd=/casper/initrd boot=casper noapic noapm nodma nomce nolapic nomodeset ---
'''
    
    with open(isolinux_dir / "isolinux.cfg", "w") as f:
        f.write(isolinux_cfg)
    
    print(f"✓ Bootloader configured")


def create_iso(edition_key, image_dir):
    """Create the final ISO image."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    iso_name = f"aegis-{edition_key}-{VERSION}.iso"
    iso_path = OUTPUT_DIR / iso_name
    
    print(f"Creating ISO: {iso_path}")
    
    isohdpfx = Path("/usr/lib/ISOLINUX/isohdpfx.bin")
    
    if isohdpfx.exists():
        cmd = f'''xorriso -as mkisofs \
            -iso-level 3 \
            -full-iso9660-filenames \
            -volid "AEGIS_{edition_key.upper()}" \
            -output "{iso_path}" \
            -isohybrid-mbr {isohdpfx} \
            -eltorito-boot isolinux/isolinux.bin \
            -no-emul-boot \
            -boot-load-size 4 \
            -boot-info-table \
            --eltorito-catalog isolinux/boot.cat \
            "{image_dir}"'''
    else:
        cmd = f'''xorriso -as mkisofs \
            -iso-level 3 \
            -full-iso9660-filenames \
            -volid "AEGIS_{edition_key.upper()}" \
            -output "{iso_path}" \
            -eltorito-boot isolinux/isolinux.bin \
            -no-emul-boot \
            -boot-load-size 4 \
            -boot-info-table \
            "{image_dir}"'''
    
    run_cmd(cmd)
    
    size_mb = iso_path.stat().st_size / (1024 * 1024)
    print(f"✓ ISO created: {iso_path} ({size_mb:.1f} MB)")
    
    return iso_path


def build_edition(edition_key):
    """Build a complete ISO for an edition."""
    print(f"\n{'='*60}")
    print(f"BUILDING AEGIS OS {EDITIONS[edition_key]['name'].upper()} EDITION")
    print(f"{'='*60}\n")
    
    base_tar = download_base()
    
    base_chroot = setup_base_chroot()
    
    if not (base_chroot / "boot").exists() or not list((base_chroot / "boot").glob("vmlinuz-*")):
        install_base_packages(base_chroot)
    
    edition_chroot = create_edition_chroot(edition_key)
    
    image_dir = create_squashfs(edition_key, edition_chroot)
    
    setup_bootloader(image_dir, edition_key)
    
    iso_path = create_iso(edition_key, image_dir)
    
    print(f"\n{'='*60}")
    print(f"BUILD COMPLETE: {iso_path}")
    print(f"{'='*60}\n")
    
    return iso_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python build_real_iso.py <edition|all>")
        print("\nAvailable editions:")
        for key, ed in EDITIONS.items():
            print(f"  {key:15} - {ed['name']} ({ed['description']})")
        print("\n  all             - Build all editions")
        sys.exit(1)
    
    edition = sys.argv[1].lower()
    
    if edition == "all":
        for key in EDITIONS:
            build_edition(key)
    elif edition in EDITIONS:
        build_edition(edition)
    else:
        print(f"Unknown edition: {edition}")
        print(f"Available: {', '.join(EDITIONS.keys())}, all")
        sys.exit(1)


if __name__ == "__main__":
    main()
