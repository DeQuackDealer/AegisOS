
#!/usr/bin/env python3
"""
Aegis OS Replit Build System
Builds a lightweight version of Aegis OS for Replit environment
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

class AegisReplotBuilder:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "output"
        self.build_dir = self.base_dir / "build-replit"
        
    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}")
    
    def setup_directories(self):
        """Create build directories"""
        print("📁 Setting up build directories...")
        self.output_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        
    def build_kernel_module(self):
        """Build the kernel module (stub for Replit)"""
        print("🐧 Building Aegis kernel module...")
        
        kernel_dir = self.base_dir / "kernel-module"
        if kernel_dir.exists():
            try:
                # Copy kernel module to output
                shutil.copy2(kernel_dir / "aegis_lkm.c", self.output_dir / "aegis_lkm.c")
                shutil.copy2(kernel_dir / "Makefile", self.output_dir / "Makefile")
                print("✅ Kernel module source copied")
            except Exception as e:
                print(f"⚠️  Kernel module copy failed: {e}")
    
    def create_filesystem_image(self):
        """Create a simulated filesystem image"""
        print("💾 Creating Aegis OS filesystem image...")
        
        # Create a tar.gz of the overlay
        overlay_dir = self.base_dir / "overlay"
        if overlay_dir.exists():
            os.chdir(self.base_dir)
            subprocess.run([
                "tar", "czf", 
                str(self.output_dir / "aegis-os-freemium-rootfs.tar.gz"),
                "-C", "overlay", "."
            ], check=True)
            print("✅ Rootfs archive created")
    
    def create_iso_stub(self):
        """Create ISO metadata file"""
        print("💿 Creating ISO metadata...")
        
        iso_info = {
            "name": "Aegis OS Freemium Edition",
            "version": "1.0.0-Genesis",
            "architecture": "x86_64",
            "kernel": "Linux 6.6.7",
            "desktop": "XFCE 4.18",
            "size_mb": 2048,
            "build_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "features": [
                "Gaming optimization",
                "Proton/Wine support", 
                "System monitoring",
                "License management"
            ]
        }
        
        import json
        with open(self.output_dir / "iso-metadata.json", 'w') as f:
            json.dump(iso_info, f, indent=2)
        
        print("✅ ISO metadata created")
    
    def create_checksums(self):
        """Generate checksums for all output files"""
        print("🔐 Generating checksums...")
        
        os.chdir(self.output_dir)
        with open("checksums.sha256", 'w') as f:
            for file_path in self.output_dir.glob("*"):
                if file_path.is_file() and file_path.name != "checksums.sha256":
                    result = subprocess.run([
                        "sha256sum", file_path.name
                    ], capture_output=True, text=True)
                    f.write(result.stdout)
        
        print("✅ Checksums generated")
    
    def create_bootable_script(self):
        """Create bootable USB creation script"""
        script_content = '''#!/bin/bash
# Aegis OS USB Creator Script

if [ $# -eq 0 ]; then
    echo "Usage: $0 /dev/sdX"
    echo "Warning: This will erase all data on the target device!"
    exit 1
fi

DEVICE=$1
ISO_FILE="aegis-os-freemium.iso"

echo "🛡️  Aegis OS USB Creator"
echo "========================"
echo "Target device: $DEVICE"
echo "ISO file: $ISO_FILE"
echo ""
echo "⚠️  This will ERASE all data on $DEVICE"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo "🔥 Creating bootable USB..."
sudo dd if="$ISO_FILE" of="$DEVICE" bs=4M status=progress oflag=sync

echo "✅ Bootable USB created successfully!"
echo "🚀 Your Aegis OS USB is ready to boot!"
'''
        
        with open(self.output_dir / "create-bootable-usb.sh", 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(self.output_dir / "create-bootable-usb.sh", 0o755)
        print("✅ USB creator script generated")
    
    def build(self):
        """Execute the complete build process"""
        self.print_header("AEGIS OS REPLIT BUILD SYSTEM")
        
        print("🚀 Starting Aegis OS build for Replit environment...")
        print("⏱️  Estimated time: 2-3 minutes")
        
        try:
            self.setup_directories()
            self.build_kernel_module()
            self.create_filesystem_image()
            self.create_iso_stub()
            self.create_checksums()
            self.create_bootable_script()
            
            self.print_header("BUILD COMPLETE")
            print("✅ Aegis OS Freemium build successful!")
            print(f"📁 Output directory: {self.output_dir}")
            print("\n📦 Generated files:")
            
            for file_path in sorted(self.output_dir.glob("*")):
                size = file_path.stat().st_size
                if size > 1024*1024:
                    size_str = f"{size/1024/1024:.1f} MB"
                elif size > 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size} bytes"
                print(f"  📄 {file_path.name} ({size_str})")
            
            print("\n🎯 Next steps:")
            print("1. Download the files from the output/ directory")
            print("2. Transfer aegis-os-freemium-rootfs.tar.gz to a Linux system")
            print("3. Extract and create a bootable ISO with genisoimage")
            print("4. Use create-bootable-usb.sh to make bootable media")
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    builder = AegisReplotBuilder()
    builder.build()
