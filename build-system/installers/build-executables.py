#!/usr/bin/env python3
"""
Aegis OS Installer Packager
Creates standalone executables from the Python installers.
Users can double-click to run - no Python or command line needed.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()

INSTALLERS = {
    "media-tool": {
        "script": "aegis-media-tool.py",
        "name": "AegisOS-Media-Creation-Tool",
        "icon": None
    },
    "freemium": {
        "script": "aegis-installer-freemium.py",
        "name": "AegisOS-Freemium-Installer",
        "icon": None
    },
    "licensed": {
        "script": "aegis-installer-licensed.py",
        "name": "AegisOS-Licensed-Installer",
        "icon": None
    }
}

DATA_FILES = [
    "manifest.json",
    "public_key.pem",
    "activation_client.py"
]

def build_installer(installer_key: str, target_os: str = "linux"):
    """Build a standalone executable for the specified installer."""
    
    config = INSTALLERS[installer_key]
    script_path = SCRIPT_DIR / config["script"]
    output_name = config["name"]
    
    if not script_path.exists():
        print(f"[!] Script not found: {script_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Building: {output_name}")
    print(f"{'='*60}")
    
    dist_dir = SCRIPT_DIR / "dist"
    build_dir = SCRIPT_DIR / "build"
    
    add_data = []
    for data_file in DATA_FILES:
        data_path = SCRIPT_DIR / data_file
        if data_path.exists():
            separator = ";" if sys.platform == "win32" else ":"
            add_data.append(f"--add-data={data_file}{separator}.")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={output_name}",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        "--clean",
        "--noconfirm",
    ]
    
    cmd.extend(add_data)
    
    if config["icon"] and (SCRIPT_DIR / config["icon"]).exists():
        cmd.append(f"--icon={config['icon']}")
    
    cmd.append(str(script_path))
    
    print(f"[*] Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR, check=True, 
                                capture_output=True, text=True)
        print(result.stdout)
        
        if target_os == "linux":
            output_path = dist_dir / output_name
        else:
            output_path = dist_dir / f"{output_name}.exe"
        
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"[+] SUCCESS: {output_path}")
            print(f"    Size: {size_mb:.1f} MB")
            return True
        else:
            print(f"[!] Output not found: {output_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[!] Build failed: {e}")
        print(e.stderr)
        return False

def clean_build_artifacts():
    """Remove temporary build files."""
    for folder in ["build", "__pycache__"]:
        folder_path = SCRIPT_DIR / folder
        if folder_path.exists():
            shutil.rmtree(folder_path)
            print(f"[*] Cleaned: {folder}")
    
    for spec_file in SCRIPT_DIR.glob("*.spec"):
        spec_file.unlink()
        print(f"[*] Removed: {spec_file.name}")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║           AEGIS OS INSTALLER PACKAGER v3.0.0              ║
    ║         Creates Standalone Double-Click Executables       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    for key in INSTALLERS:
        success = build_installer(key)
        results[key] = success
    
    clean_build_artifacts()
    
    print("\n" + "="*60)
    print("BUILD SUMMARY")
    print("="*60)
    
    dist_dir = SCRIPT_DIR / "dist"
    
    for key, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        name = INSTALLERS[key]["name"]
        print(f"  {status}: {name}")
    
    if all(results.values()):
        print(f"\n[+] All executables built successfully!")
        print(f"[+] Location: {dist_dir}/")
        print(f"\nUsers can now double-click to run - no command line needed!")
    else:
        print(f"\n[!] Some builds failed. Check errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
