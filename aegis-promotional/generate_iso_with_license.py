#!/usr/bin/env python3
"""
Aegis OS ISO Builder with License Integration
Generates customized ISO files with embedded license validation
"""

import os
import sys
import json
import subprocess
import shutil
import tempfile
from pathlib import Path
from license_system import AegisLicenseSystem

class AegisISOBuilder:
    """Builds customized Aegis OS ISOs with license integration"""
    
    def __init__(self, base_iso_path: str, output_dir: str = "builds"):
        self.base_iso = Path(base_iso_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def customize_iso_for_tier(self, tier: str, license_key: str = None, 
                              customer_email: str = None) -> Path:
        """
        Create a customized ISO for a specific tier with optional pre-embedded license
        
        Args:
            tier: The OS tier (freemium, basic, gamer, ai-dev, server)
            license_key: Optional pre-embedded license key
            customer_email: Customer email for personalization
            
        Returns:
            Path to the generated ISO file
        """
        print(f"Building Aegis OS ISO - {tier.upper()} Edition")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract base ISO
            print("Extracting base ISO...")
            extract_dir = temp_path / "iso_extract"
            extract_dir.mkdir()
            
            # Use 7z or xorriso to extract ISO
            subprocess.run([
                "7z", "x", "-o" + str(extract_dir), str(self.base_iso)
            ], check=True, capture_output=True)
            
            # Customize for tier
            self._customize_for_tier(extract_dir, tier)
            
            # Embed license if provided
            if license_key:
                self._embed_license(extract_dir, license_key, customer_email)
            
            # Add boot-time license validation script
            self._add_license_validation(extract_dir)
            
            # Rebuild ISO
            output_iso = self._rebuild_iso(extract_dir, tier)
            
            print(f"ISO built successfully: {output_iso}")
            return output_iso
    
    def _customize_for_tier(self, iso_dir: Path, tier: str):
        """Apply tier-specific customizations"""
        
        # Create tier configuration
        tier_config = {
            'freemium': {
                'packages': ['xfce4', 'wine', 'firefox', 'basic-tools'],
                'drivers': ['nouveau'],
                'services': ['basic-desktop'],
                'wallpaper': 'aegis_freemium.jpg',
                'memory_limit': '4G'
            },
            'basic': {
                'packages': ['xfce4', 'wine', 'proton', 'firefox', 'security-suite',
                           'vpn-client', 'encryption-tools', 'anti-ransomware'],
                'drivers': ['nouveau', 'nvidia-470'],
                'services': ['enhanced-security', 'vpn', 'firewall'],
                'wallpaper': 'aegis_basic.jpg',
                'memory_limit': '16G'
            },
            'gamer': {
                'packages': ['xfce4-gaming', 'wine', 'proton', 'steam', 'lutris',
                           'gamemode', 'mangohud', 'vkbasalt', 'gaming-tools'],
                'drivers': ['nvidia-latest', 'amd-latest', 'vulkan'],
                'services': ['gaming-optimization', 'rgb-control', 'low-latency'],
                'wallpaper': 'aegis_gamer.jpg',
                'memory_limit': '32G'
            },
            'ai-dev': {
                'packages': ['xfce4-dev', 'docker', 'kubernetes', 'jupyter-lab',
                           'pytorch', 'tensorflow', 'cuda-toolkit', 'ml-libraries'],
                'drivers': ['nvidia-cuda', 'rocm', 'intel-oneapi'],
                'services': ['docker', 'jupyter', 'cuda-compute'],
                'wallpaper': 'aegis_ai_dev.jpg',
                'memory_limit': '64G'
            },
            'server': {
                'packages': ['minimal-base', 'docker', 'kubernetes', 'monitoring',
                           'ha-tools', 'clustering', 'load-balancer'],
                'drivers': ['server-optimized'],
                'services': ['kubernetes', 'monitoring', 'high-availability'],
                'wallpaper': None,  # Headless
                'memory_limit': None  # Unlimited
            }
        }
        
        config = tier_config.get(tier, tier_config['freemium'])
        
        # Write tier configuration
        config_path = iso_dir / "etc" / "aegis" / "tier.conf"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump({
                'tier': tier,
                'config': config,
                'build_date': str(Path.ctime(Path.cwd()))
            }, f, indent=2)
        
        # Customize package list
        packages_file = iso_dir / "var" / "lib" / "aegis" / "packages.list"
        packages_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(packages_file, 'w') as f:
            f.write('\n'.join(config['packages']))
        
        print(f"Applied {tier} tier customizations")
    
    def _embed_license(self, iso_dir: Path, license_key: str, email: str = None):
        """Embed a license key in the ISO"""
        
        license_dir = iso_dir / "etc" / "aegis"
        license_dir.mkdir(parents=True, exist_ok=True)
        
        # Create license cache file
        license_cache = license_dir / ".license_cache"
        with open(license_cache, 'w') as f:
            f.write(license_key)
        
        # Create license info file
        if email:
            license_info = license_dir / "license_info.json"
            with open(license_info, 'w') as f:
                json.dump({
                    'licensed_to': email,
                    'license_key': license_key[:10] + '...',  # Partial for security
                    'embedded': True
                }, f, indent=2)
        
        print(f"Embedded license key in ISO")
    
    def _add_license_validation(self, iso_dir: Path):
        """Add license validation to boot process"""
        
        # Copy license validation script
        boot_script_src = Path("license_boot_script.sh")
        boot_script_dst = iso_dir / "usr" / "local" / "bin" / "aegis-license-check"
        boot_script_dst.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(boot_script_src, boot_script_dst)
        boot_script_dst.chmod(0o755)
        
        # Add to systemd service
        service_file = iso_dir / "etc" / "systemd" / "system" / "aegis-license.service"
        service_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(service_file, 'w') as f:
            f.write("""[Unit]
Description=Aegis OS License Validation
Before=graphical.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/aegis-license-check
RemainAfterExit=yes
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=multi-user.target
""")
        
        # Enable the service
        enable_link = iso_dir / "etc" / "systemd" / "system" / "multi-user.target.wants" / "aegis-license.service"
        enable_link.parent.mkdir(parents=True, exist_ok=True)
        enable_link.symlink_to("../aegis-license.service")
        
        print("Added license validation to boot process")
    
    def _rebuild_iso(self, iso_dir: Path, tier: str) -> Path:
        """Rebuild the ISO file"""
        
        output_name = f"aegis-os-{tier}-{Path.ctime(Path.cwd()):.0f}.iso"
        output_path = self.output_dir / output_name
        
        print(f"Building ISO: {output_name}")
        
        # Use xorriso to create bootable ISO
        subprocess.run([
            "xorriso",
            "-as", "mkisofs",
            "-o", str(output_path),
            "-b", "isolinux/isolinux.bin",
            "-c", "isolinux/boot.cat",
            "-no-emul-boot",
            "-boot-load-size", "4",
            "-boot-info-table",
            "-J", "-R", "-V", f"AEGIS_OS_{tier.upper()}",
            str(iso_dir)
        ], check=True)
        
        # Calculate checksum
        checksum_file = output_path.with_suffix('.sha256')
        result = subprocess.run(
            ["sha256sum", str(output_path)],
            capture_output=True,
            text=True
        )
        
        with open(checksum_file, 'w') as f:
            f.write(result.stdout)
        
        return output_path

def main():
    """Main entry point for ISO builder"""
    
    if len(sys.argv) < 3:
        print("Usage: python3 generate_iso_with_license.py <base_iso> <tier> [license_key] [email]")
        print("Tiers: freemium, basic, gamer, ai-dev, server")
        sys.exit(1)
    
    base_iso = sys.argv[1]
    tier = sys.argv[2]
    license_key = sys.argv[3] if len(sys.argv) > 3 else None
    email = sys.argv[4] if len(sys.argv) > 4 else None
    
    if not os.path.exists(base_iso):
        print(f"Error: Base ISO not found: {base_iso}")
        sys.exit(1)
    
    builder = AegisISOBuilder(base_iso)
    output_iso = builder.customize_iso_for_tier(tier, license_key, email)
    
    print(f"\nSuccess! ISO generated at: {output_iso}")
    print(f"Size: {output_iso.stat().st_size / (1024**3):.2f} GB")

if __name__ == "__main__":
    main()