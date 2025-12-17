#!/usr/bin/env python3
"""
Aegis OS Media Creation Tool
Downloads ISO from GitHub, embeds license, flashes to USB
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import platform
import os
import sys
import urllib.request
import tempfile
import json
import time

class AegisMediaCreator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aegis OS Media Creation Tool")
        self.root.geometry("520x580")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")
        
        self.license_key = tk.StringVar()
        self.selected_drive = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Enter your license key to begin")
        
        self.license_info = None
        self.github_base = "https://github.com/DeQuackDealer/AegisOSRepo/releases/latest/download"
        self.api_base = "https://aegis-os.replit.app"
        
        self.setup_ui()
        
    def setup_ui(self):
        main = tk.Frame(self.root, bg="#0f172a", padx=30, pady=25)
        main.pack(fill="both", expand=True)
        
        tk.Label(main, text="AEGIS OS", font=("Segoe UI", 24, "bold"), 
                bg="#0f172a", fg="#3b82f6").pack()
        tk.Label(main, text="Media Creation Tool", font=("Segoe UI", 11), 
                bg="#0f172a", fg="#64748b").pack(pady=(0, 25))
        
        license_frame = tk.LabelFrame(main, text=" License Key ", bg="#0f172a", fg="white",
                                       font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        license_frame.pack(fill="x", pady=(0, 15))
        
        self.license_entry = tk.Entry(license_frame, textvariable=self.license_key,
                                       font=("Consolas", 12), width=35, bg="#1e293b", 
                                       fg="white", insertbackground="white", relief="flat")
        self.license_entry.pack(fill="x", pady=(5, 10), ipady=8)
        
        btn_frame = tk.Frame(license_frame, bg="#0f172a")
        btn_frame.pack(fill="x")
        
        self.verify_btn = tk.Button(btn_frame, text="Verify License", font=("Segoe UI", 10, "bold"),
                                     bg="#3b82f6", fg="white", relief="flat", padx=15, pady=6,
                                     cursor="hand2", command=self.verify_license)
        self.verify_btn.pack(side="left")
        
        self.freemium_btn = tk.Button(btn_frame, text="Use Freemium", font=("Segoe UI", 10),
                                       bg="#374151", fg="white", relief="flat", padx=15, pady=6,
                                       cursor="hand2", command=self.use_freemium)
        self.freemium_btn.pack(side="right")
        
        self.edition_label = tk.Label(main, text="", font=("Segoe UI", 11, "bold"),
                                       bg="#0f172a", fg="#22c55e")
        self.edition_label.pack(pady=5)
        
        drive_frame = tk.LabelFrame(main, text=" Select USB Drive ", bg="#0f172a", fg="white",
                                     font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        drive_frame.pack(fill="x", pady=(10, 15))
        
        drive_row = tk.Frame(drive_frame, bg="#0f172a")
        drive_row.pack(fill="x")
        
        self.drive_combo = ttk.Combobox(drive_row, textvariable=self.selected_drive,
                                         state="readonly", font=("Segoe UI", 10), width=32)
        self.drive_combo.pack(side="left", fill="x", expand=True)
        
        tk.Button(drive_row, text="Refresh", font=("Segoe UI", 9), bg="#374151", fg="white",
                 relief="flat", padx=10, command=self.refresh_drives).pack(side="right", padx=(10, 0))
        
        tk.Label(drive_frame, text="WARNING: All data on selected drive will be erased!",
                bg="#0f172a", fg="#ef4444", font=("Segoe UI", 9, "bold")).pack(pady=(10, 0))
        
        progress_frame = tk.Frame(main, bg="#0f172a")
        progress_frame.pack(fill="x", pady=20)
        
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", thickness=25)
        
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                         maximum=100, length=400)
        self.progress.pack(fill="x")
        
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var,
                                      bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9))
        self.status_label.pack(pady=(8, 0))
        
        self.create_btn = tk.Button(main, text="Create Bootable USB", font=("Segoe UI", 13, "bold"),
                                     bg="#22c55e", fg="white", relief="flat", pady=12,
                                     cursor="hand2", state="disabled", command=self.start_creation)
        self.create_btn.pack(fill="x", pady=(10, 0))
        
        tk.Label(main, text="aegis-os.com", font=("Segoe UI", 8),
                bg="#0f172a", fg="#475569").pack(side="bottom", pady=(15, 0))
        
        self.refresh_drives()
        
    def verify_license(self):
        key = self.license_key.get().strip().upper()
        if not key:
            messagebox.showerror("Error", "Please enter a license key")
            return
            
        self.status_var.set("Verifying license...")
        self.verify_btn.config(state="disabled")
        
        def verify():
            try:
                data = json.dumps({"license_key": key}).encode()
                req = urllib.request.Request(f"{self.api_base}/api/validate-license",
                                              data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    result = json.loads(resp.read())
                    
                    if result.get("valid"):
                        self.license_info = {
                            "key": key,
                            "edition": result.get("edition", "gamer"),
                            "type": result.get("license_type", "lifetime")
                        }
                        self.root.after(0, lambda: self.on_license_valid())
                    else:
                        self.root.after(0, lambda: self.on_license_invalid(result.get("error", "Invalid license")))
            except Exception as e:
                self.root.after(0, lambda: self.on_license_invalid(f"Connection error: {e}"))
        
        threading.Thread(target=verify, daemon=True).start()
    
    def on_license_valid(self):
        edition = self.license_info["edition"].upper()
        self.edition_label.config(text=f"Edition: {edition}", fg="#22c55e")
        self.status_var.set(f"License verified! Ready to create {edition} edition")
        self.create_btn.config(state="normal", bg="#22c55e")
        self.verify_btn.config(state="normal")
        
    def on_license_invalid(self, error):
        self.edition_label.config(text=f"Error: {error}", fg="#ef4444")
        self.status_var.set("License verification failed")
        self.verify_btn.config(state="normal")
        
    def use_freemium(self):
        self.license_info = {"key": None, "edition": "freemium", "type": "free"}
        self.edition_label.config(text="Edition: FREEMIUM (Free)", fg="#f59e0b")
        self.status_var.set("Freemium mode - no license required")
        self.create_btn.config(state="normal", bg="#f59e0b")
        
    def refresh_drives(self):
        drives = self.get_usb_drives()
        self.drive_combo['values'] = drives
        if drives and "No USB" not in drives[0]:
            self.drive_combo.current(0)
            
    def get_usb_drives(self):
        drives = []
        if platform.system() == "Windows":
            try:
                import ctypes
                bitmask = ctypes.windll.kernel32.GetLogicalDrives()
                for i, letter in enumerate('DEFGHIJKLMNOPQRSTUVWXYZ'):
                    if bitmask & (1 << (i + 3)):
                        path = f"{letter}:\\"
                        if ctypes.windll.kernel32.GetDriveTypeW(path) == 2:
                            try:
                                free = ctypes.c_ulonglong()
                                total = ctypes.c_ulonglong()
                                ctypes.windll.kernel32.GetDiskFreeSpaceExW(path, None, ctypes.pointer(total), ctypes.pointer(free))
                                size_gb = total.value / (1024**3)
                                drives.append(f"{letter}: ({size_gb:.1f} GB)")
                            except:
                                drives.append(f"{letter}:")
            except:
                pass
        elif platform.system() == "Linux":
            try:
                result = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,TRAN', '-n'], capture_output=True, text=True)
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 3 and parts[2] == 'usb':
                        drives.append(f"/dev/{parts[0]} ({parts[1]})")
            except:
                pass
        return drives if drives else ["No USB drives found"]
    
    def start_creation(self):
        drive = self.selected_drive.get()
        if not drive or "No USB" in drive:
            messagebox.showerror("Error", "Please select a USB drive")
            return
            
        if not self.license_info:
            messagebox.showerror("Error", "Please verify your license first")
            return
            
        confirm = messagebox.askyesno("Confirm",
            f"This will ERASE ALL DATA on {drive}\n\n"
            f"Edition: {self.license_info['edition'].upper()}\n\n"
            "Continue?")
            
        if confirm:
            self.create_btn.config(state="disabled")
            self.verify_btn.config(state="disabled")
            threading.Thread(target=self.create_media, args=(drive,), daemon=True).start()
    
    def update_status(self, progress, text):
        self.progress_var.set(progress)
        self.status_var.set(text)
        
    def create_media(self, drive):
        try:
            edition = self.license_info["edition"]
            iso_name = f"aegis-{edition}.iso"
            iso_url = f"{self.github_base}/{iso_name}"
            temp_dir = tempfile.gettempdir()
            iso_path = os.path.join(temp_dir, iso_name)
            
            self.root.after(0, lambda: self.update_status(5, f"Downloading {iso_name}..."))
            
            def progress_hook(count, block, total):
                if total > 0:
                    pct = min(5 + (count * block / total) * 60, 65)
                    mb = (count * block) / (1024*1024)
                    total_mb = total / (1024*1024)
                    self.root.after(0, lambda p=pct, m=mb, t=total_mb: 
                        self.update_status(p, f"Downloading: {m:.0f} / {t:.0f} MB"))
            
            try:
                urllib.request.urlretrieve(iso_url, iso_path, progress_hook)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Download Error",
                    f"Could not download ISO.\n\nMake sure '{iso_name}' exists at:\n{self.github_base}\n\nError: {e}"))
                self.root.after(0, self.reset_buttons)
                return
            
            self.root.after(0, lambda: self.update_status(70, "Preparing USB drive..."))
            
            license_data = {
                "license_key": self.license_info["key"],
                "edition": edition,
                "license_type": self.license_info["type"],
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            license_json = json.dumps(license_data, indent=2)
            
            self.root.after(0, lambda: self.update_status(80, "Writing ISO to USB..."))
            
            success = self.flash_usb(iso_path, drive, license_json)
            
            if success:
                self.root.after(0, lambda: self.update_status(100, "Complete!"))
                self.root.after(0, lambda: messagebox.showinfo("Success",
                    f"Aegis OS {edition.upper()} ready!\n\n"
                    "To install:\n"
                    "1. Restart your computer\n"
                    "2. Boot from USB\n"
                    "3. Follow the prompts\n\n"
                    "On first boot, you'll be asked to bind\n"
                    "your license to this computer."))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error",
                    "Failed to write to USB.\n\nTry running as Administrator."))
                    
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self.reset_buttons)
    
    def flash_usb(self, iso_path, drive, license_json):
        system = platform.system()
        drive_letter = drive.split(":")[0] if ":" in drive else drive.split()[0]
        
        try:
            if system == "Windows":
                temp_license = os.path.join(tempfile.gettempdir(), "aegis-license.json")
                with open(temp_license, "w") as f:
                    f.write(license_json)
                
                ps_script = f'''
$ErrorActionPreference = "Stop"
$drive = "{drive_letter}:"
$iso = "{iso_path.replace(os.sep, '/')}"
$license = "{temp_license.replace(os.sep, '/')}"

Write-Host "Formatting drive..."
Format-Volume -DriveLetter {drive_letter} -FileSystem FAT32 -Force -Confirm:$false | Out-Null

Write-Host "Mounting ISO..."
$mount = Mount-DiskImage -ImagePath $iso -PassThru
$vol = $mount | Get-Volume
$isoLetter = $vol.DriveLetter

Write-Host "Copying files from $isoLetter to $drive..."
Copy-Item -Path "${{isoLetter}}:\\*" -Destination "$drive\\" -Recurse -Force

Write-Host "Adding license..."
Copy-Item -Path $license -Destination "$drive\\aegis-license.json" -Force

Dismount-DiskImage -ImagePath $iso | Out-Null
Write-Host "Done!"
'''
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True
                )
                return "Done!" in result.stdout or result.returncode == 0
                
            elif system == "Linux":
                subprocess.run(['sudo', 'dd', f'if={iso_path}', f'of={drive_letter}', 
                               'bs=4M', 'status=progress'], check=True)
                subprocess.run(['sync'], check=True)
                
                subprocess.run(['sudo', 'mount', drive_letter, '/mnt'], check=True)
                with open('/mnt/aegis-license.json', 'w') as f:
                    f.write(license_json)
                subprocess.run(['sudo', 'umount', '/mnt'], check=True)
                return True
                
        except Exception as e:
            print(f"Flash error: {e}")
            return False
            
        return False
    
    def reset_buttons(self):
        self.create_btn.config(state="normal")
        self.verify_btn.config(state="normal")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AegisMediaCreator()
    app.run()
