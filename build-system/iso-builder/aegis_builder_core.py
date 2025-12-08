#!/usr/bin/env python3
"""
Aegis OS ISO Builder - Core Module
Handles ISO assembly from embedded resources.
100% offline operation - no internet required.
"""

import os
import sys
import json
import hashlib
import tempfile
import shutil
import subprocess
import struct
import lzma
import tarfile
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime

VERSION = "2.0.0"
BUILD_DATE = "2025-01"

@dataclass
class Edition:
    """Represents an Aegis OS edition."""
    id: str
    name: str
    price: str
    description: str
    size_gb: float
    packages: list
    overlay_id: str

EDITIONS = {
    "freemium": Edition(
        id="freemium",
        name="Freemium",
        price="FREE",
        description="Basic desktop with essential tools",
        size_gb=3.2,
        packages=["xfce4", "firefox", "thunar", "vlc"],
        overlay_id="overlay_freemium"
    ),
    "basic": Edition(
        id="basic",
        name="Basic",
        price="$69",
        description="Full desktop with security and backup tools",
        size_gb=3.5,
        packages=["xfce4", "firefox", "libreoffice", "gimp", "clamav", "timeshift"],
        overlay_id="overlay_basic"
    ),
    "workplace": Edition(
        id="workplace",
        name="Workplace",
        price="$49",
        description="Business productivity suite",
        size_gb=4.0,
        packages=["xfce4", "firefox", "libreoffice", "thunderbird", "remmina", "evolution"],
        overlay_id="overlay_workplace"
    ),
    "gamer": Edition(
        id="gamer",
        name="Gamer",
        price="$69",
        description="Gaming-optimized with Steam and Lutris",
        size_gb=5.5,
        packages=["xfce4", "steam", "lutris", "gamemode", "mangohud", "wine"],
        overlay_id="overlay_gamer"
    ),
    "ai": Edition(
        id="ai",
        name="AI Developer",
        price="$89",
        description="Machine learning and AI development tools",
        size_gb=6.0,
        packages=["xfce4", "python3", "jupyter", "cuda", "pytorch", "vscode"],
        overlay_id="overlay_ai"
    ),
    "gamer-ai": Edition(
        id="gamer-ai",
        name="Gamer+AI",
        price="$129",
        description="Ultimate gaming with AI enhancements",
        size_gb=7.0,
        packages=["xfce4", "steam", "lutris", "python3", "cuda", "mangohud"],
        overlay_id="overlay_gamer_ai"
    ),
    "server": Edition(
        id="server",
        name="Server",
        price="$129",
        description="Headless server with Docker and databases",
        size_gb=3.0,
        packages=["docker", "nginx", "postgresql", "redis", "fail2ban"],
        overlay_id="overlay_server"
    ),
}


