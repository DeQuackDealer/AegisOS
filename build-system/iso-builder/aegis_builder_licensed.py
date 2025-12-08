#!/usr/bin/env python3
"""
Aegis OS Licensed - ISO Builder
A polished GUI application for building licensed Aegis OS ISOs.
Requires valid license for premium editions.
"""

import os
import sys
import json
import threading
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from aegis_builder_core import (
    ISOBuilder, Edition, EDITIONS, get_output_path, VERSION,
    LicenseValidator
)

DARK_BG = "#1a1a2e"
DARK_SECONDARY = "#16213e"
DARK_TERTIARY = "#0f3460"
CYAN_ACCENT = "#00d4ff"
CYAN_HOVER = "#00b8e6"
GOLD_ACCENT = "#ffd700"
GOLD_HOVER = "#e6c200"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#b0b0b0"
SUCCESS_GREEN = "#00ff88"
ERROR_RED = "#ff4757"
WARNING_YELLOW = "#ffa502"

BUILD_STEPS = [
    "Preparing",
    "Extracting",
    "Customizing", 
    "Creating ISO",
    "Complete"
]


class ModernButton(tk.Canvas):
    """A modern styled button with hover effects."""
    
    def __init__(self, parent, text, command=None, primary=True, width=200, height=40, 
                 accent_color=None, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=DARK_BG, highlightthickness=0, **kwargs)
        
        self.command = command
        self.text = text
        self.primary = primary
        self.width = width
        self.height = height
        self.enabled = True
        
        if accent_color:
            self.bg_color = accent_color
            self.hover_color = GOLD_HOVER if accent_color == GOLD_ACCENT else CYAN_HOVER
        else:
            self.bg_color = CYAN_ACCENT if primary else DARK_TERTIARY
            self.hover_color = CYAN_HOVER if primary else DARK_SECONDARY
        
        self.text_color = DARK_BG if primary else TEXT_PRIMARY
        
        self._draw()
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _draw(self, hover=False):
        self.delete("all")
        color = self.hover_color if hover else self.bg_color
        if not self.enabled:
            color = DARK_TERTIARY
        
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 8, fill=color, outline="")
        
        text_color = self.text_color if self.enabled else TEXT_SECONDARY
        self.create_text(self.width//2, self.height//2, text=self.text, 
                        fill=text_color, font=("Segoe UI", 11, "bold"))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        if self.enabled:
            self._draw(hover=True)
            self.config(cursor="hand2")
    
    def _on_leave(self, event):
        self._draw(hover=False)
        self.config(cursor="")
    
    def _on_click(self, event):
        if self.enabled and self.command:
            self.command()
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        self._draw()
    
    def set_text(self, text):
        self.text = text
        self._draw()


class StepIndicator(tk.Frame):
    """Shows the current build step with visual progress."""
    
    def __init__(self, parent, steps):
        super().__init__(parent, bg=DARK_BG)
        self.steps = steps
        self.current_step = -1
        self.step_labels = []
        self.step_dots = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        for i, step in enumerate(self.steps):
            frame = tk.Frame(self, bg=DARK_BG)
            frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
            
            dot_canvas = tk.Canvas(frame, width=24, height=24, 
                                  bg=DARK_BG, highlightthickness=0)
            dot_canvas.pack()
            dot_canvas.create_oval(4, 4, 20, 20, fill=DARK_TERTIARY, outline="")
            self.step_dots.append(dot_canvas)
            
            label = tk.Label(frame, text=step, font=("Segoe UI", 9),
                           bg=DARK_BG, fg=TEXT_SECONDARY)
            label.pack(pady=(4, 0))
            self.step_labels.append(label)
            
            if i < len(self.steps) - 1:
                line = tk.Canvas(self, width=40, height=24, 
                               bg=DARK_BG, highlightthickness=0)
                line.pack(side=tk.LEFT)
                line.create_line(0, 12, 40, 12, fill=DARK_TERTIARY, width=2)
    
    def set_step(self, step_index):
        self.current_step = step_index
        
        for i, (dot, label) in enumerate(zip(self.step_dots, self.step_labels)):
            dot.delete("all")
            
            if i < step_index:
                dot.create_oval(4, 4, 20, 20, fill=SUCCESS_GREEN, outline="")
                dot.create_text(12, 12, text="✓", fill=DARK_BG, font=("Segoe UI", 10, "bold"))
                label.config(fg=SUCCESS_GREEN)
            elif i == step_index:
                dot.create_oval(4, 4, 20, 20, fill=GOLD_ACCENT, outline="")
                label.config(fg=GOLD_ACCENT)
            else:
                dot.create_oval(4, 4, 20, 20, fill=DARK_TERTIARY, outline="")
                label.config(fg=TEXT_SECONDARY)
    
    def reset(self):
        self.set_step(-1)
        for dot, label in zip(self.step_dots, self.step_labels):
            dot.delete("all")
            dot.create_oval(4, 4, 20, 20, fill=DARK_TERTIARY, outline="")
            label.config(fg=TEXT_SECONDARY)


