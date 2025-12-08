#!/usr/bin/env python3
"""
Aegis OS Freemium - ISO Builder
A polished GUI application for building Aegis OS Freemium ISOs.
No license required - immediately usable.
"""

import os
import sys
import threading
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from aegis_builder_core import ISOBuilder, Edition, EDITIONS, get_output_path, VERSION

DARK_BG = "#1a1a2e"
DARK_SECONDARY = "#16213e"
DARK_TERTIARY = "#0f3460"
CYAN_ACCENT = "#00d4ff"
CYAN_HOVER = "#00b8e6"
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
    
    def __init__(self, parent, text, command=None, primary=True, width=200, height=40, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=DARK_BG, highlightthickness=0, **kwargs)
        
        self.command = command
        self.text = text
        self.primary = primary
        self.width = width
        self.height = height
        self.enabled = True
        
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
                dot.create_oval(4, 4, 20, 20, fill=CYAN_ACCENT, outline="")
                label.config(fg=CYAN_ACCENT)
            else:
                dot.create_oval(4, 4, 20, 20, fill=DARK_TERTIARY, outline="")
                label.config(fg=TEXT_SECONDARY)
    
    def reset(self):
        self.set_step(-1)
        for dot, label in zip(self.step_dots, self.step_labels):
            dot.delete("all")
            dot.create_oval(4, 4, 20, 20, fill=DARK_TERTIARY, outline="")
            label.config(fg=TEXT_SECONDARY)