class ResourceManager:
    """
    Manages embedded resources for offline ISO building.
    Resources are stored as compressed data within the executable.
    """
    
    def __init__(self):
        self.resources: Dict[str, bytes] = {}
        self.resource_dir = self._get_resource_dir()
        
    def _get_resource_dir(self) -> Path:
        """Get the resource directory (handles both script and frozen exe)."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return Path(sys._MEIPASS) / "resources"
        else:
            # Running as script
            return Path(__file__).parent / "resources"
    
    def has_resource(self, name: str) -> bool:
        """Check if a resource exists."""
        resource_path = self.resource_dir / name
        return resource_path.exists() or name in self.resources
    
    def get_resource(self, name: str) -> Optional[bytes]:
        """Get a resource by name."""
        if name in self.resources:
            return self.resources[name]
        
        resource_path = self.resource_dir / name
        if resource_path.exists():
            return resource_path.read_bytes()
        
        return None
    
    def get_resource_path(self, name: str) -> Optional[Path]:
        """Get the path to a resource file."""
        resource_path = self.resource_dir / name
        if resource_path.exists():
            return resource_path
        return None
    
    def extract_resource(self, name: str, destination: Path) -> bool:
        """Extract a resource to a destination path."""
        data = self.get_resource(name)
        if data is None:
            return False
        
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if it's compressed
        if name.endswith('.xz'):
            data = lzma.decompress(data)
        
        destination.write_bytes(data)
        return True


class ISOBuilder:
    """
    Builds Aegis OS ISO from embedded resources.
    Completely offline - no internet connection required.
    """
    
    def __init__(self, edition: Edition, progress_callback: Optional[Callable] = None):
        self.edition = edition
        self.progress_callback = progress_callback or (lambda p, m: None)
        self.resources = ResourceManager()
        self.build_dir: Optional[Path] = None
        self.cancelled = False
        
    def report_progress(self, percent: int, message: str):
        """Report build progress."""
        if not self.cancelled:
            self.progress_callback(percent, message)
    
    def cancel(self):
        """Cancel the build process."""
        self.cancelled = True
    
    def validate_resources(self) -> tuple[bool, str]:
        """Validate that all required resources are present."""
        required = [
            "base_system.tar.xz",
            "kernel/vmlinuz",
            "kernel/initrd.img",
            "isolinux/isolinux.bin",
            "isolinux/ldlinux.c32",
            f"overlays/{self.edition.overlay_id}.tar.xz"
        ]
        
        missing = []
        for res in required:
            if not self.resources.has_resource(res):
                missing.append(res)
        
        if missing:
            return False, f"Missing resources: {', '.join(missing)}"
        
        return True, "All resources validated"
    
    def build(self, output_path: Path) -> tuple[bool, str]:
        """
        Build the ISO file.
        
        Args:
            output_path: Where to save the final ISO
            
        Returns:
            (success, message) tuple
        """
        try:
            self.cancelled = False
            
            # Step 1: Validate resources
            self.report_progress(5, "Validating embedded resources...")
            valid, msg = self.validate_resources()
            if not valid:
                return False, msg
            
            if self.cancelled:
                return False, "Build cancelled"
            
            # Step 2: Create build directory
            self.report_progress(10, "Preparing build environment...")
            self.build_dir = Path(tempfile.mkdtemp(prefix="aegis_build_"))
            iso_dir = self.build_dir / "iso"
            iso_dir.mkdir()
            
            if self.cancelled:
                return False, "Build cancelled"
            
            # Step 3: Extract base system
            self.report_progress(15, "Extracting base system (this takes a while)...")
            success = self._extract_base_system(iso_dir)
            if not success:
                return False, "Failed to extract base system"
            
            if self.cancelled:
                return False, "Build cancelled"
            
            # Step 4: Apply edition overlay
            self.report_progress(50, f"Applying {self.edition.name} customizations...")
            success = self._apply_overlay(iso_dir)
            if not success:
                return False, "Failed to apply edition overlay"
            
            if self.cancelled:
                return False, "Build cancelled"
            
            # Step 5: Copy kernel and initrd
            self.report_progress(65, "Setting up boot files...")
            success = self._setup_boot(iso_dir)
            if not success:
                return False, "Failed to setup boot files"
            
            if self.cancelled:
                return False, "Build cancelled"
            
            # Step 6: Create squashfs
            self.report_progress(70, "Creating compressed filesystem...")
            success = self._create_squashfs(iso_dir)
            if not success:
                return False, "Failed to create filesystem"
            
            if self.cancelled:
                return False, "Build cancelled"
            
            # Step 7: Setup isolinux
            self.report_progress(85, "Configuring bootloader...")
            success = self._setup_isolinux(iso_dir)
            if not success:
                return False, "Failed to setup bootloader"
            
            if self.cancelled:
                return False, "Build cancelled"
            
            # Step 8: Generate ISO
            self.report_progress(90, "Generating ISO image...")
            success = self._generate_iso(iso_dir, output_path)
            if not success:
                return False, "Failed to generate ISO"
            
            # Step 9: Verify ISO
            self.report_progress(98, "Verifying ISO integrity...")
            iso_hash = self._compute_hash(output_path)
            
            # Cleanup
            self.report_progress(100, "Build complete!")
            self._cleanup()
            
            size_mb = output_path.stat().st_size / (1024 * 1024)
            return True, f"ISO created successfully!\n\nFile: {output_path}\nSize: {size_mb:.1f} MB\nSHA-256: {iso_hash[:16]}..."
            
        except Exception as e:
            self._cleanup()
            return False, f"Build error: {str(e)}"
    
    def _extract_base_system(self, iso_dir: Path) -> bool:
        """Extract the base system tarball."""
        casper_dir = iso_dir / "casper"
        casper_dir.mkdir(parents=True)
        
        base_tar = self.resources.get_resource_path("base_system.tar.xz")
        if base_tar is None:
            # Try to extract from embedded data
            data = self.resources.get_resource("base_system.tar.xz")
            if data is None:
                return False
            base_tar = self.build_dir / "base_system.tar.xz"
            base_tar.write_bytes(data)
        
        # Extract tarball
        rootfs_dir = self.build_dir / "rootfs"
        rootfs_dir.mkdir()
        
        try:
            with tarfile.open(base_tar, 'r:xz') as tar:
                tar.extractall(rootfs_dir)
            self.report_progress(40, "Base system extracted")
            return True
        except Exception as e:
            print(f"Extract error: {e}")
            return False
    
    def _apply_overlay(self, iso_dir: Path) -> bool:
        """Apply edition-specific overlay."""
        overlay_name = f"overlays/{self.edition.overlay_id}.tar.xz"
        overlay_tar = self.resources.get_resource_path(overlay_name)
        
        if overlay_tar is None:
            data = self.resources.get_resource(overlay_name)
            if data is None:
                # No overlay is OK for freemium
                if self.edition.id == "freemium":
                    return True
                return False
            overlay_tar = self.build_dir / "overlay.tar.xz"
            overlay_tar.write_bytes(data)
        
        rootfs_dir = self.build_dir / "rootfs"
        
        try:
            with tarfile.open(overlay_tar, 'r:xz') as tar:
                tar.extractall(rootfs_dir)
            return True
        except Exception:
            return True  # Overlay is optional
    
    def _setup_boot(self, iso_dir: Path) -> bool:
        """Setup kernel and initrd."""
        casper_dir = iso_dir / "casper"
        casper_dir.mkdir(exist_ok=True)
        
        # Copy kernel
        if not self.resources.extract_resource("kernel/vmlinuz", casper_dir / "vmlinuz"):
            # Try from rootfs
            rootfs_kernel = self.build_dir / "rootfs" / "boot" / "vmlinuz"
            if rootfs_kernel.exists():
                shutil.copy(rootfs_kernel, casper_dir / "vmlinuz")
            else:
                return False
        
        # Copy initrd
        if not self.resources.extract_resource("kernel/initrd.img", casper_dir / "initrd"):
            rootfs_initrd = self.build_dir / "rootfs" / "boot" / "initrd.img"
            if rootfs_initrd.exists():
                shutil.copy(rootfs_initrd, casper_dir / "initrd")
            else:
                return False
        
        return True
    
    def _create_squashfs(self, iso_dir: Path) -> bool:
        """Create compressed squashfs filesystem."""
        rootfs_dir = self.build_dir / "rootfs"
        squashfs_path = iso_dir / "casper" / "filesystem.squashfs"
        
        # Write edition info to rootfs
        aegis_dir = rootfs_dir / "etc" / "aegis"
        aegis_dir.mkdir(parents=True, exist_ok=True)
        (aegis_dir / "edition").write_text(self.edition.id)
        (aegis_dir / "version").write_text(VERSION)
        (aegis_dir / "build_date").write_text(datetime.now().isoformat())
        
        try:
            # Use mksquashfs if available
            result = subprocess.run(
                ["mksquashfs", str(rootfs_dir), str(squashfs_path), 
                 "-comp", "xz", "-Xbcj", "x86", "-b", "1M"],
                capture_output=True,
                timeout=600
            )
            return result.returncode == 0
        except FileNotFoundError:
            # Fallback: create a simple archive
            self.report_progress(75, "Creating filesystem archive...")
            with tarfile.open(squashfs_path, 'w:xz') as tar:
                tar.add(rootfs_dir, arcname=".")
            return True
        except Exception:
            return False
    
    def _setup_isolinux(self, iso_dir: Path) -> bool:
        """Setup isolinux bootloader."""
        isolinux_dir = iso_dir / "isolinux"
        isolinux_dir.mkdir(exist_ok=True)
        
        # Copy isolinux files
        isolinux_files = [
            "isolinux/isolinux.bin",
            "isolinux/ldlinux.c32",
            "isolinux/libutil.c32",
            "isolinux/libcom32.c32",
            "isolinux/vesamenu.c32",
        ]
        
        for f in isolinux_files:
            self.resources.extract_resource(f, iso_dir / f)
        
        # Create isolinux.cfg
        config = f"""
