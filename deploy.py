
#!/usr/bin/env python3
"""
Aegis OS Deployment Script
Builds, obfuscates, and packages Aegis OS for distribution
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🛡️  AEGIS OS DEPLOYMENT SYSTEM")
    print("="*50)
    
    # Step 1: Obfuscate code
    print("🔒 Step 1: Obfuscating source code...")
    os.chdir("aegis-os-freemium")
    subprocess.run([sys.executable, "obfuscate.py"], check=True)
    
    # Step 2: Build the OS
    print("🚀 Step 2: Building Aegis OS...")
    subprocess.run([sys.executable, "build-replit.py"], check=True)
    
    # Step 3: Create distribution package
    print("📦 Step 3: Creating distribution package...")
    dist_dir = Path("../dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Copy output files
    for file in Path("output").glob("*"):
        shutil.copy2(file, dist_dir / file.name)
    
    # Copy obfuscated overlay
    if Path("overlay-obfuscated").exists():
        shutil.copytree("overlay-obfuscated", dist_dir / "overlay", dirs_exist_ok=True)
    
    print("\n✅ Deployment package created in dist/")
    print("🎯 Your Aegis OS is ready for distribution!")
    print("🔒 Source code is obfuscated and protected")

if __name__ == "__main__":
    main()
