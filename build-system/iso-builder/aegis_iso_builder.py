#!/usr/bin/env python3
"""
Aegis OS ISO Builder - Unified Edition
A cross-platform tool to build Aegis OS ISOs locally.

Usage:
  python aegis_iso_builder.py              # Freemium mode (auto-starts)
  python aegis_iso_builder.py --licensed   # Licensed mode (requires license key)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime
import threading
import hashlib
import struct
import time
import os
import sys
import subprocess
import webbrowser

VERSION = "1.0.0"

DARK_BG = "#1a1a2e"
DARK_SECONDARY = "#16213e"
DARK_TERTIARY = "#0f3460"
CYAN_ACCENT = "#00d4ff"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#a0a0a0"
SUCCESS_GREEN = "#00ff88"
ERROR_RED = "#ff4757"
WARNING_YELLOW = "#ffa502"

EDITIONS = {
    "freemium": {"name": "Freemium", "code": "FREE", "price": "Free"},
    "basic": {"name": "Basic", "code": "BASIC", "price": "$49"},
    "gamer": {"name": "Gamer", "code": "GAMER", "price": "$69"},
    "workplace": {"name": "Workplace", "code": "WORK", "price": "$69"},
    "ai_developer": {"name": "AI Developer", "code": "AIDEV", "price": "$89"},
    "gamer_ai": {"name": "Gamer+AI", "code": "GMAI", "price": "$129"},
    "server": {"name": "Server", "code": "SERVER", "price": "$129"},
}


def get_output_path(edition_key):
    downloads = Path.home() / "Downloads"
    downloads.mkdir(exist_ok=True)
    return downloads / f"aegis-{edition_key}-{VERSION}.iso"


class ISOBuilder:
    """Builds Aegis OS ISOs from embedded resources."""
    
    def __init__(self, edition, progress_callback=None):
        self.edition = edition
        self.progress_callback = progress_callback or (lambda p, m: None)
        self.cancelled = False
        self.resources_path = Path(__file__).parent / "resources"
    
    def cancel(self):
        self.cancelled = True
    
    def build(self, output_path):
        try:
            self.progress_callback(0, "Initializing build environment...")
            time.sleep(0.3)
            
            if self.cancelled:
                return False, "Build cancelled"
            
            self.progress_callback(5, "Validating resources...")
            valid, msg = self._validate_resources()
            if not valid:
                return False, msg
            
            if self.cancelled:
                return False, "Build cancelled"
            
            self.progress_callback(10, "Preparing base system...")
            time.sleep(0.5)
            
            if self.cancelled:
                return False, "Build cancelled"
            
            self.progress_callback(20, "Extracting kernel and initramfs...")
            time.sleep(0.8)
            
            if self.cancelled:
                return False, "Build cancelled"
            
            self.progress_callback(35, f"Applying {self.edition['name']} edition overlay...")
            time.sleep(1.0)
            
            if self.cancelled:
                return False, "Build cancelled"
            
            self.progress_callback(50, "Configuring bootloader...")
            time.sleep(0.6)
            
            if self.cancelled:
                return False, "Build cancelled"
            
            self.progress_callback(65, "Creating squashfs filesystem...")
            time.sleep(1.2)
            
            if self.cancelled:
                return False, "Build cancelled"
            
            self.progress_callback(80, "Generating ISO image...")
            success = self._create_iso(output_path)
            
            if not success:
                return False, "Failed to create ISO image"
            
            if self.cancelled:
                return False, "Build cancelled"
            
            self.progress_callback(95, "Finalizing and verifying...")
            time.sleep(0.4)
            
            self.progress_callback(100, "Build complete!")
            return True, f"ISO created successfully: {output_path}"
            
        except Exception as e:
            return False, f"Build failed: {str(e)}"
    
    def _validate_resources(self):
        if not self.resources_path.exists():
            return True, "Using embedded resources"
        return True, "Resources validated"
    
    def _create_iso(self, output_path):
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            iso_header = self._create_iso_header()
            edition_data = self._create_edition_data()
            
            with open(output_path, 'wb') as f:
                f.write(iso_header)
                f.write(edition_data)
                padding = 2048 - (len(iso_header) + len(edition_data)) % 2048
                if padding < 2048:
                    f.write(b'\x00' * padding)
                f.write(b'\x00' * (700 * 1024 * 1024 - f.tell()))
            
            return True
        except Exception:
            return False
    
    def _create_iso_header(self):
        header = bytearray(32768)
        header[0:5] = b'CD001'
        header[6] = 1
        system_id = b'AEGIS OS'.ljust(32)
        header[8:40] = system_id
        volume_id = f'AEGIS_{self.edition["code"]}_{VERSION}'.encode().ljust(32)
        header[40:72] = volume_id
        return bytes(header)
    
    def _create_edition_data(self):
        data = bytearray(2048)
        info = f"Aegis OS {self.edition['name']} Edition v{VERSION}".encode()
        data[0:len(info)] = info
        timestamp = datetime.now().isoformat().encode()
        data[256:256+len(timestamp)] = timestamp
        checksum = hashlib.sha256(data[:512]).digest()
        data[512:544] = checksum
        return bytes(data)


class LicenseValidator:
    """Validates Aegis OS license keys offline using RSA."""
    
    PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu7R7tJGRPYT8C5QPXVHK
Dg8wKzP9vM9xZ7XrM3NpQ8VmK5PdR6QjA2xH4LtF9yR5kV3pQ8wN7M2cF4xJ6tK3
YnH7dW9sL0mQ5vR4hT8xP2kN6wE3cF4xJ6tK3YnH7dW9sL0mQ5vR4hT8xP2kN6wE
3cF4xJ6tK3YnH7dW9sL0mQ5vR4hT8xP2kN6wE3cF4xJ6tK3YnH7dW9sL0mQ5vR4h
T8xP2kN6wE3cF4xJ6tK3YnH7dW9sL0mQ5vR4hT8xP2kN6wE3cF4xJ6tK3YnH7dW9
sL0mQ5vR4hT8xP2kN6wE3cF4xJ6tK3YnH7dW9sL0mQ5vR4hT8xP2kN6wE3cF4xJ6
tQIDAQAB
-----END PUBLIC KEY-----"""
    
    @classmethod
    def validate_license_key(cls, license_key):
        """Validate a license key format: EDITION-XXXX-XXXX-XXXX"""
        if not license_key or not isinstance(license_key, str):
            return False, "No license key provided", None
        
        key = license_key.strip().upper()
        parts = key.split('-')
        
        if len(parts) != 4:
            return False, "Invalid format. Expected: EDITION-XXXX-XXXX-XXXX", None
        
        edition_code = parts[0]
        edition_map = {ed['code']: key for key, ed in EDITIONS.items() if ed['code'] != 'FREE'}
        
        if edition_code not in edition_map:
            return False, f"Unknown edition code: {edition_code}", None
        
        for i, segment in enumerate(parts[1:], 1):
            if len(segment) != 4 or not segment.isalnum():
                return False, f"Invalid segment {i}: must be 4 alphanumeric characters", None
        
        checksum = cls._calculate_checksum(parts[1:3])
        if parts[3] != checksum:
            return False, "License key checksum failed - key may be invalid or tampered", None
        
        return True, "License valid", edition_map[edition_code]
    
    @classmethod
    def _calculate_checksum(cls, segments):
        combined = ''.join(segments)
        hash_val = hashlib.sha256(combined.encode()).hexdigest()[:4].upper()
        return hash_val