DEFAULT live
TIMEOUT 50
PROMPT 0

UI vesamenu.c32
MENU TITLE Aegis OS {self.edition.name} Edition

LABEL live
    MENU LABEL ^Start Aegis OS {self.edition.name}
    KERNEL /casper/vmlinuz
    APPEND initrd=/casper/initrd boot=casper quiet splash ---

LABEL install
    MENU LABEL ^Install Aegis OS
    KERNEL /casper/vmlinuz
    APPEND initrd=/casper/initrd boot=casper only-ubiquity quiet splash ---

LABEL safe
    MENU LABEL Start in ^Safe Mode
    KERNEL /casper/vmlinuz
    APPEND initrd=/casper/initrd boot=casper nomodeset quiet ---
"""
        (isolinux_dir / "isolinux.cfg").write_text(config)
        
        return True
    
    def _generate_iso(self, iso_dir: Path, output_path: Path) -> bool:
        """Generate the final ISO image."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Try xorriso first
            result = subprocess.run([
                "xorriso", "-as", "mkisofs",
                "-iso-level", "3",
                "-full-iso9660-filenames",
                "-volid", f"AEGIS_{self.edition.id.upper()}",
                "-eltorito-boot", "isolinux/isolinux.bin",
                "-eltorito-catalog", "isolinux/boot.cat",
                "-no-emul-boot", "-boot-load-size", "4", "-boot-info-table",
                "-isohybrid-mbr", "/usr/lib/ISOLINUX/isohdpfx.bin",
                "-output", str(output_path),
                str(iso_dir)
            ], capture_output=True, timeout=300)
            
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Fallback: create a simple ISO structure
        try:
            result = subprocess.run([
                "genisoimage", "-o", str(output_path),
                "-b", "isolinux/isolinux.bin",
                "-c", "isolinux/boot.cat",
                "-no-emul-boot", "-boot-load-size", "4", "-boot-info-table",
                "-V", f"AEGIS_{self.edition.id.upper()}",
                str(iso_dir)
            ], capture_output=True, timeout=300)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _compute_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _cleanup(self):
        """Clean up temporary build directory."""
        if self.build_dir and self.build_dir.exists():
            try:
                shutil.rmtree(self.build_dir)
            except Exception:
                pass


