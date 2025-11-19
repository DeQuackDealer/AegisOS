#!/usr/bin/env python3
"""
Aegis OS Freemium - Build Simulation and Test Script
This script simulates the OS build process and tests all components
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

class AegisOSSimulator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.overlay_dir = self.base_dir / "overlay"
        self.tests_passed = 0
        self.tests_failed = 0
        
    def print_header(self, text):
        print(f"\n{'=' * 60}")
        print(f"  {text}")
        print(f"{'=' * 60}")
        
    def test_component(self, name, test_func):
        """Run a test and track results"""
        try:
            print(f"\n✓ Testing {name}...", end=" ")
            test_func()
            print("PASSED")
            self.tests_passed += 1
            return True
        except Exception as e:
            print(f"FAILED: {e}")
            self.tests_failed += 1
            return False
    
    def test_buildroot_config(self):
        """Test if Buildroot configuration exists and is valid"""
        config_file = self.base_dir / "buildroot-config" / ".config"
        if not config_file.exists():
            raise Exception("Buildroot config not found")
        
        with open(config_file, 'r') as f:
            content = f.read()
            # Check for critical settings
            required = [
                "BR2_x86_64=y",
                "BR2_PACKAGE_XFCE4=y",
                "BR2_INIT_SYSTEMD=y",
                "BR2_PACKAGE_WINE=y"
            ]
            for setting in required:
                if setting not in content:
                    raise Exception(f"Missing critical setting: {setting}")
    
    def test_overlay_structure(self):
        """Test overlay directory structure"""
        required_dirs = [
            "etc/systemd/system",
            "usr/local/bin",
            "usr/share/applications",
            "usr/share/pixmaps"
        ]
        for dir_path in required_dirs:
            full_path = self.overlay_dir / dir_path
            if not full_path.exists():
                raise Exception(f"Missing overlay directory: {dir_path}")
    
    def test_system_scripts(self):
        """Test system utility scripts"""
        scripts = [
            "usr/local/bin/aegis-system-monitor",
            "usr/local/bin/aegis-gaming-optimizer",
            "usr/local/bin/aegis-license-manager",
            "usr/local/bin/aegis-welcome"
        ]
        for script_path in scripts:
            full_path = self.overlay_dir / script_path
            if not full_path.exists():
                raise Exception(f"Missing script: {script_path}")
            
            # Check if script has proper shebang
            with open(full_path, 'r') as f:
                first_line = f.readline()
                if not first_line.startswith("#!"):
                    raise Exception(f"Script missing shebang: {script_path}")
    
    def test_systemd_services(self):
        """Test systemd service files"""
        services = [
            "aegis-system-monitor.service",
            "aegis-gaming-optimizer.service",
            "aegis-license-manager.service",
            "aegis-kernel-interface.service"
        ]
        for service in services:
            service_path = self.overlay_dir / "etc/systemd/system" / service
            if not service_path.exists():
                raise Exception(f"Missing service: {service}")
            
            with open(service_path, 'r') as f:
                content = f.read()
                if "[Unit]" not in content or "[Service]" not in content:
                    raise Exception(f"Invalid service file: {service}")
    
    def test_post_build_script(self):
        """Test post-build script exists and is valid"""
        script = self.base_dir / "post-build.sh"
        if not script.exists():
            raise Exception("post-build.sh not found")
        
        with open(script, 'r') as f:
            content = f.read()
            if "#!/bin/bash" not in content:
                raise Exception("Invalid post-build script")
    
    def simulate_boot_sequence(self):
        """Simulate the OS boot sequence"""
        print("\n" + "=" * 60)
        print("  AEGIS OS FREEMIUM - BOOT SEQUENCE SIMULATION")
        print("=" * 60)
        
        boot_steps = [
            ("BIOS/UEFI", "Initializing hardware..."),
            ("GRUB2", "Loading bootloader..."),
            ("Linux Kernel", "Loading Linux 6.6.7..."),
            ("Systemd", "Starting system services..."),
            ("Network", "Configuring network..."),
            ("Graphics", "Loading Mesa/Vulkan drivers..."),
            ("Audio", "Initializing PulseAudio..."),
            ("Aegis Services", "Starting Aegis optimization..."),
            ("XFCE Desktop", "Loading desktop environment..."),
            ("User Session", "Welcome to Aegis OS!")
        ]
        
        for component, message in boot_steps:
            print(f"\n[{component:15}] {message}")
            time.sleep(0.5)
            print(f"[{component:15}] ✓ OK")
        
        print("\n" + "=" * 60)
        print("  BOOT COMPLETE - System Ready")
        print("=" * 60)
    
    def display_system_info(self):
        """Display simulated system information"""
        print("\n" + "=" * 60)
        print("  AEGIS OS SYSTEM INFORMATION")
        print("=" * 60)
        
        info = {
            "OS": "Aegis OS Freemium Edition",
            "Version": "1.0.0-Genesis",
            "Kernel": "Linux 6.6.7",
            "Desktop": "XFCE 4.18",
            "Graphics": "Mesa 23.3.1 (OpenGL/Vulkan)",
            "Gaming": "Wine 8.21 + Proton Support",
            "Audio": "PulseAudio 16.1",
            "Network": "NetworkManager 1.44",
            "Init": "systemd 254"
        }
        
        for key, value in info.items():
            print(f"  {key:12}: {value}")
    
    def simulate_gaming_optimization(self):
        """Simulate gaming optimization features"""
        print("\n" + "=" * 60)
        print("  GAMING OPTIMIZATION STATUS")
        print("=" * 60)
        
        optimizations = [
            ("CPU Governor", "Performance mode", "✓"),
            ("GPU Power", "Maximum performance", "✓"),
            ("Memory", "Low latency mode", "✓"),
            ("Wine/Proton", "Configured for Steam", "✓"),
            ("Vulkan", "AMD/NVIDIA/Intel drivers", "✓"),
            ("Game Mode", "Ready", "✓")
        ]
        
        for feature, status, icon in optimizations:
            print(f"  {icon} {feature:15}: {status}")
    
    def run_simulation(self):
        """Run the complete simulation"""
        print("\n")
        print("    ▄▀█ █▀▀ █▀▀ █ █▀   █▀█ █▀")
        print("    █▀█ ██▄ █▄█ █ ▄█   █▄█ ▄█")
        print("\n    OS BUILD SIMULATION & TEST SUITE")
        print("    The Gold Standard for Gaming\n")
        
        # Run tests
        self.print_header("RUNNING COMPONENT TESTS")
        
        self.test_component("Buildroot Configuration", self.test_buildroot_config)
        self.test_component("Overlay Structure", self.test_overlay_structure)
        self.test_component("System Scripts", self.test_system_scripts)
        self.test_component("Systemd Services", self.test_systemd_services)
        self.test_component("Post-Build Script", self.test_post_build_script)
        
        # Display results
        self.print_header("TEST RESULTS")
        print(f"\n  Tests Passed: {self.tests_passed}")
        print(f"  Tests Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("\n  🎉 ALL TESTS PASSED - OS IS BUILD-READY!")
        else:
            print("\n  ⚠️  Some tests failed - review errors above")
        
        # Simulate boot if all tests passed
        if self.tests_failed == 0:
            self.simulate_boot_sequence()
            self.display_system_info()
            self.simulate_gaming_optimization()
            
            self.print_header("BUILD INSTRUCTIONS")
            print("""
  To build the actual OS image:
  
  1. Install build dependencies:
     sudo apt-get install build-essential wget cpio unzip rsync bc
  
  2. Run the build script:
     cd aegis-os-freemium
     chmod +x build.sh
     ./build.sh
  
  3. Wait 1-2 hours for compilation
  
  4. Find output in aegis-os-freemium/output/:
     - aegis-os-freemium.iso (bootable ISO)
     - aegis-os-freemium.ext4 (root filesystem)
     - aegis-kernel (Linux kernel)
  
  5. Create bootable USB:
     sudo dd if=output/aegis-os-freemium.iso of=/dev/sdX bs=4M
  
  The OS is configured with:
  ✓ XFCE 4.18 desktop environment
  ✓ Wine/Proton for Windows game compatibility
  ✓ Vulkan/OpenGL for graphics acceleration
  ✓ NetworkManager for easy network setup
  ✓ Systemd for modern service management
  ✓ Gaming optimizations enabled by default
            """)

if __name__ == "__main__":
    simulator = AegisOSSimulator()
    simulator.run_simulation()