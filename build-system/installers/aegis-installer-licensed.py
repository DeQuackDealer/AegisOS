#!/usr/bin/env python3
"""
Aegis OS Licensed Edition Installer
Offline installer with download fallback and RSA-2048 license verification
Works with bundled ISO files and license files, with option to download from Aegis servers
"""

import os
import sys
import hashlib
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import time
import webbrowser
import json
import base64
import binascii
from datetime import datetime
from typing import Optional, Tuple, Any
import urllib.request
import urllib.error
import ssl
import socket

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.backends import default_backend
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    hashes = None
    serialization = None
    padding = None
    default_backend = None
    InvalidSignature = Exception

VERSION = "2.1.0"
APP_NAME = "Aegis OS Licensed Installer"

ISO_DOWNLOAD_BASE_URL = "https://download.aegis-os.com/iso/licensed"
ISO_DOWNLOAD_FALLBACK_URL = "https://mirror.aegis-os.com/iso/licensed"
DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "AegisOS"

EDITIONS = {
    "basic": {
        "name": "Aegis OS Basic",
        "prefix": "BSIC",
        "price": "$69 Lifetime",
        "size_gb": 3.5,
        "features": [
            "All Freemium Features",
            "500+ Professional Apps",
            "Development Tools & IDEs", 
            "Aegis DeskLink Pro",
            "24/7 Email Support"
        ],
        "iso_filename": "aegis-basic.iso"
    },
    "workplace": {
        "name": "Aegis OS Workplace",
        "prefix": "WORK",
        "price": "$49 Lifetime",
        "size_gb": 4.0,
        "features": [
            "All Basic Features",
            "Office 365 Compatibility",
            "Team Collaboration",
            "Remote Desktop",
            "Enterprise Security"
        ],
        "iso_filename": "aegis-workplace.iso"
    },
    "gamer": {
        "name": "Aegis OS Gamer",
        "prefix": "GAME",
        "price": "$69 Lifetime",
        "size_gb": 4.5,
        "features": [
            "All Basic Features",
            "Steam + Proton Gaming",
            "GPU Optimizations",
            "Low-latency Kernel",
            "Gaming Support"
        ],
        "iso_filename": "aegis-gamer.iso"
    },
    "aidev": {
        "name": "Aegis OS AI Developer",
        "prefix": "AIDV",
        "price": "$89 Lifetime",
        "size_gb": 6.0,
        "features": [
            "All Basic Features",
            "PyTorch & TensorFlow",
            "CUDA Toolkit",
            "Jupyter Notebooks",
            "Developer Support"
        ],
        "iso_filename": "aegis-aidev.iso"
    },
    "gamer_ai": {
        "name": "Aegis OS Gamer + AI",
        "prefix": "GMAI",
        "price": "$129 Lifetime",
        "size_gb": 8.0,
        "features": [
            "All Gamer Features",
            "All AI Dev Features",
            "AI Game Optimization",
            "Neural Upscaling",
            "Priority Support"
        ],
        "iso_filename": "aegis-gamer-ai.iso"
    },
    "server": {
        "name": "Aegis OS Server",
        "prefix": "SERV",
        "price": "$129 Lifetime",
        "size_gb": 3.0,
        "features": [
            "Headless Server Mode",
            "Docker & Kubernetes",
            "Database Servers",
            "Monitoring Stack",
            "Enterprise SLA"
        ],
        "iso_filename": "aegis-server.iso"
    }
}