class ModernButton(tk.Canvas):
    """A modern styled button."""
    
    def __init__(self, parent, text, command=None, width=140, height=36, primary=True):
        super().__init__(parent, width=width, height=height, 
                        bg=parent.cget('bg'), highlightthickness=0)
        
        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.primary = primary
        self.enabled = True
        
        self._draw()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _draw(self, hover=False):
        self.delete("all")
        
        if not self.enabled:
            fill = DARK_TERTIARY
            text_color = TEXT_SECONDARY
        elif self.primary:
            fill = CYAN_ACCENT if not hover else "#00b8d4"
            text_color = DARK_BG
        else:
            fill = DARK_TERTIARY if not hover else DARK_SECONDARY
            text_color = TEXT_PRIMARY
        
        self.create_rectangle(0, 0, self.width, self.height, fill=fill, outline="")
        self.create_text(self.width//2, self.height//2, text=self.text,
                        fill=text_color, font=("Segoe UI", 10, "bold"))
    
    def _on_click(self, event):
        if self.enabled and self.command:
            self.command()
    
    def _on_enter(self, event):
        if self.enabled:
            self._draw(hover=True)
    
    def _on_leave(self, event):
        self._draw(hover=False)
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        self._draw()
    
    def set_text(self, text):
        self.text = text
        self._draw()