class AegisFreemiumBuilder(tk.Tk):
    """Main application window for building Aegis OS Freemium ISOs."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Aegis OS Freemium - ISO Builder")
        self.geometry("700x600")
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        
        try:
            if sys.platform == "win32":
                self.iconbitmap(default="")
        except:
            pass
        
        self.edition = EDITIONS["freemium"]
        self.builder = None
        self.build_thread = None
        self.is_building = False
        self.output_path = get_output_path(self.edition)
        
        self._create_widgets()
        self._center_window()
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        header_frame = tk.Frame(self, bg=DARK_SECONDARY, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg=DARK_SECONDARY)
        title_frame.pack(expand=True)
        
        logo_canvas = tk.Canvas(title_frame, width=50, height=50, 
                               bg=DARK_SECONDARY, highlightthickness=0)
        logo_canvas.pack(side=tk.LEFT, padx=(0, 15))
        logo_canvas.create_oval(5, 5, 45, 45, fill=CYAN_ACCENT, outline="")
        logo_canvas.create_text(25, 25, text="A", fill=DARK_BG, 
                               font=("Segoe UI", 20, "bold"))
        
        title_text = tk.Frame(title_frame, bg=DARK_SECONDARY)
        title_text.pack(side=tk.LEFT)
        
        tk.Label(title_text, text="Aegis OS", font=("Segoe UI", 18, "bold"),
                bg=DARK_SECONDARY, fg=TEXT_PRIMARY).pack(anchor=tk.W)
        tk.Label(title_text, text=f"Freemium Edition • v{VERSION}", 
                font=("Segoe UI", 10), bg=DARK_SECONDARY, 
                fg=CYAN_ACCENT).pack(anchor=tk.W)
        
        self.steps_frame = tk.Frame(self, bg=DARK_BG, pady=20)
        self.steps_frame.pack(fill=tk.X, padx=40)
        
        self.step_indicator = StepIndicator(self.steps_frame, BUILD_STEPS)
        self.step_indicator.pack()
        
        content_frame = tk.Frame(self, bg=DARK_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        path_frame = tk.Frame(content_frame, bg=DARK_BG)
        path_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(path_frame, text="Output Location:", font=("Segoe UI", 10),
                bg=DARK_BG, fg=TEXT_SECONDARY).pack(anchor=tk.W)
        
        path_input_frame = tk.Frame(path_frame, bg=DARK_TERTIARY)
        path_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.path_var = tk.StringVar(value=str(self.output_path))
        self.path_entry = tk.Entry(path_input_frame, textvariable=self.path_var,
                                  font=("Consolas", 10), bg=DARK_TERTIARY,
                                  fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                  relief=tk.FLAT, bd=10)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(path_input_frame, text="Browse", 
                              font=("Segoe UI", 9), bg=DARK_SECONDARY,
                              fg=TEXT_PRIMARY, relief=tk.FLAT, padx=15,
                              cursor="hand2", command=self._browse_path)
        browse_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.status_label = tk.Label(content_frame, 
                                    text="Ready to build Aegis OS Freemium",
                                    font=("Segoe UI", 12), bg=DARK_BG, 
                                    fg=TEXT_PRIMARY)
        self.status_label.pack(pady=(0, 10))
        
        progress_frame = tk.Frame(content_frame, bg=DARK_TERTIARY, height=8)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        progress_frame.pack_propagate(False)
        
        self.progress_bar = tk.Canvas(progress_frame, bg=DARK_TERTIARY, 
                                     highlightthickness=0, height=8)
        self.progress_bar.pack(fill=tk.BOTH, expand=True)
        self.progress_fill = None
        self._update_progress(0)
        
        self.percent_label = tk.Label(content_frame, text="0%", 
                                     font=("Segoe UI", 10, "bold"),
                                     bg=DARK_BG, fg=CYAN_ACCENT)
        self.percent_label.pack()
        
        log_frame = tk.Frame(content_frame, bg=DARK_TERTIARY)
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
        self.log_text.tag_configure("info", foreground=CYAN_ACCENT)
        
        button_frame = tk.Frame(content_frame, bg=DARK_BG)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.build_btn = ModernButton(button_frame, "Build ISO", 
                                     command=self._start_build, width=180)
        self.build_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = ModernButton(button_frame, "Cancel", 
                                      command=self._cancel_build, 
                                      primary=False, width=120)
        self.cancel_btn.pack(side=tk.LEFT)
        self.cancel_btn.set_enabled(False)
        
        self.post_build_frame = tk.Frame(button_frame, bg=DARK_BG)
        self.post_build_frame.pack(side=tk.RIGHT)
        
        self.etcher_btn = ModernButton(self.post_build_frame, "Open Balena Etcher",
                                      command=self._open_etcher, width=160)
        self.etcher_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.etcher_btn.set_enabled(False)
        
        self.folder_btn = ModernButton(self.post_build_frame, "Open Folder",
                                      command=self._open_folder, 
                                      primary=False, width=120)
        self.folder_btn.pack(side=tk.LEFT)
        self.folder_btn.set_enabled(False)
        
        footer = tk.Frame(self, bg=DARK_SECONDARY, height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        tk.Label(footer, text="After building, use Balena Etcher to flash the ISO to a USB drive",
                font=("Segoe UI", 9), bg=DARK_SECONDARY, 
                fg=TEXT_SECONDARY).pack(expand=True)
    
    def _browse_path(self):
        filename = filedialog.asksaveasfilename(
            title="Save ISO As",
            defaultextension=".iso",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")],
            initialdir=str(Path.home() / "Downloads"),
            initialfile=f"aegis-freemium-{VERSION}.iso"
        )
        if filename:
            self.path_var.set(filename)
            self.output_path = Path(filename)
    
    def _update_progress(self, percent):
        self.progress_bar.delete("all")
        width = self.progress_bar.winfo_width()
        if width <= 1:
            width = 600
        fill_width = int((width * percent) / 100)
        
        if fill_width > 0:
            self.progress_bar.create_rectangle(0, 0, fill_width, 8, 
                                              fill=CYAN_ACCENT, outline="")
        
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
        
        self.output_path = Path(self.path_var.get())
        
        if self.output_path.exists():
            if not messagebox.askyesno("File Exists", 
                f"The file {self.output_path.name} already exists.\n\n"
                "Do you want to overwrite it?"):
                return
        
        self.is_building = True
        self.build_btn.set_enabled(False)
        self.cancel_btn.set_enabled(True)
        self.etcher_btn.set_enabled(False)
        self.folder_btn.set_enabled(False)
        self.path_entry.config(state=tk.DISABLED)
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self._log("Starting Aegis OS Freemium build...", "info")
        self._log(f"Output: {self.output_path}", "info")
        
        self.builder = ISOBuilder(self.edition, self._progress_callback)
        self.build_thread = threading.Thread(target=self._build_worker, daemon=True)
        self.build_thread.start()
    
    def _build_worker(self):
        try:
            success, message = self.builder.build(self.output_path)
            self.after(0, lambda: self._build_complete(success, message))
        except Exception as e:
            self.after(0, lambda: self._build_complete(False, f"Build error: {str(e)}"))
    
    def _build_complete(self, success, message):
        self.is_building = False
        self.build_btn.set_enabled(True)
        self.cancel_btn.set_enabled(False)
        self.path_entry.config(state=tk.NORMAL)
        
        if success:
            self.step_indicator.set_step(4)
            self._update_progress(100)
            self.status_label.config(text="ISO built successfully! Use Balena Etcher to flash it to USB.")
            self._log("Build completed successfully!", "success")
            self._log(message, "success")
            
            self.etcher_btn.set_enabled(True)
            self.folder_btn.set_enabled(True)
            
            messagebox.showinfo("Build Complete", 
                f"Aegis OS Freemium ISO built successfully!\n\n"
                f"Location: {self.output_path}\n\n"
                "Use Balena Etcher to flash the ISO to a USB drive.")
        else:
            self.status_label.config(text="Build failed - check the log for details")
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
            self.build_btn.set_enabled(True)
            self.cancel_btn.set_enabled(False)
            self.path_entry.config(state=tk.NORMAL)
            self.status_label.config(text="Build cancelled")
            self.step_indicator.reset()
            self._update_progress(0)
            self._log("Build cancelled by user", "warning")
    
    def _open_etcher(self):
        etcher_urls = [
            "balena-etcher://",
            "https://www.balena.io/etcher/"
        ]
        
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
        self._log("Balena Etcher not found - opening download page", "warning")
    
    def _open_folder(self):
        folder = self.output_path.parent
        
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", str(self.output_path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(self.output_path)])
        else:
            subprocess.Popen(["xdg-open", str(folder)])


def main():
    app = AegisFreemiumBuilder()
    app.mainloop()


if __name__ == "__main__":
    main()
