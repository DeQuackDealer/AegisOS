#!/usr/bin/env python3
"""
Aegis OS Media Creation Tool v3.0.0
Like Windows Media Creation Tool - downloads official Aegis OS ISOs

Usage:
1. Run the executable
2. Enter your license key (or select Freemium)
3. Tool validates and downloads the correct ISO
4. Flash to USB with Balena Etcher
"""
from __future__ import annotations

import os
import sys
import json
import hashlib
import threading
import urllib.request
import urllib.error
import ssl
import certifi
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Optional, Tuple

def get_resource_path(filename: str) -> str:
    """Get the path to a bundled resource file."""
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

def get_app_dir() -> str:
    """Get the directory where the app is running from."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

TKINTER_AVAILABLE = False
tk: Any = None
ttk: Any = None
filedialog: Any = None
messagebox: Any = None

try:
    import tkinter as _tk
    from tkinter import ttk as _ttk, filedialog as _filedialog, messagebox as _messagebox
    tk = _tk
    ttk = _ttk
    filedialog = _filedialog
    messagebox = _messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    pass

VERSION = "3.0.0"
APP_NAME = "Aegis OS Media Creation Tool"

EDITIONS = {
    "freemium": {
        "name": "Aegis OS Freemium",
        "description": "Free edition with essential tools",
        "size_mb": 2800,
        "requires_license": False
    },
    "basic": {
        "name": "Aegis OS Basic",
        "description": "Full desktop experience - $69",
        "size_mb": 3200,
        "requires_license": True
    },
    "gamer": {
        "name": "Aegis OS Gamer",
        "description": "Optimized for gaming - $69",
        "size_mb": 4500,
        "requires_license": True
    },
    "workplace": {
        "name": "Aegis OS Workplace",
        "description": "Business productivity - $49",
        "size_mb": 3400,
        "requires_license": True
    },
    "ai-developer": {
        "name": "Aegis OS AI Developer",
        "description": "AI/ML development - $89",
        "size_mb": 5200,
        "requires_license": True
    },
    "gamer-ai": {
        "name": "Aegis OS Gamer+AI",
        "description": "Gaming + AI features - $129",
        "size_mb": 6000,
        "requires_license": True
    },
    "server": {
        "name": "Aegis OS Server",
        "description": "Server deployment - $129",
        "size_mb": 2400,
        "requires_license": True
    }
}

DOWNLOAD_BASE_URL = "https://download.aegis-os.com/releases/v3.0.0"
ACTIVATION_SERVER = "https://api.aegis-os.com/v1"


class LicenseValidator:
    """Validates license keys with the Aegis server."""
    
    LICENSE_PREFIXES = {
        "AEGIS-BASIC": "basic",
        "AEGIS-GAMER": "gamer",
        "AEGIS-WORK": "workplace",
        "AEGIS-AIDEV": "ai-developer",
        "AEGIS-GMAI": "gamer-ai",
        "AEGIS-SERV": "server"
    }
    
    @staticmethod
    def get_ssl_context() -> ssl.SSLContext:
        """Get SSL context for HTTPS requests with proper certificate verification."""
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            return context
        except Exception:
            return ssl.create_default_context()
    
    @classmethod
    def validate_format(cls, license_key: str) -> tuple:
        """
        Validate license key format.
        Returns: (valid, edition_id, message)
        """
        if not license_key or not license_key.strip():
            return False, None, "Please enter a license key"
        
        key = license_key.strip().upper()
        
        for prefix, edition in cls.LICENSE_PREFIXES.items():
            if key.startswith(prefix):
                parts = key.split("-")
                if len(parts) == 5:
                    return True, edition, f"Valid format for {EDITIONS[edition]['name']}"
        
        return False, None, "Invalid license key format"
    
    @classmethod
    def validate_online(cls, license_key: str) -> tuple:
        """
        Validate license key with server.
        Returns: (valid, edition_id, message)
        """
        format_valid, edition, format_msg = cls.validate_format(license_key)
        if not format_valid:
            return False, None, format_msg
        
        try:
            url = f"{ACTIVATION_SERVER}/validate"
            data = json.dumps({
                "license_key": license_key.strip().upper(),
                "action": "validate"
            }).encode('utf-8')
            
            request = urllib.request.Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': f'AegisOS-MediaTool/{VERSION}'
                },
                method='POST'
            )
            
            context = cls.get_ssl_context()
            
            with urllib.request.urlopen(request, timeout=10, context=context) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get("valid"):
                    return True, result.get("edition", edition), "License validated successfully"
                else:
                    return False, None, result.get("message", "License validation failed")
                    
        except urllib.error.URLError:
            return False, None, "Cannot validate license - no internet connection. Please connect to the internet and try again."
        except Exception as e:
            return False, None, f"License validation failed: {str(e)[:50]}"


class ISODownloader:
    """Handles ISO download with progress tracking and checksum verification."""
    
    def __init__(self, edition_id: str, destination: str, progress_callback: Optional[Callable] = None, status_callback: Optional[Callable] = None):
        self.edition_id = edition_id
        self.destination = destination
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.cancelled = False
        self.download_url = f"{DOWNLOAD_BASE_URL}/aegis-os-{edition_id}-x86_64.iso"
        self.expected_size = EDITIONS.get(edition_id, {}).get("size_mb", 3000) * 1024 * 1024
        self.expected_checksum = self._load_expected_checksum()
    
    def _load_expected_checksum(self) -> Optional[str]:
        """Load expected SHA-256 checksum from manifest."""
        try:
            manifest_path = get_resource_path("manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                edition_key = self.edition_id.replace("-", "_")
                if self.edition_id == "ai-developer":
                    edition_key = "aidev"
                elif self.edition_id == "gamer-ai":
                    edition_key = "gamer_ai"
                edition_data = manifest.get("editions", {}).get(edition_key, {})
                checksum = edition_data.get("sha256")
                if checksum and not checksum.startswith("00000"):
                    return checksum
        except Exception:
            pass
        return None
    
    def cancel(self):
        """Cancel the download."""
        self.cancelled = True
    
    def update_status(self, message: str):
        """Update status message."""
        if self.status_callback:
            self.status_callback(message)
    
    def update_progress(self, percent: float, speed: str = ""):
        """Update progress bar."""
        if self.progress_callback:
            self.progress_callback(percent, speed)
    
    def download(self) -> tuple:
        """
        Download the ISO file.
        Returns: (success, message, filepath)
        """
        try:
            self.update_status(f"Connecting to download server...")
            self.update_progress(0, "Connecting...")
            
            context = LicenseValidator.get_ssl_context()
            
            request = urllib.request.Request(
                self.download_url,
                headers={'User-Agent': f'AegisOS-MediaTool/{VERSION}'}
            )
            
            try:
                response = urllib.request.urlopen(request, timeout=30, context=context)
                total_size = int(response.headers.get('Content-Length', self.expected_size))
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return False, "ISO file not found on server. The download server may not have this edition available yet. Please check aegis-os.com for updates.", None
                return False, f"Download failed: HTTP {e.code}", None
            except urllib.error.URLError as e:
                return False, f"Cannot connect to download server. Please check your internet connection.\n\nError: {str(e.reason)}", None
            
            self.update_status(f"Downloading {total_size / (1024*1024):.0f} MB...")
            
            downloaded = 0
            start_time = datetime.now()
            chunk_size = 1024 * 1024
            
            with open(self.destination, 'wb') as f:
                while not self.cancelled:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed > 0:
                        speed = downloaded / elapsed
                        speed_str = f"{speed / (1024*1024):.1f} MB/s"
                        eta = (total_size - downloaded) / speed if speed > 0 else 0
                        eta_str = f" - ETA: {int(eta)}s" if eta > 0 else ""
                    else:
                        speed_str = "Calculating..."
                        eta_str = ""
                    
                    percent = (downloaded / total_size) * 100
                    self.update_progress(percent, f"{speed_str}{eta_str}")
                    self.update_status(f"Downloaded {downloaded / (1024*1024):.0f} / {total_size / (1024*1024):.0f} MB")
            
            if self.cancelled:
                if os.path.exists(self.destination):
                    os.remove(self.destination)
                return False, "Download cancelled", None
            
            self.update_progress(100, "Verifying...")
            self.update_status("Verifying download integrity...")
            
            if self.expected_checksum:
                actual_checksum = self._calculate_checksum(self.destination)
                if actual_checksum != self.expected_checksum.lower():
                    os.remove(self.destination)
                    return False, "Download verification failed - file may be corrupted. Please try again.", None
                self.update_status("Download verified successfully!")
            else:
                self.update_status("Download complete! (checksum not available)")
            
            return True, "ISO downloaded successfully", self.destination
            
        except Exception as e:
            if os.path.exists(self.destination):
                os.remove(self.destination)
            return False, f"Download error: {str(e)}", None
    
    def _calculate_checksum(self, filepath: str) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest().lower()


class MediaCreationToolGUI:
    """Main GUI application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.current_frame = None
        self.license_key = tk.StringVar()
        self.selected_edition = tk.StringVar(value="freemium")
        self.save_path = tk.StringVar()
        self.downloader = None
        self.download_thread = None
        
        self._setup_styles()
        self._show_welcome_screen()
    
    def _setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Big.TButton', font=('Segoe UI', 11), padding=10)
    
    def _clear_frame(self):
        """Clear the current frame."""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ttk.Frame(self.root, padding=20)
        self.current_frame.pack(fill='both', expand=True)
    
    def _show_welcome_screen(self):
        """Show the welcome/start screen."""
        self._clear_frame()
        
        ttk.Label(
            self.current_frame,
            text="Aegis OS Media Creation Tool",
            style='Title.TLabel'
        ).pack(pady=(20, 5))
        
        ttk.Label(
            self.current_frame,
            text="Download official Aegis OS installation media",
            style='Subtitle.TLabel'
        ).pack(pady=(0, 30))
        
        ttk.Label(
            self.current_frame,
            text="Based on Arch Linux | Version 3.0.0",
            foreground='gray'
        ).pack(pady=(0, 40))
        
        btn_frame = ttk.Frame(self.current_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="Download Freemium Edition (Free)",
            style='Big.TButton',
            command=lambda: self._start_download("freemium"),
            width=35
        ).pack(pady=10)
        
        ttk.Button(
            btn_frame,
            text="I Have a License Key",
            style='Big.TButton',
            command=self._show_license_screen,
            width=35
        ).pack(pady=10)
        
        ttk.Label(
            self.current_frame,
            text="Freemium includes essential tools. Paid editions unlock\n"
                 "premium features like gaming optimization, AI tools, and more.",
            foreground='gray',
            justify='center'
        ).pack(pady=30)
    
    def _show_license_screen(self):
        """Show license key entry screen."""
        self._clear_frame()
        
        ttk.Label(
            self.current_frame,
            text="Enter Your License Key",
            style='Title.TLabel'
        ).pack(pady=(20, 30))
        
        ttk.Label(
            self.current_frame,
            text="Enter your license key to download your edition:"
        ).pack(pady=(0, 10))
        
        entry_frame = ttk.Frame(self.current_frame)
        entry_frame.pack(pady=10, fill='x', padx=50)
        
        self.license_entry = ttk.Entry(
            entry_frame,
            textvariable=self.license_key,
            font=('Consolas', 12),
            width=40
        )
        self.license_entry.pack(pady=10)
        self.license_entry.focus()
        
        ttk.Label(
            self.current_frame,
            text="Format: AEGIS-XXXXX-XXXX-XXXX-XXXX",
            foreground='gray'
        ).pack()
        
        self.validation_label = ttk.Label(
            self.current_frame,
            text="",
            foreground='gray'
        )
        self.validation_label.pack(pady=20)
        
        btn_frame = ttk.Frame(self.current_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="Validate & Download",
            style='Big.TButton',
            command=self._validate_and_download
        ).pack(side='left', padx=10)
        
        ttk.Button(
            btn_frame,
            text="Back",
            command=self._show_welcome_screen
        ).pack(side='left', padx=10)
    
    def _validate_and_download(self):
        """Validate the license key and start download."""
        key = self.license_key.get().strip()
        
        if not key:
            self.validation_label.config(text="Please enter a license key", foreground='red')
            return
        
        self.validation_label.config(text="Validating license...", foreground='blue')
        self.root.update()
        
        valid, edition, message = LicenseValidator.validate_online(key)
        
        if valid and edition:
            self.validation_label.config(
                text=f"Valid! Edition: {EDITIONS[edition]['name']}",
                foreground='green'
            )
            self.root.after(1000, lambda: self._start_download(edition))
        else:
            self.validation_label.config(text=message, foreground='red')
    
    def _start_download(self, edition_id: str):
        """Start the download process."""
        edition = EDITIONS.get(edition_id)
        if not edition:
            messagebox.showerror("Error", "Unknown edition")
            return
        
        default_filename = f"aegis-os-{edition_id}-{VERSION}.iso"
        
        save_path = filedialog.asksaveasfilename(
            title="Save ISO As",
            defaultextension=".iso",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if not save_path:
            return
        
        self.save_path.set(save_path)
        self._show_download_screen(edition_id)
    
    def _show_download_screen(self, edition_id: str):
        """Show the download progress screen."""
        self._clear_frame()
        
        edition = EDITIONS.get(edition_id, {})
        
        ttk.Label(
            self.current_frame,
            text=f"Downloading {edition.get('name', edition_id)}",
            style='Title.TLabel'
        ).pack(pady=(20, 10))
        
        ttk.Label(
            self.current_frame,
            text=f"Estimated size: {edition.get('size_mb', 3000)} MB",
            foreground='gray'
        ).pack(pady=(0, 30))
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.current_frame,
            variable=self.progress_var,
            maximum=100,
            length=500,
            mode='determinate'
        )
        self.progress_bar.pack(pady=20)
        
        self.progress_label = ttk.Label(
            self.current_frame,
            text="0%"
        )
        self.progress_label.pack()
        
        self.speed_label = ttk.Label(
            self.current_frame,
            text="Preparing download...",
            foreground='gray'
        )
        self.speed_label.pack(pady=10)
        
        self.status_label = ttk.Label(
            self.current_frame,
            text="Connecting...",
            foreground='blue'
        )
        self.status_label.pack(pady=20)
        
        self.cancel_btn = ttk.Button(
            self.current_frame,
            text="Cancel",
            command=self._cancel_download
        )
        self.cancel_btn.pack(pady=20)
        
        self.downloader = ISODownloader(
            edition_id,
            self.save_path.get(),
            progress_callback=self._update_progress,
            status_callback=self._update_status
        )
        
        self.download_thread = threading.Thread(target=self._run_download)
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def _update_progress(self, percent: float, speed: str):
        """Update progress bar (thread-safe)."""
        self.root.after(0, lambda: self._do_update_progress(percent, speed))
    
    def _do_update_progress(self, percent: float, speed: str):
        """Actually update progress (main thread)."""
        self.progress_var.set(percent)
        self.progress_label.config(text=f"{percent:.1f}%")
        self.speed_label.config(text=speed)
    
    def _update_status(self, message: str):
        """Update status label (thread-safe)."""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def _run_download(self) -> None:
        """Run the download in background thread."""
        if self.downloader is None:
            return
        success, message, filepath = self.downloader.download()
        self.root.after(0, lambda: self._download_complete(success, message, filepath))
    
    def _download_complete(self, success: bool, message: str, filepath: str):
        """Handle download completion."""
        if success:
            self._show_complete_screen(filepath)
        else:
            messagebox.showerror("Download Failed", message)
            self._show_welcome_screen()
    
    def _cancel_download(self):
        """Cancel the current download."""
        if self.downloader:
            self.downloader.cancel()
        self._show_welcome_screen()
    
    def _show_complete_screen(self, filepath: str):
        """Show download complete screen."""
        self._clear_frame()
        
        ttk.Label(
            self.current_frame,
            text="Download Complete!",
            style='Title.TLabel',
            foreground='green'
        ).pack(pady=(40, 20))
        
        ttk.Label(
            self.current_frame,
            text="Your Aegis OS ISO has been downloaded successfully.",
            style='Subtitle.TLabel'
        ).pack(pady=10)
        
        file_frame = ttk.Frame(self.current_frame)
        file_frame.pack(pady=20, fill='x', padx=40)
        
        ttk.Label(
            file_frame,
            text="Saved to:",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w')
        
        path_label = ttk.Label(
            file_frame,
            text=filepath,
            foreground='blue',
            wraplength=500
        )
        path_label.pack(anchor='w', pady=5)
        
        ttk.Label(
            self.current_frame,
            text="\nNext Steps:",
            style='Header.TLabel'
        ).pack(pady=(20, 10))
        
        steps = [
            "1. Download Balena Etcher from balena.io/etcher",
            "2. Insert a USB drive (8GB+ recommended)",
            "3. Open Etcher and select your ISO file",
            "4. Select your USB drive",
            "5. Click 'Flash!' and wait for completion",
            "6. Boot your computer from the USB drive"
        ]
        
        for step in steps:
            ttk.Label(
                self.current_frame,
                text=step,
                foreground='gray'
            ).pack(anchor='w', padx=60)
        
        btn_frame = ttk.Frame(self.current_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(
            btn_frame,
            text="Download Another",
            style='Big.TButton',
            command=self._show_welcome_screen
        ).pack(side='left', padx=10)
        
        ttk.Button(
            btn_frame,
            text="Exit",
            command=self.root.quit
        ).pack(side='left', padx=10)
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    if not TKINTER_AVAILABLE:
        print("ERROR: This application requires a graphical display.")
        print("Please run this on a system with a desktop environment.")
        print("\nIf you're on Linux without a display, set up X11 forwarding")
        print("or run on a system with a graphical desktop.")
        sys.exit(1)
    
    try:
        app = MediaCreationToolGUI()
        app.run()
    except tk.TclError as e:
        if "no display" in str(e).lower():
            print("ERROR: No display available.")
            print("This application requires a graphical desktop environment.")
        else:
            print(f"GUI Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
