#!/usr/bin/env python3
"""
Aegis OS License Manager
Hardware-bound license verification system

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh
"""

import os
import sys
import json
import base64
import hashlib
import subprocess
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Cryptography imports (build-time dependency)
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.backends import default_backend
    from cryptography.exceptions import InvalidSignature
except ImportError:
    # Stub for raw source - will be resolved during build
    pass


class LicenseType(Enum):
    FREEMIUM = "freemium"
    ANNUAL = "annual"
    LIFETIME = "lifetime"
    TRIAL = "trial"


class LicenseStatus(Enum):
    VALID = "valid"
    EXPIRED = "expired"
    INVALID_HARDWARE = "invalid_hardware"
    INVALID_SIGNATURE = "invalid_signature"
    NOT_FOUND = "not_found"
    REVOKED = "revoked"


@dataclass
class LicenseInfo:
    license_key: str
    edition: str
    license_type: LicenseType
    hardware_id: str
    issued_date: datetime
    expiry_date: Optional[datetime]
    status: LicenseStatus
    customer_email: Optional[str]


class LicenseManager:
    """
    Hardware-bound license verification using RSA-2048.
    
    License Key Format:
    AEGIS-XXXX-XXXX-XXXX-XXXX
    
    Where the key encodes:
    - Edition identifier
    - License type
    - Hardware binding hash
    - RSA signature
    """
    
    LICENSE_PATH = Path("/etc/aegis/license.key")
    PUBLIC_KEY_PATH = Path("/etc/aegis/aegis_public.pem")
    CACHE_PATH = Path("/var/lib/aegis/license_cache.json")
    
    # Public key embedded at build time
    # %%EMBED_PUBLIC_KEY%%
    EMBEDDED_PUBLIC_KEY = None  # Replaced during build
    
    def __init__(self):
        self._current_license: Optional[LicenseInfo] = None
        self._hardware_id: Optional[str] = None
        self._public_key = None
        
    def initialize(self) -> bool:
        """Initialize license manager and load public key"""
        # TODO: Load public key and verify system state
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_hardware_id(self) -> str:
        """Generate unique hardware identifier for license binding"""
        if self._hardware_id:
            return self._hardware_id
            
        components = []
        
        # CPU info
        cpu_id = self._get_cpu_id()
        if cpu_id:
            components.append(f"CPU:{cpu_id}")
            
        # Machine ID (systemd)
        machine_id = self._get_machine_id()
        if machine_id:
            components.append(f"MID:{machine_id}")
            
        # First disk serial
        disk_serial = self._get_disk_serial()
        if disk_serial:
            components.append(f"DSK:{disk_serial}")
            
        # MAC address of primary interface
        mac = self._get_primary_mac()
        if mac:
            components.append(f"MAC:{mac}")
            
        # Generate deterministic hash
        combined = "|".join(sorted(components))
        raw_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        # Format as readable ID
        self._hardware_id = f"HW-{raw_hash[:8]}-{raw_hash[8:16]}-{raw_hash[16:24]}"
        return self._hardware_id
    
    def _get_cpu_id(self) -> Optional[str]:
        """Get CPU identifier"""
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":")[1].strip()[:32]
        except Exception:
            pass
        return None
    
    def _get_machine_id(self) -> Optional[str]:
        """Get systemd machine ID"""
        try:
            with open("/etc/machine-id", "r") as f:
                return f.read().strip()[:16]
        except Exception:
            pass
        return None
    
    def _get_disk_serial(self) -> Optional[str]:
        """Get primary disk serial number"""
        try:
            result = subprocess.run(
                ["lsblk", "-ndo", "SERIAL", "/dev/sda"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()[:16]
        except Exception:
            pass
        return None
    
    def _get_primary_mac(self) -> Optional[str]:
        """Get primary network interface MAC address"""
        try:
            # Get default route interface
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                parts = result.stdout.split()
                if "dev" in parts:
                    iface = parts[parts.index("dev") + 1]
                    mac_path = Path(f"/sys/class/net/{iface}/address")
                    if mac_path.exists():
                        return mac_path.read_text().strip().replace(":", "")
        except Exception:
            pass
        return None
    
    def verify_license(self, license_key: str) -> Tuple[LicenseStatus, Optional[LicenseInfo]]:
        """
        Verify license key authenticity and hardware binding.
        
        Verification steps:
        1. Parse license key format
        2. Verify RSA-2048 signature
        3. Check hardware ID matches
        4. Verify expiry date (if applicable)
        5. Check revocation list (online if available)
        """
        # TODO: Implement full verification logic
        raise NotImplementedError("Build required: ./build.sh")
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """Activate license and bind to hardware"""
        # TODO: Implement activation logic
        raise NotImplementedError("Build required: ./build.sh")
    
    def deactivate_license(self) -> bool:
        """Deactivate current license (requires online)"""
        # TODO: Implement deactivation
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_current_license(self) -> Optional[LicenseInfo]:
        """Get currently active license info"""
        return self._current_license
    
    def is_licensed(self) -> bool:
        """Check if system has valid license"""
        if not self._current_license:
            return False
        return self._current_license.status == LicenseStatus.VALID
    
    def get_edition_features(self, edition: str) -> Dict[str, bool]:
        """Get feature flags for edition"""
        # Base features (Freemium)
        features = {
            "proton_support": True,
            "wine_support": True,
            "steam_integration": True,
            "basic_updates": True,
            "driver_manager": True,
            "community_support": True,
            # Premium features (disabled in base)
            "dual_gpu": False,
            "streaming_studio": False,
            "priority_updates": False,
            "anti_cheat_support": False,
            "performance_services": False,
            "ai_features": False,
        }
        
        # Upgrade based on edition
        if edition in ["basic", "gamer", "ai-developer", "gamer-ai", "server"]:
            features["priority_updates"] = True
            
        if edition in ["gamer", "gamer-ai"]:
            features["dual_gpu"] = True
            features["streaming_studio"] = True
            features["anti_cheat_support"] = True
            features["performance_services"] = True
            
        if edition in ["ai-developer", "gamer-ai"]:
            features["ai_features"] = True
            
        return features


# Build marker
# %%BUILD_MARKER:LICENSE_MANAGER%%
