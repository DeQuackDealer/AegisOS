#!/usr/bin/env python3
"""
Aegis OS Media Creation Tool
Simple Windows-like installer that downloads and creates bootable USB
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import platform
import os
import sys
import urllib.request
import tempfile
import json
import hashlib

if platform.system() == "Windows":
    import ctypes

class AegisMediaCreator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aegis OS Media Creation Tool")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        
        self.edition_var = tk.StringVar(value="freemium")
        self.license_key = tk.StringVar()
        self.selected_drive = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Select your edition and USB drive")
        
        self.github_base = "https://github.com/DeQuackDealer/AegisOSRepo/releases/latest/download"
        self.api_base = "https://aegis-os.replit.app"
        
        self.setup_ui()
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#1a1a2e", foreground="white", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#4da6ff")
        style.configure("TButton", font=("Segoe UI", 11), padding=10)
        style.configure("TRadiobutton", background="#1a1a2e", foreground="white", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("Horizontal.TProgressbar", thickness=20)
        
        main_frame = tk.Frame(self.root, bg="#1a1a2e", padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        logo_frame = tk.Frame(main_frame, bg="#1a1a2e")
        logo_frame.pack(pady=(0, 20))
        
        tk.Label(logo_frame, text="🛡️", font=("Segoe UI", 40), bg="#1a1a2e", fg="#4da6ff").pack()
        ttk.Label(logo_frame, text="Aegis OS", style="Title.TLabel").pack()
        ttk.Label(logo_frame, text="Media Creation Tool", style="TLabel").pack()
        
        edition_frame = tk.LabelFrame(main_frame, text="Select Edition", bg="#1a1a2e", fg="white", 
                                       font=("Segoe UI", 10, "bold"), padx=15, pady=10)
        edition_frame.pack(fill="x", pady=10)
        
        editions = [
            ("Freemium (Free)", "freemium", "$0"),
            ("Basic Edition", "basic", "$19"),
            ("Gamer Edition ⭐", "gamer", "$69"),
            ("AI Developer", "ai-dev", "$79"),
            ("Workplace", "workplace", "$9"),
        ]
        
        for name, value, price in editions:
            frame = tk.Frame(edition_frame, bg="#1a1a2e")
            frame.pack(fill="x", pady=2)
            ttk.Radiobutton(frame, text=name, variable=self.edition_var, 
                           value=value, style="TRadiobutton",
                           command=self.on_edition_change).pack(side="left")
            tk.Label(frame, text=price, bg="#1a1a2e", fg="#888", 
                    font=("Segoe UI", 9)).pack(side="right")
        
        license_frame = tk.LabelFrame(main_frame, text="License Key (for paid editions)", 
                                       bg="#1a1a2e", fg="white", font=("Segoe UI", 10, "bold"),
                                       padx=15, pady=10)
        license_frame.pack(fill="x", pady=10)
        
        self.license_entry = ttk.Entry(license_frame, textvariable=self.license_key, 
                                        font=("Consolas", 11), width=40)
        self.license_entry.pack(fill="x", pady=5)
        self.license_entry.config(state="disabled")
        
        tk.Label(license_frame, text="Enter the license key from your purchase email", 
                bg="#1a1a2e", fg="#888", font=("Segoe UI", 8)).pack()
        
        drive_frame = tk.LabelFrame(main_frame, text="Select USB Drive", bg="#1a1a2e", 
                                     fg="white", font=("Segoe UI", 10, "bold"), padx=15, pady=10)
        drive_frame.pack(fill="x", pady=10)
        
        drive_select_frame = tk.Frame(drive_frame, bg="#1a1a2e")
        drive_select_frame.pack(fill="x")
        
        self.drive_combo = ttk.Combobox(drive_select_frame, textvariable=self.selected_drive,
                                         state="readonly", font=("Segoe UI", 10), width=30)
        self.drive_combo.pack(side="left", fill="x", expand=True, pady=5)
        
        ttk.Button(drive_select_frame, text="🔄", width=3, 
                  command=self.refresh_drives).pack(side="right", padx=(5, 0))
        
        tk.Label(drive_frame, text="⚠️ All data on the selected drive will be erased!", 
                bg="#1a1a2e", fg="#ff6b6b", font=("Segoe UI", 9, "bold")).pack(pady=(5, 0))
        
        progress_frame = tk.Frame(main_frame, bg="#1a1a2e")
        progress_frame.pack(fill="x", pady=20)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                             maximum=100, style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var,
                                      bg="#1a1a2e", fg="#aaa", font=("Segoe UI", 9))
        self.status_label.pack()
        
        button_frame = tk.Frame(main_frame, bg="#1a1a2e")
        button_frame.pack(fill="x", pady=10)
        
        self.create_btn = tk.Button(button_frame, text="Create Bootable USB", 
                                     font=("Segoe UI", 12, "bold"), bg="#4da6ff", fg="white",
                                     activebackground="#3d8bd9", activeforeground="white",
                                     relief="flat", padx=20, pady=12, cursor="hand2",
                                     command=self.start_creation)
        self.create_btn.pack(fill="x")
        
        footer = tk.Label(main_frame, text="© 2024 Aegis OS | aegis-os.com", 
                         bg="#1a1a2e", fg="#555", font=("Segoe UI", 8))
        footer.pack(side="bottom", pady=(20, 0))
        
        self.refresh_drives()
        
    def on_edition_change(self):
        edition = self.edition_var.get()
        if edition == "freemium":
            self.license_entry.config(state="disabled")
            self.license_key.set("")
        else:
            self.license_entry.config(state="normal")
            
    def refresh_drives(self):
        drives = self.get_usb_drives()
        self.drive_combo['values'] = drives
        if drives:
            self.drive_combo.current(0)
        self.status_var.set(f"Found {len(drives)} USB drive(s)")
            
    def get_usb_drives(self):
        drives = []
        system = platform.system()
        
        if system == "Windows":
            try:
                import ctypes
                bitmask = ctypes.windll.kernel32.GetLogicalDrives()
                for letter in 'DEFGHIJKLMNOPQRSTUVWXYZ':
                    if bitmask & 1:
                        drive_path = f"{letter}:\\"
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
                        if drive_type == 2:
                            try:
                                total, used, free = self.get_drive_space(drive_path)
                                size_gb = total / (1024**3)
                                drives.append(f"{letter}: ({size_gb:.1f} GB)")
                            except:
                                drives.append(f"{letter}: (Unknown size)")
                    bitmask >>= 1
            except Exception as e:
                drives.append("Error detecting drives")
                
        elif system == "Linux":
            try:
                result = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,TRAN', '-n'], 
                                       capture_output=True, text=True)
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 3 and parts[2] == 'usb':
                        drives.append(f"/dev/{parts[0]} ({parts[1]})")
            except:
                pass
                
        elif system == "Darwin":
            try:
                result = subprocess.run(['diskutil', 'list', 'external'], 
                                       capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if '/dev/disk' in line:
                        parts = line.split()
                        if parts:
                            drives.append(parts[0])
            except:
                pass
                
        return drives if drives else ["No USB drives found"]
    
    def get_drive_space(self, path):
        if platform.system() == "Windows":
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                path, None, ctypes.pointer(total_bytes), ctypes.pointer(free_bytes))
            return total_bytes.value, total_bytes.value - free_bytes.value, free_bytes.value
        else:
            st = os.statvfs(path)
            total = st.f_blocks * st.f_frsize
            free = st.f_bavail * st.f_frsize
            return total, total - free, free
    
    def validate_license(self, edition, license_key):
        if edition == "freemium":
            return True, "Freemium - no license needed"
            
        if not license_key:
            return False, "License key required for paid editions"
            
        try:
            url = f"{self.api_base}/api/validate-license"
            data = json.dumps({"license_key": license_key, "edition": edition}).encode()
            req = urllib.request.Request(url, data=data, 
                                          headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read())
                if result.get("valid"):
                    return True, "License validated!"
                return False, result.get("error", "Invalid license")
        except Exception as e:
            return True, "Offline mode - license will be verified on first boot"
    
    def start_creation(self):
        edition = self.edition_var.get()
        license_key = self.license_key.get().strip()
        drive = self.selected_drive.get()
        
        if "No USB" in drive or "Error" in drive:
            messagebox.showerror("Error", "Please select a valid USB drive")
            return
            
        valid, msg = self.validate_license(edition, license_key)
        if not valid:
            messagebox.showerror("License Error", msg)
            return
            
        confirm = messagebox.askyesno(
            "Confirm", 
            f"This will ERASE ALL DATA on {drive}.\n\n"
            f"Edition: {edition.upper()}\n\n"
            "Are you sure you want to continue?"
        )
        
        if confirm:
            self.create_btn.config(state="disabled")
            thread = threading.Thread(target=self.create_media, args=(edition, license_key, drive))
            thread.daemon = True
            thread.start()
    
    def update_progress(self, value, status):
        self.progress_var.set(value)
        self.status_var.set(status)
        self.root.update_idletasks()
    
    def create_media(self, edition, license_key, drive):
        try:
            self.update_progress(5, "Preparing download...")
            
            iso_name = f"aegis-{edition}.iso"
            iso_url = f"{self.github_base}/{iso_name}"
            
            temp_dir = tempfile.gettempdir()
            iso_path = os.path.join(temp_dir, iso_name)
            
            self.update_progress(10, f"Downloading {iso_name}...")
            
            try:
                self.download_file(iso_url, iso_path)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Download Error", 
                    f"Could not download ISO.\n\nMake sure the ISO is uploaded to:\n{iso_url}\n\nError: {str(e)}"))
                self.root.after(0, lambda: self.create_btn.config(state="normal"))
                return
            
            self.update_progress(70, "Writing to USB drive...")
            
            drive_letter = drive.split(":")[0] if ":" in drive else drive.split()[0]
            
            success = self.write_to_usb(iso_path, drive_letter, edition, license_key)
            
            if success:
                self.update_progress(100, "Complete! You can now boot from the USB.")
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"Aegis OS {edition.upper()} has been written to {drive}!\n\n"
                    "You can now:\n"
                    "1. Restart your computer\n"
                    "2. Boot from the USB drive\n"
                    "3. Follow the installation prompts"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", 
                    "Failed to write to USB. Try running as Administrator."))
                    
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.create_btn.config(state="normal"))
    
    def download_file(self, url, destination):
        def report_progress(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(10 + (downloaded / total_size) * 60, 70)
                size_mb = downloaded / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                self.root.after(0, lambda: self.update_progress(percent, 
                    f"Downloading: {size_mb:.0f} / {total_mb:.0f} MB"))
        
        urllib.request.urlretrieve(url, destination, report_progress)
    
    def write_to_usb(self, iso_path, drive, edition, license_key):
        system = platform.system()
        
        try:
            if system == "Windows":
                ps_script = f'''
                $drive = "{drive}:"
                Write-Host "Formatting drive..."
                Format-Volume -DriveLetter {drive} -FileSystem FAT32 -Force -Confirm:$false
                
                Write-Host "Mounting ISO..."
                $mount = Mount-DiskImage -ImagePath "{iso_path}" -PassThru
                $isoLetter = ($mount | Get-Volume).DriveLetter
                
                Write-Host "Copying files..."
                Copy-Item -Path "${{isoLetter}}:\\*" -Destination "$drive\\" -Recurse -Force
                
                Dismount-DiskImage -ImagePath "{iso_path}"
                '''
                
                license_data = {
                    "edition": edition,
                    "license_key": license_key,
                    "created": str(os.popen("date /t").read().strip())
                }
                license_path = os.path.join(f"{drive}:", "aegis-license.json")
                
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True, shell=True
                )
                
                if license_key:
                    with open(license_path, 'w') as f:
                        json.dump(license_data, f)
                
                return result.returncode == 0
                
            elif system == "Linux":
                subprocess.run(['sudo', 'dd', f'if={iso_path}', f'of={drive}', 
                               'bs=4M', 'status=progress'], check=True)
                subprocess.run(['sync'], check=True)
                return True
                
            elif system == "Darwin":
                subprocess.run(['sudo', 'dd', f'if={iso_path}', f'of={drive}', 
                               'bs=4m'], check=True)
                return True
                
        except Exception as e:
            print(f"Write error: {e}")
            return False
        
        return False
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AegisMediaCreator()
    app.run()