class AegisLicensedBuilder(tk.Tk):
    """Main application window for building licensed Aegis OS ISOs."""
    
    SCREEN_LICENSE = "license"
    SCREEN_EDITION = "edition"
    SCREEN_BUILD = "build"
    SCREEN_COMPLETE = "complete"
    
    def __init__(self):
        super().__init__()
        
        self.title("Aegis OS Licensed - ISO Builder")
        self.geometry("750x650")
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        
        try:
            if sys.platform == "win32":
                self.iconbitmap(default="")
        except:
            pass
        
        self.license_validator = LicenseValidator()
        self.license_data = None
        self.licensed_edition = None
        self.edition = None
        self.builder = None
        self.build_thread = None
        self.is_building = False
        self.output_path = None
        
        self.current_screen = None
        self.screen_frames = {}
        
        self._create_header()
        self._create_screens()
        self._center_window()
        
        self._auto_find_license()
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_header(self):
        self.header_frame = tk.Frame(self, bg=DARK_SECONDARY, height=80)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(self.header_frame, bg=DARK_SECONDARY)
        title_frame.pack(expand=True)
        
        logo_canvas = tk.Canvas(title_frame, width=50, height=50, 
                               bg=DARK_SECONDARY, highlightthickness=0)
        logo_canvas.pack(side=tk.LEFT, padx=(0, 15))
        logo_canvas.create_oval(5, 5, 45, 45, fill=GOLD_ACCENT, outline="")
        logo_canvas.create_text(25, 25, text="A", fill=DARK_BG, 
                               font=("Segoe UI", 20, "bold"))
        
        title_text = tk.Frame(title_frame, bg=DARK_SECONDARY)
        title_text.pack(side=tk.LEFT)
        
        tk.Label(title_text, text="Aegis OS", font=("Segoe UI", 18, "bold"),
                bg=DARK_SECONDARY, fg=TEXT_PRIMARY).pack(anchor=tk.W)
        self.header_subtitle = tk.Label(title_text, text=f"Licensed Edition • v{VERSION}", 
                font=("Segoe UI", 10), bg=DARK_SECONDARY, 
                fg=GOLD_ACCENT)
        self.header_subtitle.pack(anchor=tk.W)
        
        self.content_frame = tk.Frame(self, bg=DARK_BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def _create_screens(self):
        self._create_license_screen()
        self._create_edition_screen()
        self._create_build_screen()
        self._create_complete_screen()
        
        self._show_screen(self.SCREEN_LICENSE)
    
    def _show_screen(self, screen_name):
        for name, frame in self.screen_frames.items():
            frame.pack_forget()
        
        self.screen_frames[screen_name].pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        self.current_screen = screen_name
    
    def _create_license_screen(self):
        frame = tk.Frame(self.content_frame, bg=DARK_BG)
        self.screen_frames[self.SCREEN_LICENSE] = frame
        
        tk.Label(frame, text="License Verification", 
                font=("Segoe UI", 16, "bold"),
                bg=DARK_BG, fg=TEXT_PRIMARY).pack(pady=(0, 10))
        
        tk.Label(frame, text="Enter your license key or load your license.json file",
                font=("Segoe UI", 10), bg=DARK_BG, fg=TEXT_SECONDARY).pack(pady=(0, 30))
        
        license_input_frame = tk.Frame(frame, bg=DARK_BG)
        license_input_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(license_input_frame, text="License Key:", font=("Segoe UI", 10),
                bg=DARK_BG, fg=TEXT_SECONDARY).pack(anchor=tk.W)
        
        key_frame = tk.Frame(license_input_frame, bg=DARK_TERTIARY)
        key_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.license_key_var = tk.StringVar()
        self.license_key_entry = tk.Entry(key_frame, textvariable=self.license_key_var,
                                         font=("Consolas", 11), bg=DARK_TERTIARY,
                                         fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                         relief=tk.FLAT, bd=12)
        self.license_key_entry.pack(fill=tk.X)
        
        or_label = tk.Label(frame, text="— or —", font=("Segoe UI", 10),
                           bg=DARK_BG, fg=TEXT_SECONDARY)
        or_label.pack(pady=15)
        
        load_btn = ModernButton(frame, "Load License File", 
                               command=self._load_license_file, 
                               primary=False, width=200)
        load_btn.pack()
        
        self.license_file_label = tk.Label(frame, text="", font=("Segoe UI", 9),
                                          bg=DARK_BG, fg=TEXT_SECONDARY)
        self.license_file_label.pack(pady=(10, 0))
        
        self.license_status_frame = tk.Frame(frame, bg=DARK_BG)
        self.license_status_frame.pack(fill=tk.X, pady=20)
        
        self.license_status_label = tk.Label(self.license_status_frame, text="",
                                            font=("Segoe UI", 10), bg=DARK_BG,
                                            fg=TEXT_SECONDARY, wraplength=500)
        self.license_status_label.pack()
        
        button_frame = tk.Frame(frame, bg=DARK_BG)
        button_frame.pack(pady=20)
        
        self.validate_btn = ModernButton(button_frame, "Validate License", 
                                        command=self._validate_license,
                                        accent_color=GOLD_ACCENT, width=180)
        self.validate_btn.pack()
        
        help_frame = tk.Frame(frame, bg=DARK_TERTIARY)
        help_frame.pack(fill=tk.X, pady=(20, 0))
        
        help_text = """License files are provided after purchase. Your license.json file contains:
• Your registered email
• Edition entitlement  
• Cryptographic signature for offline verification

Need help? Visit aegis-os.com/support"""
        
        tk.Label(help_frame, text=help_text, font=("Segoe UI", 9),
                bg=DARK_TERTIARY, fg=TEXT_SECONDARY, justify=tk.LEFT,
                padx=15, pady=15).pack(anchor=tk.W)
    
    def _create_edition_screen(self):
        frame = tk.Frame(self.content_frame, bg=DARK_BG)
        self.screen_frames[self.SCREEN_EDITION] = frame
        
        tk.Label(frame, text="License Verified!", 
                font=("Segoe UI", 16, "bold"),
                bg=DARK_BG, fg=SUCCESS_GREEN).pack(pady=(0, 10))
        
        self.edition_info_label = tk.Label(frame, text="",
                font=("Segoe UI", 10), bg=DARK_BG, fg=TEXT_SECONDARY)
        self.edition_info_label.pack(pady=(0, 30))
        
        self.edition_card_frame = tk.Frame(frame, bg=DARK_TERTIARY)
        self.edition_card_frame.pack(fill=tk.X, pady=20, ipadx=20, ipady=20)
        
        self.edition_name_label = tk.Label(self.edition_card_frame, text="",
                font=("Segoe UI", 18, "bold"), bg=DARK_TERTIARY, fg=GOLD_ACCENT)
        self.edition_name_label.pack(pady=(10, 5))
        
        self.edition_desc_label = tk.Label(self.edition_card_frame, text="",
                font=("Segoe UI", 11), bg=DARK_TERTIARY, fg=TEXT_PRIMARY)
        self.edition_desc_label.pack()
        
        self.edition_size_label = tk.Label(self.edition_card_frame, text="",
                font=("Segoe UI", 10), bg=DARK_TERTIARY, fg=TEXT_SECONDARY)
        self.edition_size_label.pack(pady=(10, 10))
        
        path_frame = tk.Frame(frame, bg=DARK_BG)
        path_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(path_frame, text="Output Location:", font=("Segoe UI", 10),
                bg=DARK_BG, fg=TEXT_SECONDARY).pack(anchor=tk.W)
        
        path_input_frame = tk.Frame(path_frame, bg=DARK_TERTIARY)
        path_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.edition_path_var = tk.StringVar()
        self.edition_path_entry = tk.Entry(path_input_frame, textvariable=self.edition_path_var,
                                          font=("Consolas", 10), bg=DARK_TERTIARY,
                                          fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                          relief=tk.FLAT, bd=10)
        self.edition_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(path_input_frame, text="Browse", 
                              font=("Segoe UI", 9), bg=DARK_SECONDARY,
                              fg=TEXT_PRIMARY, relief=tk.FLAT, padx=15,
                              cursor="hand2", command=self._browse_output_path)
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        button_frame = tk.Frame(frame, bg=DARK_BG)
        button_frame.pack(pady=20)
        
        back_btn = ModernButton(button_frame, "Back", 
                               command=lambda: self._show_screen(self.SCREEN_LICENSE),
                               primary=False, width=120)
        back_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.proceed_btn = ModernButton(button_frame, "Build ISO", 
                                       command=self._start_build_from_edition,
                                       accent_color=GOLD_ACCENT, width=180)
        self.proceed_btn.pack(side=tk.LEFT)
    
    def _create_build_screen(self):
        frame = tk.Frame(self.content_frame, bg=DARK_BG)
        self.screen_frames[self.SCREEN_BUILD] = frame
        
        self.build_title_label = tk.Label(frame, text="Building Aegis OS", 
                font=("Segoe UI", 16, "bold"),
                bg=DARK_BG, fg=TEXT_PRIMARY)
        self.build_title_label.pack(pady=(0, 20))
        
        self.steps_frame = tk.Frame(frame, bg=DARK_BG)
        self.steps_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.step_indicator = StepIndicator(self.steps_frame, BUILD_STEPS)
        self.step_indicator.pack()
        
        self.build_status_label = tk.Label(frame, 
                                    text="Initializing...",
                                    font=("Segoe UI", 12), bg=DARK_BG, 
                                    fg=TEXT_PRIMARY)
        self.build_status_label.pack(pady=(0, 10))
        
        progress_frame = tk.Frame(frame, bg=DARK_TERTIARY, height=8)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        progress_frame.pack_propagate(False)
        
        self.progress_bar = tk.Canvas(progress_frame, bg=DARK_TERTIARY, 
                                     highlightthickness=0, height=8)
        self.progress_bar.pack(fill=tk.BOTH, expand=True)
        
        self.percent_label = tk.Label(frame, text="0%", 
                                     font=("Segoe UI", 10, "bold"),
                                     bg=DARK_BG, fg=GOLD_ACCENT)
        self.percent_label.pack()
        
        log_frame = tk.Frame(frame, bg=DARK_TERTIARY)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        tk.Label(log_frame, text=" Build Log", font=("Segoe UI", 9, "bold"),
                bg=DARK_TERTIARY, fg=TEXT_SECONDARY, anchor=tk.W).pack(
                fill=tk.X, padx=10, pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, font=("Consolas", 9), 
                               bg=DARK_TERTIARY, fg=TEXT_SECONDARY,
                               relief=tk.FLAT, height=8, wrap=tk.WORD,
                               state=tk.DISABLED, padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.log_text.tag_configure("success", foreground=SUCCESS_GREEN)
        self.log_text.tag_configure("error", foreground=ERROR_RED)
        self.log_text.tag_configure("warning", foreground=WARNING_YELLOW)
        self.log_text.tag_configure("info", foreground=GOLD_ACCENT)
        
        button_frame = tk.Frame(frame, bg=DARK_BG)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.cancel_btn = ModernButton(button_frame, "Cancel Build", 
                                      command=self._cancel_build, 
                                      primary=False, width=140)
        self.cancel_btn.pack()
    
    def _create_complete_screen(self):
        frame = tk.Frame(self.content_frame, bg=DARK_BG)
        self.screen_frames[self.SCREEN_COMPLETE] = frame
        
        success_canvas = tk.Canvas(frame, width=80, height=80, 
                                  bg=DARK_BG, highlightthickness=0)
        success_canvas.pack(pady=(20, 15))
        success_canvas.create_oval(5, 5, 75, 75, fill=SUCCESS_GREEN, outline="")
        success_canvas.create_text(40, 40, text="✓", fill=DARK_BG, 
                                  font=("Segoe UI", 32, "bold"))
        
        tk.Label(frame, text="ISO Built Successfully!", 
                font=("Segoe UI", 18, "bold"),
                bg=DARK_BG, fg=SUCCESS_GREEN).pack(pady=(0, 10))
        
        self.complete_info_label = tk.Label(frame, text="",
                font=("Segoe UI", 11), bg=DARK_BG, fg=TEXT_PRIMARY)
        self.complete_info_label.pack(pady=(0, 5))
        
        self.complete_path_label = tk.Label(frame, text="",
                font=("Consolas", 9), bg=DARK_BG, fg=TEXT_SECONDARY,
                wraplength=500)
        self.complete_path_label.pack(pady=(0, 30))
        
        button_frame = tk.Frame(frame, bg=DARK_BG)
        button_frame.pack(pady=10)
        
        self.complete_etcher_btn = ModernButton(button_frame, "Open Balena Etcher",
                                      command=self._open_etcher,
                                      accent_color=GOLD_ACCENT, width=180)
        self.complete_etcher_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.complete_folder_btn = ModernButton(button_frame, "Open Folder",
                                      command=self._open_folder, 
                                      primary=False, width=140)
        self.complete_folder_btn.pack(side=tk.LEFT)
        
        tk.Label(frame, 
                text="Use Balena Etcher to flash the ISO to a USB drive",
                font=("Segoe UI", 10), bg=DARK_BG, fg=TEXT_SECONDARY).pack(pady=30)
        
        build_another_btn = ModernButton(frame, "Build Another", 
                                        command=self._reset_to_license,
                                        primary=False, width=150)
        build_another_btn.pack()
    
    def _auto_find_license(self):
        license_data = self.license_validator.find_license()
        if license_data:
            self.license_data = license_data
            key = license_data.get("key", "")
            if key:
                self.license_key_var.set(key)
            
            file_locations = [
                Path.cwd() / "license.json",
                Path.home() / ".aegis" / "license.json",
                Path.home() / "Downloads" / "aegis-license.json",
                Path.home() / "Desktop" / "aegis-license.json",
            ]
            for loc in file_locations:
                if loc.exists():
                    self.license_file_label.config(
                        text=f"Found: {loc}",
                        fg=SUCCESS_GREEN
                    )
                    break
    
    def _load_license_file(self):
        filename = filedialog.askopenfilename(
            title="Select License File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path.home() / "Downloads")
        )
        if filename:
            license_data = self.license_validator.load_license_file(Path(filename))
            if license_data:
                self.license_data = license_data
                key = license_data.get("key", "")
                if key:
                    self.license_key_var.set(key)
                self.license_file_label.config(
                    text=f"Loaded: {filename}",
                    fg=SUCCESS_GREEN
                )
                self._set_license_status("License file loaded successfully", "success")
            else:
                self._set_license_status("Invalid license file - could not parse JSON", "error")
    
    def _set_license_status(self, message, status_type="info"):
        colors = {
            "success": SUCCESS_GREEN,
            "error": ERROR_RED,
            "warning": WARNING_YELLOW,
            "info": TEXT_SECONDARY
        }
        self.license_status_label.config(text=message, fg=colors.get(status_type, TEXT_SECONDARY))
    
    def _validate_license(self):
        if self.license_data is None:
            key = self.license_key_var.get().strip()
            if not key:
                self._set_license_status(
                    "No license file found - please enter your key or load the file",
                    "error"
                )
                return
            
            self.license_data = {
                "key": key,
                "edition": "",
                "signature": key[:32] if len(key) >= 32 else key
            }
        
        is_valid, message, edition = self.license_validator.validate(self.license_data)
        
        if is_valid:
            self.licensed_edition = edition
            self.edition = EDITIONS.get(edition)
            if self.edition:
                self._show_edition_screen()
            else:
                self._set_license_status(
                    f"License is not valid for this edition: {edition}",
                    "error"
                )
        else:
            if "expired" in message.lower():
                expires = self.license_data.get("expires", "unknown date")
                self._set_license_status(
                    f"License has expired on {expires}",
                    "error"
                )
            elif "invalid" in message.lower():
                self._set_license_status(
                    "Invalid license key - please check and try again",
                    "error"
                )
            else:
                self._set_license_status(message, "error")
    
    def _show_edition_screen(self):
        email = self.license_data.get("email", "your account")
        self.edition_info_label.config(
            text=f"Licensed to: {email}"
        )
        
        self.edition_name_label.config(text=f"{self.edition.name} Edition")
        self.edition_desc_label.config(text=self.edition.description)
        self.edition_size_label.config(text=f"Estimated size: {self.edition.size_gb} GB")
        
        self.output_path = get_output_path(self.edition)
        self.edition_path_var.set(str(self.output_path))
        
        self.header_subtitle.config(text=f"{self.edition.name} Edition • v{VERSION}")
        
        self._show_screen(self.SCREEN_EDITION)
    
    def _browse_output_path(self):
        filename = filedialog.asksaveasfilename(
            title="Save ISO As",
            defaultextension=".iso",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")],
            initialdir=str(Path.home() / "Downloads"),
            initialfile=f"aegis-{self.edition.id}-{VERSION}.iso"
        )
        if filename:
            self.edition_path_var.set(filename)
            self.output_path = Path(filename)
    
    def _start_build_from_edition(self):
        self.output_path = Path(self.edition_path_var.get())
        
        if self.output_path.exists():
            if not messagebox.askyesno("File Exists", 
                f"The file {self.output_path.name} already exists.\n\n"
                "Do you want to overwrite it?"):
                return
        
        self._show_screen(self.SCREEN_BUILD)
        self.build_title_label.config(text=f"Building Aegis OS {self.edition.name}")
        self._start_build()
    
    def _start_build(self):
        if self.is_building:
            return
        
        self.is_building = True
        self.cancel_btn.set_enabled(True)
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self._log(f"Starting Aegis OS {self.edition.name} build...", "info")
        self._log(f"Output: {self.output_path}", "info")
        
        self.step_indicator.reset()
        self._update_progress(0)
        
        self.builder = ISOBuilder(self.edition, self._progress_callback)
        self.build_thread = threading.Thread(target=self._build_worker, daemon=True)
        self.build_thread.start()
    
    def _build_worker(self):
        try:
            success, message = self.builder.build(self.output_path)
            self.after(0, lambda: self._build_complete(success, message))
        except Exception as e:
            self.after(0, lambda: self._build_complete(False, f"Build error: {str(e)}"))
    
    def _progress_callback(self, percent, message):
        self.after(0, lambda: self._update_ui(percent, message))
    
    def _update_ui(self, percent, message):
        self._update_progress(percent)
        self.build_status_label.config(text=message)
        
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
    
    def _update_progress(self, percent):
        self.progress_bar.delete("all")
        width = self.progress_bar.winfo_width()
        if width <= 1:
            width = 600
        fill_width = int((width * percent) / 100)
        
        if fill_width > 0:
            self.progress_bar.create_rectangle(0, 0, fill_width, 8, 
                                              fill=GOLD_ACCENT, outline="")
        
        self.percent_label.config(text=f"{percent}%")
    
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
    
    def _build_complete(self, success, message):
        self.is_building = False
        self.cancel_btn.set_enabled(False)
        
        if success:
            self.step_indicator.set_step(4)
            self._update_progress(100)
            self._log("Build completed successfully!", "success")
            self._log(message, "success")
            
            self.complete_info_label.config(
                text=f"Your Aegis OS {self.edition.name} ISO is ready!"
            )
            self.complete_path_label.config(text=str(self.output_path))
            
            self._show_screen(self.SCREEN_COMPLETE)
        else:
            self.build_status_label.config(text="Build failed - check the log for details")
            self._log(f"Build failed: {message}", "error")
            
            messagebox.showerror("Build Failed", 
                f"The build process encountered an error:\n\n{message}\n\n"
                "Please check the build log for more details.")
    
    def _cancel_build(self):
        if not self.is_building:
            return
        
        if messagebox.askyesno("Cancel Build", 
            "Are you sure you want to cancel the build?"):
            self._log("Cancelling build...", "warning")
            if self.builder:
                self.builder.cancel()
            
            self.is_building = False
            self.cancel_btn.set_enabled(False)
            self.build_status_label.config(text="Build cancelled")
            self.step_indicator.reset()
            self._update_progress(0)
            self._log("Build cancelled by user", "warning")
            
            self._show_screen(self.SCREEN_EDITION)
    
    def _reset_to_license(self):
        self.license_data = None
        self.licensed_edition = None
        self.edition = None
        self.output_path = None
        self.license_key_var.set("")
        self.license_file_label.config(text="", fg=TEXT_SECONDARY)
        self.license_status_label.config(text="", fg=TEXT_SECONDARY)
        self.header_subtitle.config(text=f"Licensed Edition • v{VERSION}")
        
        self._show_screen(self.SCREEN_LICENSE)
        self._auto_find_license()
    
    def _open_etcher(self):
        if sys.platform == "win32":
            etcher_paths = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "balena-etcher" / "balenaEtcher.exe",
                Path(os.environ.get("PROGRAMFILES", "")) / "balenaEtcher" / "balenaEtcher.exe",
                Path(os.environ.get("PROGRAMFILES(X86)", "")) / "balenaEtcher" / "balenaEtcher.exe",
            ]
            for path in etcher_paths:
                if path.exists():
                    subprocess.Popen([str(path)])
                    return
        elif sys.platform == "darwin":
            etcher_paths = [
                Path("/Applications/balenaEtcher.app"),
                Path.home() / "Applications" / "balenaEtcher.app"
            ]
            for path in etcher_paths:
                if path.exists():
                    subprocess.Popen(["open", str(path)])
                    return
        else:
            for cmd in ["balena-etcher-electron", "balena-etcher", "etcher"]:
                try:
                    subprocess.Popen([cmd])
                    return
                except FileNotFoundError:
                    continue
        
        webbrowser.open("https://www.balena.io/etcher/")
    
    def _open_folder(self):
        if self.output_path is None:
            return
            
        folder = self.output_path.parent
        
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", str(self.output_path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(self.output_path)])
        else:
            subprocess.Popen(["xdg-open", str(folder)])


def main():
    app = AegisLicensedBuilder()
    app.mainloop()


if __name__ == "__main__":
    main()
