#!/usr/bin/env python3
"""
Aegis OS Freemium Edition Installer
Python/Tkinter replacement for aegis-installer-freemium.hta
Downloads the free version of Aegis OS with checksum verification
"""

import os
import sys
import hashlib
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import urllib.request
import urllib.error
import time
import webbrowser
import tempfile

VERSION = "1.0.0"
APP_NAME = "Aegis OS Freemium Installer"

DOWNLOAD_MIRRORS = [
    "https://repo.linuxliteos.com/linuxlite/isos/7.2/linux-lite-7.2-64bit.iso",
    "https://mirror.freedif.org/LinuxLiteOS/isos/7.2/linux-lite-7.2-64bit.iso",
]

EXPECTED_SHA256 = "DC8955E02C68537815ED0010F7C4C035CE786BBA2C679DD74532B22205DF8216"
ISO_FILENAME = "AegisOS-Freemium.iso"

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


class AegisFreemiumInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("550x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        self.download_folder = str(Path.home() / "Downloads")
        self.download_thread = None
        self.cancel_download = False
        self.iso_path = ""
        self.iso_hash = ""
        
        self._setup_styles()
        self._create_ui()
        self._center_window()
    
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
        
        subtitle = tk.Label(header_inner, text="Free Forever - Try Before You Buy",
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
        
        self.btn_start = ttk.Button(btn_frame, text="Download ISO", 
                                    command=self._start_download, style="Primary.TButton")
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
        
        folder_section = self._create_section(self.step1_frame, "Download Location")
        
        path_frame = tk.Frame(folder_section, bg="#f5f5f5")
        path_frame.pack(fill="x", pady=(8, 5))
        
        self.folder_label = tk.Label(path_frame, text=self.download_folder,
                                    font=("Consolas", 9), bg="#f5f5f5", 
                                    wraplength=400, justify="left")
        self.folder_label.pack(padx=8, pady=6, anchor="w")
        
        btn_browse = ttk.Button(folder_section, text="Change Folder", 
                               command=self._browse_folder)
        btn_browse.pack(anchor="w", pady=(0, 5))
        
        req_section = self._create_section(self.step1_frame, "Requirements")
        
        req_lbl = tk.Label(req_section, text="~3 GB disk space, stable internet, 8GB+ USB drive",
                          font=("Segoe UI", 10), bg="white")
        req_lbl.pack(anchor="w", pady=(5, 0))
    
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
        
        self.progress_text = tk.Label(center_frame, text="Starting download...",
                                     font=("Segoe UI", 11), bg="white", fg="#666666")
        self.progress_text.pack()
        
        self.progress_speed = tk.Label(center_frame, text="",
                                      font=("Segoe UI", 10), bg="white", fg="#888888")
        self.progress_speed.pack(pady=(5, 0))
    
    def _create_step3(self):
        success_section = self._create_section(self.step3_frame, None)
        
        success_lbl = tk.Label(success_section, text="✔ Download Complete!",
                              font=("Segoe UI", 18), bg="white", fg="#0078D7")
        success_lbl.pack(pady=10)
        
        path_section = self._create_section(self.step3_frame, "ISO File")
        
        self.iso_path_label = tk.Label(path_section, text="",
                                      font=("Consolas", 9), bg="#f5f5f5",
                                      wraplength=450, justify="left")
        self.iso_path_label.pack(fill="x", padx=8, pady=6)
        
        hash_section = self._create_section(self.step3_frame, "SHA256 Checksum")
        
        self.hash_label = tk.Label(hash_section, text="",
                                  font=("Consolas", 8), bg="#f5f5f5",
                                  wraplength=450)
        self.hash_label.pack(fill="x", padx=8, pady=6)
        
        next_section = self._create_section(self.step3_frame, "Next: Create Bootable USB")
        
        step1_frame = tk.Frame(next_section, bg="white")
        step1_frame.pack(anchor="w", pady=2)
        
        tk.Label(step1_frame, text="1. Download ", font=("Segoe UI", 10), bg="white").pack(side="left")
        
        etcher_link = tk.Label(step1_frame, text="Balena Etcher", 
                              font=("Segoe UI", 10, "underline"),
                              bg="white", fg="#0066cc", cursor="hand2")
        etcher_link.pack(side="left")
        etcher_link.bind("<Button-1>", lambda e: self._open_etcher())
        
        tk.Label(next_section, text="2. Select ISO, select USB, click Flash",
                font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=2)
    
    def _show_step(self, step):
        self.step1_frame.pack_forget()
        self.step2_frame.pack_forget()
        self.step3_frame.pack_forget()
        
        if step == 1:
            self.step1_frame.pack(fill="both", expand=True)
            self.btn_start.configure(text="Download ISO", state="normal")
        elif step == 2:
            self.step2_frame.pack(fill="both", expand=True)
            self.btn_start.configure(text="Downloading...", state="disabled")
        elif step == 3:
            self.step3_frame.pack(fill="both", expand=True)
            self.btn_start.configure(text="Open Folder", state="normal",
                                    command=self._open_folder)
            self.btn_cancel.configure(text="Close")
    
    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_folder,
                                        title="Select Download Location")
        if folder:
            self.download_folder = folder
            self.folder_label.configure(text=folder)
    
    def _start_download(self):
        self.cancel_download = False
        self._show_step(2)
        
        self.download_thread = threading.Thread(target=self._download_worker, daemon=True)
        self.download_thread.start()
    
    def _download_worker(self):
        iso_path = os.path.join(self.download_folder, ISO_FILENAME)
        
        for mirror_url in DOWNLOAD_MIRRORS:
            if self.cancel_download:
                return
            
            try:
                self._update_progress(0, f"Connecting to mirror...", "")
                
                request = urllib.request.Request(mirror_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                response = urllib.request.urlopen(request, timeout=30)
                total_size = int(response.headers.get('Content-Length', 0))
                
                if total_size == 0:
                    continue
                
                downloaded = 0
                start_time = time.time()
                last_update = start_time
                
                with open(iso_path, 'wb') as f:
                    while True:
                        if self.cancel_download:
                            f.close()
                            try:
                                os.remove(iso_path)
                            except:
                                pass
                            return
                        
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        now = time.time()
                        if now - last_update >= 0.5:
                            pct = int((downloaded / total_size) * 90)
                            elapsed = now - start_time
                            speed = downloaded / elapsed / (1024 * 1024) if elapsed > 0 else 0
                            
                            self._update_progress(
                                pct,
                                f"Downloading: {int(downloaded/total_size*100)}%",
                                f"{speed:.1f} MB/s"
                            )
                            last_update = now
                
                self._update_progress(92, "Verifying checksum...", "")
                
                file_hash = self._calculate_sha256(iso_path)
                
                if file_hash.upper() != EXPECTED_SHA256.upper():
                    self._show_error("Checksum Mismatch", 
                                    "The downloaded file is corrupted. Please try again.")
                    try:
                        os.remove(iso_path)
                    except:
                        pass
                    return
                
                self.iso_path = iso_path
                self.iso_hash = file_hash.upper()
                
                self._download_complete()
                return
                
            except urllib.error.URLError as e:
                continue
            except Exception as e:
                continue
        
        self._show_error("Download Failed", 
                        "Could not download from any mirror. Please check your internet connection.")
    
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
    
    def _download_complete(self):
        def complete():
            self.iso_path_label.configure(text=self.iso_path)
            self.hash_label.configure(text=self.iso_hash)
            self._show_step(3)
        
        self.root.after(0, complete)
    
    def _show_error(self, title, message):
        def show():
            self.progress_pct.configure(text="!", fg="#d32f2f")
            self.progress_text.configure(text=message, fg="#d32f2f")
            self.progress_speed.configure(text="")
            self.btn_start.configure(text="Retry", state="normal",
                                    command=self._retry_download)
        
        self.root.after(0, show)
    
    def _retry_download(self):
        self.progress_pct.configure(fg="#0078D7")
        self.progress_text.configure(fg="#666666")
        self._start_download()
    
    def _open_folder(self):
        if sys.platform == "win32":
            os.startfile(self.download_folder)
        elif sys.platform == "darwin":
            os.system(f'open "{self.download_folder}"')
        else:
            os.system(f'xdg-open "{self.download_folder}"')
    
    def _open_etcher(self):
        webbrowser.open("https://etcher.balena.io/")
    
    def _on_cancel(self):
        if self.download_thread and self.download_thread.is_alive():
            if messagebox.askyesno("Cancel Download", 
                                  "Are you sure you want to cancel the download?"):
                self.cancel_download = True
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