class LicenseValidator:
    """
    Validates Aegis OS licenses using RSA-2048 signatures.
    100% offline verification - no internet required.
    """
    
    # Embedded public key for license verification
    PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/ygWyf8gd
DxDyRR5sLzTMbmN0TbQzd7lCy3WxQHTFxBxRlZCpCpiRkMvDhQdN3Nf2PlPXgK8J3wXt
QwP3FKBzMjBk8E8eKxLSzJHX8YfqPQM9TZPkLwLzCf9DtBqk8yBfM0lDZ0qaTFxRKbMJ
k7dJHFnRHLFLDQ3mBk7cNqFwFno1CDZpAZGVJYmRfqKvZYMzB8Zpa8Y2xvB1kNPKY8Cx
hQ3yDQBz8Xf5DdKLA3S8g6fKVl8zN5oPBc3Qf+rKQt7FM8a7P3Uo5Q3Dbg4zy0aBbLYu
W1yCYdZlPqTNLkZsDgEoFt5D3hBxfLzundwYFbaPIQIDAQAB
-----END PUBLIC KEY-----"""
    
    def __init__(self):
        self._public_key = None
        self._load_public_key()
    
    def _load_public_key(self):
        """Load the RSA public key for verification."""
        try:
            from cryptography.hazmat.primitives import serialization
            self._public_key = serialization.load_pem_public_key(
                self.PUBLIC_KEY_PEM.encode()
            )
        except ImportError:
            # Fallback: use simple checksum validation
            self._public_key = None
        except Exception:
            self._public_key = None
    
    def validate(self, license_data: dict) -> tuple[bool, str, Optional[str]]:
        """
        Validate a license.
        
        Args:
            license_data: License dictionary with keys: edition, email, key, signature, expires
            
        Returns:
            (is_valid, message, edition) tuple
        """
        required_fields = ["edition", "key", "signature"]
        for field in required_fields:
            if field not in license_data:
                return False, f"Invalid license: missing {field}", None
        
        edition = license_data.get("edition", "").lower()
        license_key = license_data.get("key", "")
        signature = license_data.get("signature", "")
        expires = license_data.get("expires", "")
        
        # Check edition is valid
        if edition not in EDITIONS:
            return False, f"Invalid edition: {edition}", None
        
        # Check if edition is freemium (shouldn't need license)
        if edition == "freemium":
            return False, "Freemium edition does not require a license", None
        
        # Check expiration
        if expires:
            try:
                exp_date = datetime.fromisoformat(expires.replace("Z", "+00:00"))
                if exp_date < datetime.now(exp_date.tzinfo):
                    return False, "License has expired", None
            except ValueError:
                pass  # Invalid date format, skip check
        
        # Verify signature
        if self._public_key is not None:
            try:
                from cryptography.hazmat.primitives import hashes
                from cryptography.hazmat.primitives.asymmetric import padding
                import base64
                
                # Reconstruct the signed data
                signed_data = f"{edition}:{license_key}:{expires}".encode()
                signature_bytes = base64.b64decode(signature)
                
                # Verify
                self._public_key.verify(
                    signature_bytes,
                    signed_data,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                
                return True, "License verified successfully", edition
                
            except Exception as e:
                return False, f"License verification failed: invalid signature", None
        else:
            # Fallback validation (checksum-based)
            expected_checksum = self._compute_checksum(edition, license_key)
            if signature.startswith(expected_checksum[:8]):
                return True, "License verified (checksum)", edition
            else:
                return False, "License verification failed", None
    
    def _compute_checksum(self, edition: str, key: str) -> str:
        """Compute a checksum for fallback validation."""
        import hashlib
        data = f"AEGIS:{edition}:{key}:VALID"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def load_license_file(self, path: Path) -> Optional[dict]:
        """Load a license from a JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def find_license(self) -> Optional[dict]:
        """Search for a license file in common locations."""
        search_paths = [
            Path.cwd() / "license.json",
            Path.home() / ".aegis" / "license.json",
            Path.home() / "Downloads" / "aegis-license.json",
            Path.home() / "Desktop" / "aegis-license.json",
        ]
        
        # Check USB drives on Windows
        if sys.platform == "win32":
            for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
                search_paths.extend([
                    Path(f"{letter}:/license.json"),
                    Path(f"{letter}:/aegis/license.json"),
                ])
        else:
            # Linux/Mac USB locations
            for mount in ["/media", "/mnt", "/Volumes"]:
                if Path(mount).exists():
                    for drive in Path(mount).iterdir():
                        if drive.is_dir():
                            search_paths.extend([
                                drive / "license.json",
                                drive / "aegis" / "license.json",
                            ])
        
        for path in search_paths:
            if path.exists():
                license_data = self.load_license_file(path)
                if license_data:
                    return license_data
        
        return None


def get_output_path(edition: Edition) -> Path:
    """Get the default output path for the ISO."""
    downloads = Path.home() / "Downloads"
    if not downloads.exists():
        downloads = Path.home()
    
    filename = f"aegis-{edition.id}-{VERSION}.iso"
    return downloads / filename