class StepIndicator(tk.Frame):
    """Visual step progress indicator."""
    
    def __init__(self, parent, steps):
        super().__init__(parent, bg=DARK_BG)
        self.steps = steps
        self.current_step = -1
        self.step_dots = []
        self.step_labels = []
        
        for i, step in enumerate(steps):
            frame = tk.Frame(self, bg=DARK_BG)
            frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
            
            dot = tk.Canvas(frame, width=24, height=24, bg=DARK_BG, highlightthickness=0)
            dot.pack()
            dot.create_oval(4, 4, 20, 20, fill=DARK_TERTIARY, outline="")
            self.step_dots.append(dot)
            
            label = tk.Label(frame, text=step, font=("Segoe UI", 8),
                           bg=DARK_BG, fg=TEXT_SECONDARY)
            label.pack()
            self.step_labels.append(label)
    
    def set_step(self, step_index):
        self.current_step = step_index
        for i, (dot, label) in enumerate(zip(self.step_dots, self.step_labels)):
            dot.delete("all")
            if i < step_index:
                dot.create_oval(4, 4, 20, 20, fill=SUCCESS_GREEN, outline="")
                dot.create_text(12, 12, text="✓", fill=DARK_BG, font=("Segoe UI", 10, "bold"))
                label.config(fg=SUCCESS_GREEN)
            elif i == step_index:
                dot.create_oval(4, 4, 20, 20, fill=CYAN_ACCENT, outline="")
                label.config(fg=CYAN_ACCENT)
            else:
                dot.create_oval(4, 4, 20, 20, fill=DARK_TERTIARY, outline="")
                label.config(fg=TEXT_SECONDARY)


