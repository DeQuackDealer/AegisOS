#!/usr/bin/env python3
"""
Aegis OS Freemium Edition Installer
Offline installer with download fallback - sources ISOs from local media
with option to download from Aegis servers if not found locally
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
import shutil
import urllib.request
import urllib.error
import ssl
import socket

VERSION = "2.1.0"
APP_NAME = "Aegis OS Freemium Installer"

ISO_FILENAME = "aegis-freemium.iso"

ISO_DOWNLOAD_URLS = {
    "primary": "https://download.aegis-os.com/iso/aegis-freemium.iso",
    "fallback": "https://mirror.aegis-os.com/iso/aegis-freemium.iso"
}
ISO_CHECKSUM_URL = "https://download.aegis-os.com/iso/aegis-freemium.iso.sha256"
DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "AegisOS"
ALT_ISO_FILENAMES = [
    "aegis-freemium.iso",
    "AegisOS-Freemium.iso",
    "aegis-os-freemium.iso",
    "aegis_freemium.iso"
]

FEATURES = [
    "Core desktop environment",
    "Firefox browser",
    "Basic office suite",
    "Media player",
    "File manager",
    "Basic security",
    "Software center",
    "30-day premium trial"
]


def is_placeholder_checksum(checksum):
    """Check if a checksum is a placeholder (all zeros with trailing digit)"""
    if not checksum:
        return True
    checksum = checksum.upper().strip()
    if checksum.startswith("0" * 60):
        return True
    if all(c == '0' for c in checksum[:-1]) and checksum[-1].isdigit():
        return True
    return False


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
    def find_iso(edition="freemium"):
        """
        Find ISO file for the specified edition
        Returns: (iso_path, manifest_data, source_description)
        """
        search_paths = OfflineISOLocator.get_search_paths()
        
        manifest, manifest_path = OfflineISOLocator.load_manifest(search_paths)
        expected_sha256 = None
        expected_filename = None
        
        if manifest and "editions" in manifest:
            edition_data = manifest["editions"].get(edition, {})
            expected_filename = edition_data.get("filename")
            expected_sha256 = edition_data.get("sha256")
        
        search_names = []
        if expected_filename:
            search_names.append(expected_filename)
        search_names.extend(ALT_ISO_FILENAMES)
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
        
        for path in search_paths:
            try:
                for iso_file in Path(path).glob("*.iso"):
                    if "freemium" in iso_file.name.lower() or "aegis" in iso_file.name.lower():
                        source = OfflineISOLocator._describe_source(path)
                        return str(iso_file), {
                            "sha256": expected_sha256,
                            "manifest_path": manifest_path
                        }, source
            except PermissionError:
                continue
        
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


class AegisFreemiumInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("550x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        self.install_folder = str(Path.home() / "AegisOS")
        self.copy_thread = None
        self.cancel_operation = False
        self.iso_path = ""
        self.iso_hash = ""
        self.iso_source = ""
        self.manifest_data = None
        self.is_downloading = False
        self.iso_downloader = None
        
        self._setup_styles()
        self._create_ui()
        self._center_window()
        self._scan_for_iso()
    
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Header.TFrame", background="#0078D7")
        style.configure("Header.TLabel", background="#0078D7", foreground="white", 
                       font=("Segoe UI", 18, "bold"))
        style.configure("HeaderSub.TLabel", background="#0078D7", foreground="#E0E0E0",
                       font=("Segoe UI", 11))
        
        style.configure("Section.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("Section.TLabel", background="white", font=("Segoe UI", 10))
        style.configure("SectionTitle.TLabel", background="white", foreground="#0078D7",
                       font=("Segoe UI", 12, "bold"))
        
        style.configure("Feature.TLabel", background="white", font=("Segoe UI", 9))
        style.configure("Path.TLabel", background="#f5f5f5", font=("Consolas", 10))
        
        style.configure("Progress.TLabel", background="white", font=("Segoe UI", 36, "bold"),
                       foreground="#0078D7")
        style.configure("ProgressText.TLabel", background="white", font=("Segoe UI", 10),
                       foreground="#666666")
        
        style.configure("Success.TLabel", background="white", font=("Segoe UI", 16),
                       foreground="#0078D7")
        style.configure("Error.TLabel", background="white", font=("Segoe UI", 12),
                       foreground="#d32f2f")
        style.configure("Found.TLabel", background="white", foreground="#28a745",
                       font=("Segoe UI", 10))
        style.configure("NotFound.TLabel", background="white", foreground="#dc3545",
                       font=("Segoe UI", 10))
        
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10))
        
        style.configure("Blue.Horizontal.TProgressbar", troughcolor="#ddd", 
                       background="#0078D7", thickness=8)
    
    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_ui(self):
        header = tk.Frame(self.root, bg="#0078D7", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_inner = tk.Frame(header, bg="#0078D7")
        header_inner.pack(expand=True)
        
        title = tk.Label(header_inner, text="Aegis OS Freemium Edition",
                        font=("Segoe UI", 18, "bold"), bg="#0078D7", fg="white")
        title.pack(pady=(15, 2))
        
        subtitle = tk.Label(header_inner, text="Offline Installer - No Internet Required",
                           font=("Segoe UI", 11), bg="#0078D7", fg="#E0E0E0")
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
        
        self.btn_start = ttk.Button(btn_frame, text="Install ISO", 
                                    command=self._start_install, style="Primary.TButton",
                                    state="disabled")
        self.btn_start.pack(side="left", padx=5)
    
    def _create_section(self, parent, title):
        frame = tk.Frame(parent, bg="white", bd=1, relief="solid")
        frame.pack(fill="x", pady=5)
        
        inner = tk.Frame(frame, bg="white")
        inner.pack(fill="both", padx=15, pady=12)
        
        if title:
            lbl = tk.Label(inner, text=title, font=("Segoe UI", 12, "bold"),
                          bg="white", fg="#0078D7")
            lbl.pack(anchor="w")
        
        return inner
    
    def _create_step1(self):
        iso_section = self._create_section(self.step1_frame, "ISO Source")
        
        self.iso_status_label = tk.Label(iso_section, text="Scanning for ISO...",
                                        font=("Segoe UI", 10), bg="white", fg="#888888")
        self.iso_status_label.pack(anchor="w", pady=(5, 0))
        
        self.iso_path_label = tk.Label(iso_section, text="",
                                      font=("Consolas", 9), bg="#f5f5f5",
                                      wraplength=450, justify="left")
        self.iso_path_label.pack(fill="x", padx=0, pady=(5, 5))
        
        btn_frame = tk.Frame(iso_section, bg="white")
        btn_frame.pack(anchor="w", pady=(0, 5))
        
        self.btn_browse_iso = ttk.Button(btn_frame, text="Browse for ISO...",
                                        command=self._browse_iso)
        self.btn_browse_iso.pack(side="left", padx=(0, 5))
        
        self.btn_rescan = ttk.Button(btn_frame, text="Rescan",
                                    command=self._scan_for_iso)
        self.btn_rescan.pack(side="left", padx=(0, 5))
        
        self.btn_download_iso = ttk.Button(btn_frame, text="Download ISO...",
                                          command=self._start_download)
        self.btn_download_iso.pack(side="left")
        self.btn_download_iso.pack_forget()
        
        features_section = self._create_section(self.step1_frame, "Included Features")
        
        features_frame = tk.Frame(features_section, bg="white")
        features_frame.pack(fill="x", pady=(8, 0))
        
        left_col = tk.Frame(features_frame, bg="white")
        left_col.pack(side="left", fill="both", expand=True)
        
        right_col = tk.Frame(features_frame, bg="white")
        right_col.pack(side="left", fill="both", expand=True)
        
        for i, feature in enumerate(FEATURES):
            col = left_col if i < 4 else right_col
            f_frame = tk.Frame(col, bg="white")
            f_frame.pack(anchor="w", pady=1)
            
            check = tk.Label(f_frame, text="✓", font=("Segoe UI", 10, "bold"),
                           bg="white", fg="#0078D7")
            check.pack(side="left")
            
            lbl = tk.Label(f_frame, text=f" {feature}", font=("Segoe UI", 9), bg="white")
            lbl.pack(side="left")
        
        folder_section = self._create_section(self.step1_frame, "Install Location")
        
        path_frame = tk.Frame(folder_section, bg="#f5f5f5")
        path_frame.pack(fill="x", pady=(8, 5))
        
        self.folder_label = tk.Label(path_frame, text=self.install_folder,
                                    font=("Consolas", 9), bg="#f5f5f5", 
                                    wraplength=400, justify="left")
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
                                    bg="white", fg="#0078D7")
        self.progress_pct.pack()
        
        self.progress_bar = ttk.Progressbar(center_frame, length=400, mode="determinate",
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
                              font=("Segoe UI", 18), bg="white", fg="#0078D7")
        success_lbl.pack(pady=10)
        
        path_section = self._create_section(self.step3_frame, "ISO File")
        
        self.final_iso_path_label = tk.Label(path_section, text="",
                                            font=("Consolas", 9), bg="#f5f5f5",
                                            wraplength=450, justify="left")
        self.final_iso_path_label.pack(fill="x", padx=8, pady=6)
        
        hash_section = self._create_section(self.step3_frame, "SHA256 Checksum")
        
        self.hash_label = tk.Label(hash_section, text="",
                                  font=("Consolas", 8), bg="#f5f5f5",
                                  wraplength=450)
        self.hash_label.pack(fill="x", padx=8, pady=6)
        
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
            if self.iso_path:
                self.btn_start.configure(text="Install ISO", state="normal")
            else:
                self.btn_start.configure(text="Install ISO", state="disabled")
        elif step == 2:
            self.step2_frame.pack(fill="both", expand=True)
            self.btn_start.configure(text="Installing...", state="disabled")
        elif step == 3:
            self.step3_frame.pack(fill="both", expand=True)
            self.btn_start.configure(text="Open Folder", state="normal",
                                    command=self._open_folder)
            self.btn_cancel.configure(text="Close")
    
    def _scan_for_iso(self):
        """Scan for ISO file in common locations"""
        self.iso_status_label.configure(text="Scanning for ISO...", fg="#888888")
        self.iso_path_label.configure(text="")
        self.btn_download_iso.pack_forget()
        self.root.update()
        
        iso_path, manifest_data, source = OfflineISOLocator.find_iso("freemium")
        
        if iso_path:
            self.iso_path = iso_path
            self.manifest_data = manifest_data
            self.iso_source = source
            
            self.iso_status_label.configure(
                text=f"✓ ISO found: {source}",
                fg="#28a745"
            )
            self.iso_path_label.configure(text=iso_path)
            self.btn_start.configure(state="normal")
            self.btn_download_iso.pack_forget()
        else:
            self.iso_path = ""
            self.manifest_data = None
            self.iso_source = ""
            
            self.iso_status_label.configure(
                text="✗ No ISO found locally. Browse for ISO or download from Aegis servers.",
                fg="#dc3545"
            )
            self.iso_path_label.configure(text="")
            self.btn_start.configure(state="disabled")
            self.btn_download_iso.pack(side="left")
    
    def _start_download(self):
        """Prompt user for download location and start download"""
        download_dir = filedialog.askdirectory(
            title="Select Download Location",
            initialdir=str(DEFAULT_DOWNLOAD_DIR.parent)
        )
        
        if not download_dir:
            download_dir = str(DEFAULT_DOWNLOAD_DIR)
        
        destination = os.path.join(download_dir, ISO_FILENAME)
        
        if os.path.exists(destination):
            if not messagebox.askyesno("File Exists",
                                       f"ISO already exists at:\n{destination}\n\nReplace it?"):
                self.iso_path = destination
                self.iso_source = "Existing download"
                self.iso_status_label.configure(
                    text=f"✓ Using existing ISO",
                    fg="#28a745"
                )
                self.iso_path_label.configure(text=destination)
                self.btn_start.configure(state="normal")
                self.btn_download_iso.pack_forget()
                return
        
        self.cancel_operation = False
        self.is_downloading = True
        self._show_step(2)
        self.progress_text.configure(text="Starting download...")
        
        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(destination,),
            daemon=True
        )
        self.download_thread.start()
    
    def _download_worker(self, destination):
        """Background worker for ISO download"""
        def progress_callback(pct, text, speed):
            self._update_progress(pct if pct >= 0 else 0, text, speed)
        
        self.iso_downloader = ISODownloader(progress_callback=progress_callback)
        
        success, message, sha256_hash = self.iso_downloader.download(
            url=ISO_DOWNLOAD_URLS["primary"],
            destination=destination,
            fallback_url=ISO_DOWNLOAD_URLS["fallback"],
            checksum_url=ISO_CHECKSUM_URL
        )
        
        if success:
            self.iso_path = destination
            self.iso_hash = sha256_hash
            self.iso_source = "Downloaded from Aegis servers"
            self.is_downloading = False
            self._download_complete(destination, sha256_hash)
        else:
            self.is_downloading = False
            if not self.cancel_operation:
                self._show_download_error(message)
    
    def _download_complete(self, dest_path, sha256_hash):
        """Handle successful download completion"""
        def complete():
            self.final_iso_path_label.configure(text=dest_path)
            self.hash_label.configure(text=sha256_hash)
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
        self.progress_pct.configure(fg="#0078D7")
        self.progress_text.configure(fg="#666666")
        download_dir = str(DEFAULT_DOWNLOAD_DIR)
        destination = os.path.join(download_dir, ISO_FILENAME)
        
        self.cancel_operation = False
        self.is_downloading = True
        
        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(destination,),
            daemon=True
        )
        self.download_thread.start()
    
    def _go_back(self):
        """Go back to step 1"""
        self._show_step(1)
        self.btn_cancel.configure(text="Cancel", command=self._on_cancel)
    
    def _browse_iso(self):
        """Browse for ISO file manually"""
        iso_file = filedialog.askopenfilename(
            title="Select Aegis OS Freemium ISO",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")],
            initialdir=str(Path.home() / "Downloads")
        )
        
        if iso_file:
            self.iso_path = iso_file
            self.iso_source = "Manual selection"
            self.manifest_data = None
            
            self.iso_status_label.configure(
                text="✓ ISO selected manually",
                fg="#28a745"
            )
            self.iso_path_label.configure(text=iso_file)
            self.btn_start.configure(state="normal")
    
    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.install_folder,
                                        title="Select Install Location")
        if folder:
            self.install_folder = folder
            self.folder_label.configure(text=folder)
    
    def _start_install(self):
        if not self.iso_path:
            messagebox.showerror("No ISO", "No ISO file found. Please browse for one.")
            return
        
        self.cancel_operation = False
        self._show_step(2)
        
        self.copy_thread = threading.Thread(target=self._install_worker, daemon=True)
        self.copy_thread.start()
    
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
            
            if self.manifest_data and self.manifest_data.get("sha256"):
                expected = self.manifest_data["sha256"].upper()
                if is_placeholder_checksum(expected):
                    self._update_progress(3, "Checksum verification skipped (development mode)", "")
                elif source_hash != expected:
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
    
    def _calculate_sha256(self, filepath):
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _update_progress(self, pct, text, speed):
        def update():
            self.progress_pct.configure(text=f"{pct}%")
            self.progress_bar["value"] = pct
            self.progress_text.configure(text=text)
            self.progress_speed.configure(text=speed)
        
        self.root.after(0, update)
    
    def _install_complete(self, dest_path):
        def complete():
            self.final_iso_path_label.configure(text=dest_path)
            self.hash_label.configure(text=self.iso_hash)
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
        self.progress_pct.configure(fg="#0078D7")
        self.progress_text.configure(fg="#666666")
        self._start_install()
    
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
    app = AegisFreemiumInstaller()
    app.run()


if __name__ == "__main__":
    main()