RSA_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5PW/lQrfv0gW4Ozoefdz
SprOqysQQOc7Fta+f9i3ObOTlK93KLWrVa7YXCFTWfxUuO36UFYHmkjiiVfzmzzH
OI8Gdnood9ar/JF2C7OheaHARGq5XJdYSdmUdFz+K+PX1kqjhYmLm4neG0ftgWxX
TOewAJ3yRh/u9t3Br9gU1yhv8PhbeFTUMMsqXvdGhmRbNnIoAg8YrMt49cYVepYw
spMA41XuX9BsEbfAwqo85Yo6T75TYrTbIc++Un6oVaDklAcWLxtjUO/dQ6nmtp6F
EHPRcn3iBRNMa485Azo9HWaQ5oW1P3jYmBaKKMpmnKfSjs8vMCXBP6mi6KOLGLFO
FQIDAQAB
-----END PUBLIC KEY-----"""


class OfflineISOLocator:
    """Handles offline ISO detection from local sources"""
    
    @staticmethod
    def get_search_paths():
        """Get all paths to search for ISO files"""
        paths = []
        
        script_dir = Path(__file__).parent
        paths.append(script_dir)
        paths.append(script_dir / "iso")
        paths.append(script_dir.parent / "iso")
        paths.append(script_dir.parent.parent / "iso")
        
        paths.append(Path.cwd())
        paths.append(Path.cwd() / "iso")
        
        paths.append(Path.home() / "Downloads")
        paths.append(Path.home() / "Desktop")
        paths.append(Path.home() / ".aegis" / "iso")
        
        usb_paths = OfflineISOLocator.get_usb_mount_points()
        for usb in usb_paths:
            paths.append(Path(usb))
            paths.append(Path(usb) / "aegis")
            paths.append(Path(usb) / "iso")
            paths.append(Path(usb) / "AegisOS")
        
        return [p for p in paths if p.exists()]
    
    @staticmethod
    def get_usb_mount_points():
        """Detect USB drive mount points across platforms"""
        usb_paths = []
        
        if sys.platform == "win32":
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        import ctypes
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                        if drive_type == 2:
                            usb_paths.append(drive)
                    except:
                        pass
        
        elif sys.platform == "darwin":
            volumes = Path("/Volumes")
            if volumes.exists():
                for vol in volumes.iterdir():
                    if vol.is_dir() and vol.name != "Macintosh HD":
                        usb_paths.append(str(vol))
        
        else:
            media_paths = [
                Path("/media") / os.getenv("USER", ""),
                Path("/mnt"),
                Path("/run/media") / os.getenv("USER", "")
            ]
            for media in media_paths:
                if media.exists():
                    for mount in media.iterdir():
                        if mount.is_dir():
                            usb_paths.append(str(mount))
        
        return usb_paths
    
    @staticmethod
    def load_manifest(search_paths):
        """Load manifest.json from any search path"""
        for path in search_paths:
            manifest_file = Path(path) / "manifest.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file, 'r') as f:
                        return json.load(f), str(manifest_file)
                except (json.JSONDecodeError, IOError):
                    continue
        return None, None
    
    @staticmethod
    def find_iso(edition_id):
        """
        Find ISO file for the specified edition
        Returns: (iso_path, manifest_data, source_description)
        """
        edition = EDITIONS.get(edition_id)
        if not edition:
            return None, None, None
        
        search_paths = OfflineISOLocator.get_search_paths()
        
        manifest, manifest_path = OfflineISOLocator.load_manifest(search_paths)
        expected_sha256 = None
        expected_filename = edition.get("iso_filename")
        
        if manifest and "editions" in manifest:
            edition_data = manifest["editions"].get(edition_id, {})
            if edition_data.get("filename"):
                expected_filename = edition_data["filename"]
            expected_sha256 = edition_data.get("sha256")
        
        search_names = []
        if expected_filename:
            search_names.append(expected_filename)
        
        search_names.extend([
            f"aegis-{edition_id}.iso",
            f"aegis-{edition_id.replace('_', '-')}.iso",
            f"AegisOS-{edition_id.title()}.iso",
            f"aegis-os-{edition_id}.iso"
        ])
        search_names = list(dict.fromkeys(search_names))
        
        for path in search_paths:
            for filename in search_names:
                iso_path = Path(path) / filename
                if iso_path.exists() and iso_path.is_file():
                    source = OfflineISOLocator._describe_source(path)
                    return str(iso_path), {
                        "sha256": expected_sha256,
                        "manifest_path": manifest_path
                    }, source
        
        return None, None, None
    
    @staticmethod
    def _describe_source(path):
        """Create human-readable source description"""
        path_str = str(path)
        
        if sys.platform == "win32":
            if len(path_str) >= 2 and path_str[1] == ':':
                return f"Drive {path_str[0].upper()}:"
        
        if "/media/" in path_str or "/mnt/" in path_str or "/Volumes/" in path_str:
            return f"USB Drive ({Path(path_str).name})"
        
        if str(Path.home()) in path_str:
            rel = Path(path_str).relative_to(Path.home())
            return f"Home/{rel}"
        
        return path_str


class RSALicenseValidator:
    """Handles RSA-2048 license verification"""
    
    def __init__(self, public_key_pem=RSA_PUBLIC_KEY_PEM):
        self.public_key_pem = public_key_pem
        self.public_key = None
        
        if CRYPTO_AVAILABLE:
            try:
                self.public_key = serialization.load_pem_public_key(
                    public_key_pem.encode(),
                    backend=default_backend()
                )
            except Exception:
                pass
    
    def find_license_file(self):
        """Search for license file in standard locations"""
        license_paths = [
            Path.home() / ".aegis" / "license.json",
            Path.cwd() / "license.json",
            Path(__file__).parent / "license.json",
            Path(__file__).parent.parent / "license.json",
        ]
        
        for usb in OfflineISOLocator.get_usb_mount_points():
            license_paths.append(Path(usb) / "license.json")
            license_paths.append(Path(usb) / "aegis" / "license.json")
            license_paths.append(Path(usb) / "AegisOS" / "license.json")
        
        for path in license_paths:
            if path.exists():
                return str(path)
        
        return None
    
    def load_license(self, license_path):
        """Load and parse license file"""
        try:
            with open(license_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            return None
    
    def verify_license(self, license_data):
        """
        Verify license using RSA-2048 signature
        
        License format:
        {
            "license_key": "XXXX-XXXX-XXXX-XXXX",
            "edition": "basic",
            "customer_email": "user@example.com",
            "issued_date": "2024-01-15",
            "expiry_date": null,  # null = lifetime
            "signature": "base64-encoded-signature"
        }
        
        Returns: (valid, edition_id, edition_name, message)
        """
        if not license_data:
            return False, None, None, "No license data provided"
        
        required_fields = ["license_key", "edition", "signature"]
        for field in required_fields:
            if field not in license_data:
                return False, None, None, f"Missing required field: {field}"
        
        edition_id = license_data.get("edition")
        if edition_id not in EDITIONS:
            return False, None, None, f"Unknown edition: {edition_id}"
        
        edition_name = EDITIONS[edition_id]["name"]
        
        expiry = license_data.get("expiry_date")
        if expiry:
            try:
                expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
                if expiry_date < datetime.now():
                    return False, None, None, f"License expired on {expiry}"
            except ValueError:
                pass
        
        if not CRYPTO_AVAILABLE:
            return False, None, None, "Cryptography library not available. Install with: pip install cryptography"
        
        if not self.public_key:
            return False, None, None, "Failed to load public key for verification"
        
        try:
            signature_data = {
                "license_key": license_data["license_key"],
                "edition": license_data["edition"],
                "customer_email": license_data.get("customer_email", ""),
                "issued_date": license_data.get("issued_date", ""),
                "expiry_date": license_data.get("expiry_date")
            }
            data_to_verify = json.dumps(signature_data, sort_keys=True, separators=(',', ':'))
            
            signature = base64.b64decode(license_data["signature"])
            
            self.public_key.verify(
                signature,
                data_to_verify.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            return True, edition_id, edition_name, "License verified successfully"
            
        except InvalidSignature:
            return False, None, None, "Invalid license signature - license may be tampered or fake"
        except binascii.Error:
            return False, None, None, "Invalid signature format (not valid base64)"
        except Exception as e:
            return False, None, None, f"Signature verification failed: {str(e)}"
    
    def validate_from_file(self, license_path=None):
        """Convenience method to validate from file"""
        if not license_path:
            license_path = self.find_license_file()
        
        if not license_path:
            return False, None, None, "No license file found. Check ~/.aegis/license.json or USB drive."
        
        license_data = self.load_license(license_path)
        if not license_data:
            return False, None, None, f"Failed to parse license file: {license_path}"
        
        return self.verify_license(license_data)


class ISODownloader:
    """Handles ISO downloads with progress, resume support, and checksum verification"""
    
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.cancelled = False
        self.download_thread = None
        self._last_bytes = 0
        self._last_time = 0
    
    def cancel(self):
        """Cancel the current download"""
        self.cancelled = True
    
    def _get_ssl_context(self):
        """Create SSL context with fallback for certificate issues"""
        try:
            context = ssl.create_default_context()
            return context
        except Exception:
            context = ssl._create_unverified_context()
            return context
    
    def _check_internet(self):
        """Check if internet connection is available"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def _get_remote_file_size(self, url):
        """Get the size of the remote file"""
        try:
            context = self._get_ssl_context()
            request = urllib.request.Request(url, method='HEAD')
            request.add_header('User-Agent', f'AegisOS-Installer/{VERSION}')
            
            with urllib.request.urlopen(request, timeout=10, context=context) as response:
                return int(response.headers.get('Content-Length', 0))
        except Exception:
            return 0
    
    def _fetch_checksum(self, checksum_url):
        """Fetch SHA-256 checksum from server"""
        try:
            context = self._get_ssl_context()
            request = urllib.request.Request(checksum_url)
            request.add_header('User-Agent', f'AegisOS-Installer/{VERSION}')
            
            with urllib.request.urlopen(request, timeout=10, context=context) as response:
                content = response.read().decode('utf-8').strip()
                if len(content) >= 64:
                    return content[:64].upper()
                return None
        except Exception:
            return None
    
    def download(self, url, destination, expected_sha256=None, fallback_url=None, checksum_url=None):
        """
        Download ISO with progress, resume support, and verification
        
        Args:
            url: Primary download URL
            destination: Local file path to save to
            expected_sha256: Expected SHA-256 hash (optional)
            fallback_url: Fallback URL if primary fails
            checksum_url: URL to fetch checksum from (optional)
        
        Returns:
            (success, message, sha256_hash)
        """
        self.cancelled = False
        dest_path = Path(destination)
        
        if not self._check_internet():
            return False, "No internet connection available", None
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not expected_sha256 and checksum_url:
            expected_sha256 = self._fetch_checksum(checksum_url)
        
        partial_path = Path(str(destination) + ".partial")
        
        success, message, sha256_hash = self._download_with_resume(
            url, destination, partial_path, expected_sha256
        )
        
        if not success and fallback_url and not self.cancelled:
            if self.progress_callback:
                self.progress_callback(0, "Trying fallback server...", "")
            success, message, sha256_hash = self._download_with_resume(
                fallback_url, destination, partial_path, expected_sha256
            )
        
        return success, message, sha256_hash
    
    def _download_with_resume(self, url, destination, partial_path, expected_sha256):
        """Download with resume support"""
        try:
            context = self._get_ssl_context()
            
            existing_size = 0
            if partial_path.exists():
                existing_size = partial_path.stat().st_size
            
            request = urllib.request.Request(url)
            request.add_header('User-Agent', f'AegisOS-Installer/{VERSION}')
            
            if existing_size > 0:
                request.add_header('Range', f'bytes={existing_size}-')
            
            try:
                response = urllib.request.urlopen(request, timeout=30, context=context)
            except urllib.error.HTTPError as e:
                if e.code == 416:
                    if partial_path.exists():
                        partial_path.rename(destination)
                        return self._verify_download(destination, expected_sha256)
                raise
            
            content_length = response.headers.get('Content-Length')
            total_size = int(content_length) if content_length else 0
            
            if existing_size > 0 and response.status == 206:
                content_range = response.headers.get('Content-Range', '')
                if '/' in content_range:
                    total_size = int(content_range.split('/')[-1])
            else:
                existing_size = 0
                total_size = int(content_length) if content_length else 0
            
            downloaded = existing_size
            start_time = time.time()
            self._last_bytes = downloaded
            self._last_time = start_time
            
            mode = 'ab' if existing_size > 0 and response.status == 206 else 'wb'
            
            with open(partial_path, mode) as f:
                while True:
                    if self.cancelled:
                        return False, "Download cancelled by user", None
                    
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    now = time.time()
                    if now - self._last_time >= 0.3:
                        elapsed = now - start_time
                        speed_bytes = (downloaded - existing_size) / elapsed if elapsed > 0 else 0
                        speed_mb = speed_bytes / (1024 * 1024)
                        
                        if total_size > 0:
                            pct = int((downloaded / total_size) * 100)
                            remaining = total_size - downloaded
                            eta_secs = remaining / speed_bytes if speed_bytes > 0 else 0
                            
                            if eta_secs > 3600:
                                eta_str = f"{int(eta_secs/3600)}h {int((eta_secs%3600)/60)}m"
                            elif eta_secs > 60:
                                eta_str = f"{int(eta_secs/60)}m {int(eta_secs%60)}s"
                            else:
                                eta_str = f"{int(eta_secs)}s"
                            
                            size_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            
                            if self.progress_callback:
                                self.progress_callback(
                                    pct,
                                    f"Downloading: {size_mb:.0f} / {total_mb:.0f} MB",
                                    f"{speed_mb:.1f} MB/s • ETA: {eta_str}"
                                )
                        else:
                            size_mb = downloaded / (1024 * 1024)
                            if self.progress_callback:
                                self.progress_callback(
                                    -1,
                                    f"Downloading: {size_mb:.0f} MB",
                                    f"{speed_mb:.1f} MB/s"
                                )
                        
                        self._last_time = now
                        self._last_bytes = downloaded
            
            partial_path.rename(destination)
            
            return self._verify_download(destination, expected_sha256)
            
        except urllib.error.URLError as e:
            if hasattr(e, 'reason'):
                return False, f"Connection failed: {e.reason}", None
            return False, f"URL error: {e}", None
        except socket.timeout:
            return False, "Connection timed out", None
        except Exception as e:
            return False, f"Download failed: {str(e)}", None
    
    def _verify_download(self, filepath, expected_sha256):
        """Verify downloaded file checksum"""
        if self.progress_callback:
            self.progress_callback(99, "Verifying checksum...", "")
        
        sha256 = hashlib.sha256()
        file_size = Path(filepath).stat().st_size
        processed = 0
        
        with open(filepath, 'rb') as f:
            while True:
                if self.cancelled:
                    return False, "Verification cancelled", None
                
                chunk = f.read(8192)
                if not chunk:
                    break
                sha256.update(chunk)
                processed += len(chunk)
        
        actual_hash = sha256.hexdigest().upper()
        
        if expected_sha256:
            expected = expected_sha256.upper()
            if actual_hash != expected:
                Path(filepath).unlink(missing_ok=True)
                return False, f"Checksum mismatch!\nExpected: {expected[:16]}...\nGot: {actual_hash[:16]}...", None
        
        return True, "Download completed successfully", actual_hash


class AegisLicensedInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("600x660")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        self.install_folder = str(Path.home() / "AegisOS")
        self.copy_thread = None
        self.cancel_operation = False
        self.iso_path = ""
        self.iso_hash = ""
        self.is_downloading = False
        self.iso_downloader = None
        self.manifest_data = None
        
        self.license_validator = RSALicenseValidator()
        self.license_path = None
        self.license_data = None
        self.validated_edition_id = None
        self.validated_edition_name = None
        
        self._setup_styles()
        self._create_ui()
        self._center_window()
        self._scan_for_license()
    
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Header.TFrame", background="#005A9E")
        style.configure("Header.TLabel", background="#005A9E", foreground="white",
                       font=("Segoe UI", 18, "bold"))
        style.configure("HeaderSub.TLabel", background="#005A9E", foreground="#E0E0E0",
                       font=("Segoe UI", 11))
        
        style.configure("Section.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("Section.TLabel", background="white", font=("Segoe UI", 10))
        style.configure("SectionTitle.TLabel", background="white", foreground="#005A9E",
                       font=("Segoe UI", 12, "bold"))
        
        style.configure("Valid.TLabel", background="white", foreground="#28a745",
                       font=("Segoe UI", 10))
        style.configure("Invalid.TLabel", background="white", foreground="#dc3545",
                       font=("Segoe UI", 10))
        
        style.configure("Progress.TLabel", background="white", font=("Segoe UI", 36, "bold"),
                       foreground="#005A9E")
        style.configure("Success.TLabel", background="white", font=("Segoe UI", 16),
                       foreground="#005A9E")
        
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10))
        
        style.configure("Blue.Horizontal.TProgressbar", troughcolor="#ddd",
                       background="#005A9E", thickness=8)
    
    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_ui(self):
        header = tk.Frame(self.root, bg="#005A9E", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_inner = tk.Frame(header, bg="#005A9E")
        header_inner.pack(expand=True)
        
        title = tk.Label(header_inner, text="Aegis OS Licensed Installer",
                        font=("Segoe UI", 18, "bold"), bg="#005A9E", fg="white")
        title.pack(pady=(15, 2))
        
        subtitle = tk.Label(header_inner, text="Offline Installer with RSA License Verification",
                           font=("Segoe UI", 11), bg="#005A9E", fg="#E0E0E0")
        subtitle.pack()
        
        self.content = tk.Frame(self.root, bg="#f0f0f0")
        self.content.pack(fill="both", expand=True, padx=20, pady=15)
        
        self.step1_frame = tk.Frame(self.content, bg="#f0f0f0")
        self.step2_frame = tk.Frame(self.content, bg="#f0f0f0")
        self.step3_frame = tk.Frame(self.content, bg="#f0f0f0")
        
        self._create_step1()
        self._create_step2()
        self._create_step3()
        
        self._show_step(1)
        
        footer = tk.Frame(self.root, bg="#e0e0e0", height=55)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        btn_frame = tk.Frame(footer, bg="#e0e0e0")
        btn_frame.pack(side="right", padx=15, pady=10)
        
        self.btn_cancel = ttk.Button(btn_frame, text="Cancel", command=self._on_cancel)
        self.btn_cancel.pack(side="left", padx=5)
        
        self.btn_start = ttk.Button(btn_frame, text="Verify & Install",
                                    command=self._verify_and_install,
                                    style="Primary.TButton", state="disabled")
        self.btn_start.pack(side="left", padx=5)
    
    def _create_section(self, parent, title):
        frame = tk.Frame(parent, bg="white", bd=1, relief="solid")
        frame.pack(fill="x", pady=5)
        
        inner = tk.Frame(frame, bg="white")
        inner.pack(fill="both", padx=15, pady=12)
        
        if title:
            lbl = tk.Label(inner, text=title, font=("Segoe UI", 12, "bold"),
                          bg="white", fg="#005A9E")
            lbl.pack(anchor="w")
        
        return inner
    
    def _create_step1(self):
        license_section = self._create_section(self.step1_frame, "License File (RSA-2048 Verified)")
        
        self.license_status_label = tk.Label(license_section, text="Scanning for license...",
                                            font=("Segoe UI", 10), bg="white", fg="#888888")
        self.license_status_label.pack(anchor="w", pady=(5, 0))
        
        self.license_path_label = tk.Label(license_section, text="",
                                          font=("Consolas", 9), bg="#f5f5f5",
                                          wraplength=450, justify="left")
        self.license_path_label.pack(fill="x", padx=0, pady=(5, 5))
        
        btn_frame = tk.Frame(license_section, bg="white")
        btn_frame.pack(anchor="w", pady=(0, 5))
        
        self.btn_browse_license = ttk.Button(btn_frame, text="Browse for License...",
                                            command=self._browse_license)
        self.btn_browse_license.pack(side="left", padx=(0, 5))
        
        self.btn_rescan = ttk.Button(btn_frame, text="Rescan",
                                    command=self._scan_for_license)
        self.btn_rescan.pack(side="left")
        
        edition_section = self._create_section(self.step1_frame, "Licensed Edition")
        
        self.edition_info_frame = tk.Frame(edition_section, bg="white")
        self.edition_info_frame.pack(fill="x", pady=(5, 0))
        
        self.edition_name_label = tk.Label(self.edition_info_frame,
                                          text="No valid license detected",
                                          font=("Segoe UI", 11), bg="white", fg="#888888")
        self.edition_name_label.pack(anchor="w")
        
        self.features_frame = tk.Frame(edition_section, bg="white")
        self.features_frame.pack(fill="x", pady=(8, 0))
        
        self.iso_section = self._create_section(self.step1_frame, "ISO Source")
        
        self.iso_status_label = tk.Label(self.iso_section, text="Validate license first",
                                        font=("Segoe UI", 10), bg="white", fg="#888888")
        self.iso_status_label.pack(anchor="w", pady=(5, 0))
        
        self.iso_path_label = tk.Label(self.iso_section, text="",
                                      font=("Consolas", 9), bg="#f5f5f5",
                                      wraplength=450, justify="left")
        self.iso_path_label.pack(fill="x", padx=0, pady=(5, 5))
        
        iso_btn_frame = tk.Frame(self.iso_section, bg="white")
        iso_btn_frame.pack(anchor="w", pady=(0, 5))
        
        self.btn_browse_iso = ttk.Button(iso_btn_frame, text="Browse for ISO...",
                                        command=self._browse_iso)
        self.btn_browse_iso.pack(side="left", padx=(0, 5))
        self.btn_browse_iso.pack_forget()
        
        self.btn_download_iso = ttk.Button(iso_btn_frame, text="Download ISO...",
                                          command=self._start_download)
        self.btn_download_iso.pack(side="left")
        self.btn_download_iso.pack_forget()
        
        folder_section = self._create_section(self.step1_frame, "Install Location")
        
        path_frame = tk.Frame(folder_section, bg="#f5f5f5")
        path_frame.pack(fill="x", pady=(8, 5))
        
        self.folder_label = tk.Label(path_frame, text=self.install_folder,
                                    font=("Consolas", 9), bg="#f5f5f5",
                                    wraplength=450, justify="left")
        self.folder_label.pack(padx=8, pady=6, anchor="w")
        
        btn_browse = ttk.Button(folder_section, text="Change Folder",
                               command=self._browse_folder)
        btn_browse.pack(anchor="w", pady=(0, 5))
    
    def _create_step2(self):
        progress_section = self._create_section(self.step2_frame, None)
        
        center_frame = tk.Frame(progress_section, bg="white")
        center_frame.pack(expand=True, pady=20)
        
        self.progress_pct = tk.Label(center_frame, text="0%",
                                    font=("Segoe UI", 42, "bold"),
                                    bg="white", fg="#005A9E")
        self.progress_pct.pack()
        
        self.progress_bar = ttk.Progressbar(center_frame, length=450, mode="determinate",
                                           style="Blue.Horizontal.TProgressbar")
        self.progress_bar.pack(pady=10)
        
        self.progress_text = tk.Label(center_frame, text="Preparing...",
                                     font=("Segoe UI", 11), bg="white", fg="#666666")
        self.progress_text.pack()
        
        self.progress_speed = tk.Label(center_frame, text="",
                                      font=("Segoe UI", 10), bg="white", fg="#888888")
        self.progress_speed.pack(pady=(5, 0))
    
    def _create_step3(self):
        success_section = self._create_section(self.step3_frame, None)
        
        success_lbl = tk.Label(success_section, text="✔ Installation Complete!",
                              font=("Segoe UI", 18), bg="white", fg="#005A9E")
        success_lbl.pack(pady=10)
        
        license_section = self._create_section(self.step3_frame, "License Details")
        
        self.final_edition_label = tk.Label(license_section, text="",
                                           font=("Segoe UI", 11, "bold"), bg="white")
        self.final_edition_label.pack(anchor="w", pady=(5, 0))
        
        self.final_license_label = tk.Label(license_section, text="",
                                           font=("Consolas", 9), bg="#f5f5f5")
        self.final_license_label.pack(fill="x", padx=0, pady=(5, 0))
        
        path_section = self._create_section(self.step3_frame, "ISO File")
        
        self.final_iso_path_label = tk.Label(path_section, text="",
                                            font=("Consolas", 9), bg="#f5f5f5",
                                            wraplength=500, justify="left")
        self.final_iso_path_label.pack(fill="x", padx=8, pady=6)
        
        next_section = self._create_section(self.step3_frame, "Next: Create Bootable USB")
        
        step1_frame = tk.Frame(next_section, bg="white")
        step1_frame.pack(anchor="w", pady=2)
        
        tk.Label(step1_frame, text="1. Use ", font=("Segoe UI", 10), bg="white").pack(side="left")
        
        etcher_link = tk.Label(step1_frame, text="Balena Etcher",
                              font=("Segoe UI", 10, "underline"),
                              bg="white", fg="#0066cc", cursor="hand2")
        etcher_link.pack(side="left")
        etcher_link.bind("<Button-1>", lambda e: self._open_etcher())
        
        tk.Label(step1_frame, text=" or similar tool", font=("Segoe UI", 10), bg="white").pack(side="left")
        
        tk.Label(next_section, text="2. Select ISO, select USB, click Flash",
                font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=2)
    
    def _show_step(self, step):
        self.step1_frame.pack_forget()
        self.step2_frame.pack_forget()
        self.step3_frame.pack_forget()
        
        if step == 1:
            self.step1_frame.pack(fill="both", expand=True)
            self.btn_start.configure(text="Verify & Install",
                                    command=self._verify_and_install)
        elif step == 2:
            self.step2_frame.pack(fill="both", expand=True)
            self.btn_start.configure(text="Installing...", state="disabled")
        elif step == 3:
            self.step3_frame.pack(fill="both", expand=True)
            self.btn_start.configure(text="Open Folder", state="normal",
                                    command=self._open_folder)
            self.btn_cancel.configure(text="Close")
    
    def _scan_for_license(self):
        """Scan for license file and validate"""
        self.license_status_label.configure(text="Scanning for license...", fg="#888888")
        self.license_path_label.configure(text="")
        self.root.update()
        
        license_path = self.license_validator.find_license_file()
        
        if license_path:
            self.license_path = license_path
            self.license_path_label.configure(text=license_path)
            self._validate_license()
        else:
            self.license_path = None
            self.license_status_label.configure(
                text="✗ No license file found. Check ~/.aegis/license.json or insert USB.",
                fg="#dc3545"
            )
            self.btn_start.configure(state="disabled")
            self._clear_edition_features()
    
    def _validate_license(self):
        """Validate the current license file"""
        if not self.license_path:
            return
        
        self.license_data = self.license_validator.load_license(self.license_path)
        if not self.license_data:
            self.license_status_label.configure(
                text="✗ Failed to parse license file",
                fg="#dc3545"
            )
            self.btn_start.configure(state="disabled")
            return
        
        valid, edition_id, edition_name, message = self.license_validator.verify_license(self.license_data)
        
        if valid:
            self.validated_edition_id = edition_id
            self.validated_edition_name = edition_name
            
            self.license_status_label.configure(
                text=f"✓ {message}",
                fg="#28a745"
            )
            self._show_edition_features(edition_id)
            self._scan_for_iso()
        else:
            self.validated_edition_id = None
            self.validated_edition_name = None
            
            self.license_status_label.configure(
                text=f"✗ {message}",
                fg="#dc3545"
            )
            self._clear_edition_features()
            self.btn_start.configure(state="disabled")
    
    def _scan_for_iso(self):
        """Scan for ISO file matching the licensed edition"""
        if not self.validated_edition_id:
            return
        
        self.iso_status_label.configure(text="Scanning for ISO...", fg="#888888")
        self.iso_path_label.configure(text="")
        self.btn_browse_iso.pack_forget()
        self.btn_download_iso.pack_forget()
        self.root.update()
        
        iso_path, manifest_data, source = OfflineISOLocator.find_iso(self.validated_edition_id)
        
        if iso_path:
            self.iso_path = iso_path
            self.manifest_data = manifest_data
            
            self.iso_status_label.configure(
                text=f"✓ ISO found: {source}",
                fg="#28a745"
            )
            self.iso_path_label.configure(text=iso_path)
            self.btn_start.configure(state="normal")
            self.btn_browse_iso.pack_forget()
            self.btn_download_iso.pack_forget()
        else:
            self.iso_path = ""
            self.iso_status_label.configure(
                text=f"✗ No ISO found locally. Browse for ISO or download from Aegis servers.",
                fg="#dc3545"
            )
            self.btn_start.configure(state="disabled")
            self.btn_browse_iso.pack(side="left", padx=(0, 5))
            self.btn_download_iso.pack(side="left")
    
    def _browse_iso(self):
        """Browse for ISO file manually"""
        if not self.validated_edition_id:
            messagebox.showerror("No License", "Please validate your license first.")
            return
        
        iso_file = filedialog.askopenfilename(
            title=f"Select {self.validated_edition_name} ISO",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")],
            initialdir=str(Path.home() / "Downloads")
        )
        
        if iso_file:
            self.iso_path = iso_file
            self.manifest_data = None
            
            self.iso_status_label.configure(
                text="✓ ISO selected manually",
                fg="#28a745"
            )
            self.iso_path_label.configure(text=iso_file)
            self.btn_start.configure(state="normal")
            self.btn_browse_iso.pack_forget()
            self.btn_download_iso.pack_forget()
    
    def _start_download(self):
        """Prompt user for download location and start download"""
        if not self.validated_edition_id:
            messagebox.showerror("No License", "Please validate your license first.")
            return
        
        edition = EDITIONS.get(self.validated_edition_id)
        if not edition:
            messagebox.showerror("Error", "Invalid edition")
            return
        
        download_dir = filedialog.askdirectory(
            title="Select Download Location",
            initialdir=str(DEFAULT_DOWNLOAD_DIR.parent)
        )
        
        if not download_dir:
            download_dir = str(DEFAULT_DOWNLOAD_DIR)
        
        iso_filename = edition.get("iso_filename", f"aegis-{self.validated_edition_id}.iso")
        destination = os.path.join(download_dir, iso_filename)
        
        if os.path.exists(destination):
            if not messagebox.askyesno("File Exists",
                                       f"ISO already exists at:\n{destination}\n\nReplace it?"):
                self.iso_path = destination
                self.iso_status_label.configure(
                    text=f"✓ Using existing ISO",
                    fg="#28a745"
                )
                self.iso_path_label.configure(text=destination)
                self.btn_start.configure(state="normal")
                self.btn_browse_iso.pack_forget()
                self.btn_download_iso.pack_forget()
                return
        
        self.cancel_operation = False
        self.is_downloading = True
        self._show_step(2)
        self.progress_text.configure(text="Starting download...")
        
        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(destination, iso_filename),
            daemon=True
        )
        self.download_thread.start()
    
    def _download_worker(self, destination, iso_filename):
        """Background worker for ISO download"""
        def progress_callback(pct, text, speed):
            self._update_progress(pct if pct >= 0 else 0, text, speed)
        
        self.iso_downloader = ISODownloader(progress_callback=progress_callback)
        
        primary_url = f"{ISO_DOWNLOAD_BASE_URL}/{iso_filename}"
        fallback_url = f"{ISO_DOWNLOAD_FALLBACK_URL}/{iso_filename}"
        checksum_url = f"{ISO_DOWNLOAD_BASE_URL}/{iso_filename}.sha256"
        
        success, message, sha256_hash = self.iso_downloader.download(
            url=primary_url,
            destination=destination,
            fallback_url=fallback_url,
            checksum_url=checksum_url
        )
        
        if success:
            self.iso_path = destination
            self.iso_hash = sha256_hash
            self.is_downloading = False
            self._download_complete(destination, sha256_hash)
        else:
            self.is_downloading = False
            if not self.cancel_operation:
                self._show_download_error(message)
    
    def _download_complete(self, dest_path, sha256_hash):
        """Handle successful download completion"""
        def complete():
            self.final_edition_label.configure(text=self.validated_edition_name)
            if self.license_data:
                self.final_license_label.configure(
                    text=f"Key: {self.license_data.get('license_key', 'N/A')}"
                )
            self.final_iso_path_label.configure(text=dest_path)
            self._show_step(3)
        
        self.root.after(0, complete)
    
    def _show_download_error(self, message):
        """Show download error and allow retry"""
        def show():
            self.progress_pct.configure(text="!", fg="#d32f2f")
            self.progress_text.configure(text=message, fg="#d32f2f")
            self.progress_speed.configure(text="")
            self.btn_start.configure(text="Retry Download", state="normal",
                                    command=self._retry_download)
            self.btn_cancel.configure(text="Back", command=self._go_back)
        
        self.root.after(0, show)
    
    def _retry_download(self):
        """Retry the download"""
        self.progress_pct.configure(fg="#005A9E")
        self.progress_text.configure(fg="#666666")
        
        edition = EDITIONS.get(self.validated_edition_id)
        if not edition:
            return
        
        download_dir = str(DEFAULT_DOWNLOAD_DIR)
        iso_filename = edition.get("iso_filename", f"aegis-{self.validated_edition_id}.iso")
        destination = os.path.join(download_dir, iso_filename)
        
        self.cancel_operation = False
        self.is_downloading = True
        
        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(destination, iso_filename),
            daemon=True
        )
        self.download_thread.start()
    
    def _go_back(self):
        """Go back to step 1"""
        self._show_step(1)
        self.btn_cancel.configure(text="Cancel", command=self._on_cancel)
    
    def _browse_license(self):
        """Browse for license file manually"""
        license_file = filedialog.askopenfilename(
            title="Select Aegis OS License File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path.home())
        )
        
        if license_file:
            self.license_path = license_file
            self.license_path_label.configure(text=license_file)
            self._validate_license()
    
    def _show_edition_features(self, edition_id):
        edition = EDITIONS.get(edition_id)
        if not edition:
            return
        
        self.edition_name_label.configure(
            text=f"{edition['name']} ({edition['price']})",
            fg="#005A9E"
        )
        
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        for feature in edition["features"]:
            f_frame = tk.Frame(self.features_frame, bg="white")
            f_frame.pack(anchor="w", pady=1)
            
            check = tk.Label(f_frame, text="✓", font=("Segoe UI", 10, "bold"),
                           bg="white", fg="#005A9E")
            check.pack(side="left")
            
            lbl = tk.Label(f_frame, text=f" {feature}", font=("Segoe UI", 9), bg="white")
            lbl.pack(side="left")
    
    def _clear_edition_features(self):
        self.edition_name_label.configure(text="No valid license detected", fg="#888888")
        
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        self.iso_status_label.configure(text="Validate license first", fg="#888888")
        self.iso_path_label.configure(text="")
    
    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.install_folder,
                                        title="Select Install Location")
        if folder:
            self.install_folder = folder
            self.folder_label.configure(text=folder)
    
    def _verify_and_install(self):
        """Verify license, activate, and start installation"""
        if not self.validated_edition_id:
            messagebox.showerror("No License", "Please provide a valid license file.")
            return
        
        if not self.iso_path:
            messagebox.showerror("No ISO", "No ISO file found. Please insert USB with ISO.")
            return
        
        license_key = self.license_data.get("license_key") if self.license_data else None
        if not license_key:
            messagebox.showerror("Invalid License", "License key not found.")
            return
        
        self.cancel_operation = False
        self._show_step(2)
        self._update_progress(0, "Activating license...", "Contacting server...")
        
        self.copy_thread = threading.Thread(
            target=self._activate_and_install_worker,
            args=(license_key,),
            daemon=True
        )
        self.copy_thread.start()
    
    def _activate_and_install_worker(self, license_key):
        """Activate license then proceed with installation"""
        try:
            from activation_client import ActivationClient, HardwareFingerprint
            
            self._update_progress(2, "Checking license activation...", "")
            
            client = ActivationClient()
            success, message, activation_data = client.activate(license_key, self.validated_edition_id)
            
            if not success:
                if "Connection" in message or "timed out" in message.lower():
                    self._update_progress(3, "Server unavailable, checking local activation...", "")
                    offline_success, offline_message = client.check_offline(license_key, self.validated_edition_id)
                    
                    if offline_success:
                        self._update_progress(5, "License verified (offline mode)", "")
                    else:
                        self._show_error("Activation Required", 
                            "This license needs to be activated online first.\n"
                            "Please connect to the internet and try again.")
                        return
                else:
                    self._show_error("Activation Failed", message)
                    return
            else:
                activations_left = 0
                if activation_data:
                    max_act = activation_data.get("max_activations", 3)
                    used = activation_data.get("activations_used", 1)
                    activations_left = max_act - used
                
                self._update_progress(5, f"License activated ({activations_left} activations remaining)", "")
            
            self._install_worker()
            
        except ImportError:
            self._update_progress(5, "Activation module not available, proceeding...", "")
            self._install_worker()
        except Exception as e:
            self._show_error("Activation Error", str(e))
    
    def _install_worker(self):
        """Copy ISO to install location with verification"""
        try:
            os.makedirs(self.install_folder, exist_ok=True)
            
            dest_path = os.path.join(self.install_folder, os.path.basename(self.iso_path))
            
            source_size = os.path.getsize(self.iso_path)
            copied = 0
            start_time = time.time()
            last_update = start_time
            
            self._update_progress(0, "Verifying source ISO...", "")
            
            sha256 = hashlib.sha256()
            with open(self.iso_path, 'rb') as src:
                while True:
                    if self.cancel_operation:
                        return
                    
                    chunk = src.read(8192)
                    if not chunk:
                        break
                    sha256.update(chunk)
            
            source_hash = sha256.hexdigest().upper()
            
            if hasattr(self, 'manifest_data') and self.manifest_data and self.manifest_data.get("sha256"):
                expected = self.manifest_data["sha256"].upper()
                if source_hash != expected:
                    self._show_error("Checksum Mismatch",
                                    f"ISO checksum does not match manifest.\n"
                                    f"Expected: {expected[:16]}...\n"
                                    f"Got: {source_hash[:16]}...")
                    return
            
            if self.iso_path == dest_path:
                self.iso_hash = source_hash
                self._install_complete(dest_path)
                return
            
            self._update_progress(5, "Copying ISO to install location...", "")
            
            with open(self.iso_path, 'rb') as src:
                with open(dest_path, 'wb') as dst:
                    while True:
                        if self.cancel_operation:
                            try:
                                os.remove(dest_path)
                            except:
                                pass
                            return
                        
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        
                        dst.write(chunk)
                        copied += len(chunk)
                        
                        now = time.time()
                        if now - last_update >= 0.3:
                            pct = 5 + int((copied / source_size) * 85)
                            elapsed = now - start_time
                            speed = copied / elapsed / (1024 * 1024) if elapsed > 0 else 0
                            
                            self._update_progress(
                                pct,
                                f"Copying: {int(copied/source_size*100)}%",
                                f"{speed:.1f} MB/s"
                            )
                            last_update = now
            
            self._update_progress(92, "Verifying copied file...", "")
            
            verify_hash = hashlib.sha256()
            with open(dest_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    verify_hash.update(chunk)
            
            dest_hash = verify_hash.hexdigest().upper()
            
            if dest_hash != source_hash:
                self._show_error("Copy Verification Failed",
                                "Copied file does not match source. Please try again.")
                try:
                    os.remove(dest_path)
                except:
                    pass
                return
            
            self.iso_hash = dest_hash
            self._install_complete(dest_path)
            
        except PermissionError:
            self._show_error("Permission Denied",
                            "Cannot write to the selected folder. Choose another location.")
        except OSError as e:
            self._show_error("File Error", f"Error during installation: {e}")
        except Exception as e:
            self._show_error("Installation Failed", str(e))
    
    def _update_progress(self, pct, text, speed):
        def update():
            self.progress_pct.configure(text=f"{pct}%")
            self.progress_bar["value"] = pct
            self.progress_text.configure(text=text)
            self.progress_speed.configure(text=speed)
        
        self.root.after(0, update)
    
    def _install_complete(self, dest_path):
        def complete():
            self.final_edition_label.configure(text=self.validated_edition_name)
            if self.license_data:
                self.final_license_label.configure(
                    text=f"Key: {self.license_data.get('license_key', 'N/A')}"
                )
            self.final_iso_path_label.configure(text=dest_path)
            self._show_step(3)
        
        self.root.after(0, complete)
    
    def _show_error(self, title, message):
        def show():
            self.progress_pct.configure(text="!", fg="#d32f2f")
            self.progress_text.configure(text=message, fg="#d32f2f")
            self.progress_speed.configure(text="")
            self.btn_start.configure(text="Retry", state="normal",
                                    command=self._retry_install)
        
        self.root.after(0, show)
    
    def _retry_install(self):
        self.progress_pct.configure(fg="#005A9E")
        self.progress_text.configure(fg="#666666")
        self._verify_and_install()
    
    def _open_folder(self):
        if sys.platform == "win32":
            os.startfile(self.install_folder)
        elif sys.platform == "darwin":
            os.system(f'open "{self.install_folder}"')
        else:
            os.system(f'xdg-open "{self.install_folder}"')
    
    def _open_etcher(self):
        webbrowser.open("https://etcher.balena.io/")
    
    def _on_cancel(self):
        if self.is_downloading and self.iso_downloader:
            if messagebox.askyesno("Cancel Download", 
                                  "Are you sure you want to cancel the download?"):
                self.cancel_operation = True
                self.iso_downloader.cancel()
                self._go_back()
        elif self.copy_thread and self.copy_thread.is_alive():
            if messagebox.askyesno("Cancel Installation",
                                  "Are you sure you want to cancel?"):
                self.cancel_operation = True
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()


def main():
    if not CRYPTO_AVAILABLE:
        try:
            import tkinter.messagebox as mb
            root = tk.Tk()
            root.withdraw()
            mb.showwarning(
                "Missing Dependency",
                "The 'cryptography' library is required for license verification.\n\n"
                "Install it with: pip install cryptography"
            )
            root.destroy()
        except:
            print("ERROR: The 'cryptography' library is required.")
            print("Install with: pip install cryptography")
        return
    
    app = AegisLicensedInstaller()
    app.run()


if __name__ == "__main__":
    main()