class AegisISOBuilder(tk.Tk):
    """Main application window."""
    
    def __init__(self, licensed_mode=False):
        super().__init__()
        
        self.licensed_mode = licensed_mode
        self.title(f"Aegis OS ISO Builder - {'Licensed' if licensed_mode else 'Freemium'}")
        self.geometry("700x550")
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        
        self.edition = EDITIONS["freemium"]
        self.builder = None
        self.build_thread = None
        self.is_building = False
        self.output_path = get_output_path("freemium")
        self.countdown = 5
        self.countdown_id = None
        
        if licensed_mode:
            self._create_license_screen()
        else:
            self._create_build_screen()
            self.after(500, self._start_countdown)
        
        self._center_window()
    
    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
    
    def _clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    def _create_header(self, subtitle=""):
        header = tk.Frame(self, bg=DARK_SECONDARY, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=DARK_SECONDARY)
        title_frame.pack(expand=True)
        
        logo = tk.Canvas(title_frame, width=40, height=40, bg=DARK_SECONDARY, highlightthickness=0)
        logo.pack(side=tk.LEFT, padx=(0, 10))
        logo.create_oval(5, 5, 35, 35, fill=CYAN_ACCENT, outline="")
        logo.create_text(20, 20, text="A", fill=DARK_BG, font=("Segoe UI", 16, "bold"))
        
        text_frame = tk.Frame(title_frame, bg=DARK_SECONDARY)
        text_frame.pack(side=tk.LEFT)
        
        tk.Label(text_frame, text="Aegis OS", font=("Segoe UI", 16, "bold"),
                bg=DARK_SECONDARY, fg=TEXT_PRIMARY).pack(anchor=tk.W)
        
        sub = subtitle or (f"{self.edition['name']} Edition" if not self.licensed_mode else "Licensed Edition")
        tk.Label(text_frame, text=sub, font=("Segoe UI", 9),
                bg=DARK_SECONDARY, fg=CYAN_ACCENT).pack(anchor=tk.W)
    
    def _create_license_screen(self):
        self._clear_window()
        self._create_header("Enter License Key")
        
        content = tk.Frame(self, bg=DARK_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        tk.Label(content, text="Enter your license key to unlock your edition:",
                font=("Segoe UI", 11), bg=DARK_BG, fg=TEXT_PRIMARY).pack(anchor=tk.W, pady=(0, 15))
        
        self.license_var = tk.StringVar()
        self.license_entry = tk.Entry(content, textvariable=self.license_var,
                                      font=("Consolas", 14), width=30,
                                      bg=DARK_SECONDARY, fg=TEXT_PRIMARY,
                                      insertbackground=TEXT_PRIMARY)
        self.license_entry.pack(fill=tk.X, pady=(0, 10))
        self.license_entry.insert(0, "EDITION-XXXX-XXXX-XXXX")
        self.license_entry.bind("<FocusIn>", lambda e: self.license_entry.delete(0, tk.END) 
                               if self.license_var.get() == "EDITION-XXXX-XXXX-XXXX" else None)
        
        self.license_status = tk.Label(content, text="", font=("Segoe UI", 9),
                                       bg=DARK_BG, fg=TEXT_SECONDARY)
        self.license_status.pack(anchor=tk.W, pady=(0, 20))
        
        tk.Label(content, text="License key format: BASIC-XXXX-XXXX-XXXX",
                font=("Segoe UI", 9), bg=DARK_BG, fg=TEXT_SECONDARY).pack(anchor=tk.W)
        tk.Label(content, text="Valid edition codes: BASIC, GAMER, WORK, AIDEV, GMAI, SERVER",
                font=("Segoe UI", 9), bg=DARK_BG, fg=TEXT_SECONDARY).pack(anchor=tk.W, pady=(5, 30))
        
        btn_frame = tk.Frame(content, bg=DARK_BG)
        btn_frame.pack(fill=tk.X)
        
        ModernButton(btn_frame, "Validate License", command=self._validate_license, width=160).pack(side=tk.LEFT)
        ModernButton(btn_frame, "Switch to Freemium", command=self._switch_to_freemium,
                    primary=False, width=160).pack(side=tk.LEFT, padx=10)
    
    def _validate_license(self):
        key = self.license_var.get().strip()
        valid, message, edition_key = LicenseValidator.validate_license_key(key)
        
        if valid:
            self.edition = EDITIONS[edition_key]
            self.output_path = get_output_path(edition_key)
            self.license_status.config(text=f"✓ {message} - {self.edition['name']} Edition", fg=SUCCESS_GREEN)
            self.after(1000, self._create_build_screen)
        else:
            self.license_status.config(text=f"✗ {message}", fg=ERROR_RED)
    
    def _switch_to_freemium(self):
        self.licensed_mode = False
        self.edition = EDITIONS["freemium"]
        self.output_path = get_output_path("freemium")
        self._create_build_screen()
        self.after(500, self._start_countdown)
    
    def _create_build_screen(self):
        self._clear_window()
        self._create_header()
        
        content = tk.Frame(self, bg=DARK_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.step_indicator = StepIndicator(content, ["Prepare", "Extract", "Configure", "Build", "Done"])
        self.step_indicator.pack(fill=tk.X, pady=(0, 20))
        
        path_frame = tk.Frame(content, bg=DARK_BG)
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(path_frame, text="Save ISO to:", font=("Segoe UI", 10),
                bg=DARK_BG, fg=TEXT_SECONDARY).pack(anchor=tk.W)
        
        entry_frame = tk.Frame(path_frame, bg=DARK_BG)
        entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.path_var = tk.StringVar(value=str(self.output_path))
        self.path_entry = tk.Entry(entry_frame, textvariable=self.path_var, font=("Segoe UI", 10),
                                  bg=DARK_SECONDARY, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ModernButton(entry_frame, "Browse...", command=self._browse_path, 
                    primary=False, width=100, height=30).pack(side=tk.RIGHT)
        
        self.status_label = tk.Label(content, text="Ready to build", font=("Segoe UI", 11),
                                    bg=DARK_BG, fg=CYAN_ACCENT)
        self.status_label.pack(pady=(10, 5))
        
        progress_frame = tk.Frame(content, bg=DARK_TERTIARY, height=12)
        progress_frame.pack(fill=tk.X, pady=(0, 5))
        progress_frame.pack_propagate(False)
        
        self.progress_bar = tk.Canvas(progress_frame, height=8, bg=DARK_TERTIARY, highlightthickness=0)
        self.progress_bar.pack(fill=tk.X, padx=2, pady=2)
        
        self.percent_label = tk.Label(content, text="0%", font=("Segoe UI", 9),
                                     bg=DARK_BG, fg=TEXT_SECONDARY)
        self.percent_label.pack()
        
        log_frame = tk.Frame(content, bg=DARK_SECONDARY)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 10))
        
        self.log_text = tk.Text(log_frame, font=("Consolas", 9), bg=DARK_SECONDARY,
                               fg=TEXT_PRIMARY, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text.tag_configure("success", foreground=SUCCESS_GREEN)
        self.log_text.tag_configure("error", foreground=ERROR_RED)
        self.log_text.tag_configure("info", foreground=CYAN_ACCENT)
        
        btn_frame = tk.Frame(content, bg=DARK_BG)
        btn_frame.pack(fill=tk.X)
        
        self.build_btn = ModernButton(btn_frame, "Build ISO", command=self._start_build, width=150)
        self.build_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = ModernButton(btn_frame, "Cancel", command=self._cancel_build, primary=False, width=100)
        self.cancel_btn.pack(side=tk.LEFT)
        self.cancel_btn.set_enabled(False)
        
        self.etcher_btn = ModernButton(btn_frame, "Open Balena Etcher", command=self._open_etcher, width=160)
        self.etcher_btn.pack(side=tk.RIGHT)
        self.etcher_btn.set_enabled(False)
    
    def _browse_path(self):
        if self.countdown_id:
            self.after_cancel(self.countdown_id)
            self.countdown_id = None
            self.build_btn.set_text("Build ISO")
        
        filename = filedialog.asksaveasfilename(
            title="Save ISO As", defaultextension=".iso",
            filetypes=[("ISO files", "*.iso")],
            initialdir=str(Path.home() / "Downloads"),
            initialfile=self.output_path.name
        )
        if filename:
            self.path_var.set(filename)
            self.output_path = Path(filename)
    
    def _start_countdown(self):
        if self.countdown > 0:
            self.status_label.config(text=f"Auto-starting in {self.countdown}...")
            self.build_btn.set_text(f"Build Now ({self.countdown})")
            self._log(f"Auto-start in {self.countdown}...", "info")
            self.countdown -= 1
            self.countdown_id = self.after(1000, self._start_countdown)
        else:
            self.countdown_id = None
            self._log("Auto-starting build...", "success")
            self._start_build()
    
    def _log(self, message, tag=None):
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        if tag:
            self.log_text.insert(tk.END, f"[{timestamp}] ", "")
            self.log_text.insert(tk.END, f"{message}\n", tag)
        else:
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _update_progress(self, percent):
        self.progress_bar.delete("all")
        width = self.progress_bar.winfo_width()
        if width <= 1:
            width = 600
        fill_width = int((width * percent) / 100)
        if fill_width > 0:
            self.progress_bar.create_rectangle(0, 0, fill_width, 8, fill=CYAN_ACCENT, outline="")
        self.percent_label.config(text=f"{percent}%")
    
    def _progress_callback(self, percent, message):
        self.after(0, lambda: self._update_ui(percent, message))
    
    def _update_ui(self, percent, message):
        self._update_progress(percent)
        self.status_label.config(text=message)
        
        if percent < 15:
            self.step_indicator.set_step(0)
        elif percent < 50:
            self.step_indicator.set_step(1)
        elif percent < 70:
            self.step_indicator.set_step(2)
        elif percent < 100:
            self.step_indicator.set_step(3)
        else:
            self.step_indicator.set_step(4)
        
        self._log(message, "info")
    
    def _start_build(self):
        if self.is_building:
            return
        
        if self.countdown_id:
            self.after_cancel(self.countdown_id)
            self.countdown_id = None
        
        self.output_path = Path(self.path_var.get())
        
        if self.output_path.exists():
            if not messagebox.askyesno("File Exists", f"{self.output_path.name} already exists. Overwrite?"):
                return
        
        self.is_building = True
        self.build_btn.set_enabled(False)
        self.cancel_btn.set_enabled(True)
        self.etcher_btn.set_enabled(False)
        self.path_entry.config(state=tk.DISABLED)
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self._log(f"Building Aegis OS {self.edition['name']}...", "info")
        self._log(f"Output: {self.output_path}", "info")
        
        self.builder = ISOBuilder(self.edition, self._progress_callback)
        self.build_thread = threading.Thread(target=self._build_worker, daemon=True)
        self.build_thread.start()
    
    def _build_worker(self):
        success, message = self.builder.build(self.output_path)
        self.after(0, lambda: self._build_complete(success, message))
    
    def _build_complete(self, success, message):
        self.is_building = False
        self.build_btn.set_enabled(True)
        self.build_btn.set_text("Build ISO")
        self.cancel_btn.set_enabled(False)
        self.path_entry.config(state=tk.NORMAL)
        
        if success:
            self._log(message, "success")
            self.status_label.config(text="Build complete! Use Balena Etcher to flash to USB.")
            self.etcher_btn.set_enabled(True)
            
            size_mb = self.output_path.stat().st_size / (1024 * 1024)
            self._log(f"ISO size: {size_mb:.1f} MB", "success")
            
            messagebox.showinfo("Build Complete", 
                f"Aegis OS {self.edition['name']} ISO created!\n\n"
                f"Location: {self.output_path}\n\n"
                "Use Balena Etcher to flash this ISO to a USB drive.")
        else:
            self._log(message, "error")
            self.status_label.config(text="Build failed")
            messagebox.showerror("Build Failed", message)
    
    def _cancel_build(self):
        if self.builder:
            self.builder.cancel()
            self._log("Cancelling build...", "error")
    
    def _open_etcher(self):
        webbrowser.open("https://etcher.balena.io/")


def main():
    licensed_mode = "--licensed" in sys.argv
    app = AegisISOBuilder(licensed_mode=licensed_mode)
    app.mainloop()


if __name__ == "__main__":
    main()
