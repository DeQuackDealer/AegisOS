#!/usr/bin/env python3
"""
Aegis OS Core Library
Foundation module for all Aegis OS editions

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Build-time constants (replaced during compilation)
AEGIS_VERSION = "%%VERSION%%"
AEGIS_BUILD_DATE = "%%BUILD_DATE%%"
AEGIS_EDITION = "%%EDITION%%"


class AegisEdition(Enum):
    FREEMIUM = "freemium"
    BASIC = "basic"
    WORKPLACE = "workplace"
    GAMER = "gamer"
    AI_DEVELOPER = "ai-developer"
    GAMER_AI = "gamer-ai"
    SERVER = "server"


@dataclass
class SystemInfo:
    cpu_model: str
    cpu_cores: int
    ram_total_gb: float
    gpu_vendor: str
    gpu_model: str
    disk_type: str
    kernel_version: str


class AegisCore:
    """Core functionality for Aegis OS"""
    
    CONFIG_PATH = Path("/etc/aegis")
    DATA_PATH = Path("/var/lib/aegis")
    LICENSE_PATH = Path("/etc/aegis/license.key")
    
    def __init__(self):
        self._edition: Optional[AegisEdition] = None
        self._licensed: bool = False
        self._hardware_id: Optional[str] = None
        self._config: Dict[str, Any] = {}
        
    def initialize(self) -> bool:
        """Initialize Aegis core system"""
        # TODO: Implement initialization logic
        # This is a stub - actual implementation in compiled version
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_hardware_id(self) -> str:
        """Generate unique hardware identifier for license binding"""
        if self._hardware_id:
            return self._hardware_id
            
        # Collect hardware identifiers
        components = []
        
        # CPU ID
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        components.append(line.strip())
                        break
        except FileNotFoundError:
            pass
            
        # Machine ID
        try:
            with open("/etc/machine-id", "r") as f:
                components.append(f.read().strip())
        except FileNotFoundError:
            pass
            
        # DMI product UUID
        try:
            result = subprocess.run(
                ["cat", "/sys/class/dmi/id/product_uuid"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                components.append(result.stdout.strip())
        except Exception:
            pass
            
        # Generate hash
        combined = "|".join(components)
        self._hardware_id = hashlib.sha256(combined.encode()).hexdigest()[:32]
        return self._hardware_id
    
    def verify_license(self, license_key: str) -> bool:
        """Verify license key against hardware ID"""
        # TODO: RSA-2048 signature verification
        # Stub implementation
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_system_info(self) -> SystemInfo:
        """Gather system hardware information"""
        # TODO: Implement full system detection
        raise NotImplementedError("Build required: ./build.sh")
    
    def detect_gpu(self) -> Dict[str, Any]:
        """Detect installed GPU(s)"""
        gpus = []
        
        try:
            # Try lspci
            result = subprocess.run(
                ["lspci", "-nn"],
                capture_output=True, text=True
            )
            
            for line in result.stdout.splitlines():
                if "VGA" in line or "3D" in line:
                    gpus.append({
                        "raw": line,
                        "vendor": self._parse_gpu_vendor(line),
                        "driver": None  # Detected at runtime
                    })
        except Exception as e:
            return {"error": str(e), "gpus": []}
            
        return {"gpus": gpus}
    
    def _parse_gpu_vendor(self, line: str) -> str:
        """Parse GPU vendor from lspci output"""
        if "NVIDIA" in line.upper():
            return "nvidia"
        elif "AMD" in line.upper() or "ATI" in line.upper():
            return "amd"
        elif "INTEL" in line.upper():
            return "intel"
        return "unknown"


class ProtonManager:
    """Manage Proton/Wine for Windows game compatibility"""
    
    PROTON_PATH = Path.home() / ".steam/steam/compatibilitytools.d"
    WINE_PREFIX = Path.home() / ".wine"
    
    def __init__(self):
        self._installed_protons: List[str] = []
        self._dxvk_version: Optional[str] = None
        
    def detect_proton_versions(self) -> List[str]:
        """Detect installed Proton versions"""
        # TODO: Scan for installed Proton versions
        raise NotImplementedError("Build required: ./build.sh")
    
    def install_proton_ge(self, version: str = "latest") -> bool:
        """Install Proton-GE for improved compatibility"""
        # TODO: Download and install Proton-GE
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_dxvk(self, prefix: Path) -> bool:
        """Configure DXVK for DirectX 9/10/11 translation"""
        # TODO: Install and configure DXVK
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_vkd3d(self, prefix: Path) -> bool:
        """Configure VKD3D-Proton for DirectX 12"""
        # TODO: Install and configure VKD3D-Proton
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_env_vars(self, game_id: Optional[str] = None) -> Dict[str, str]:
        """Get Proton environment variables"""
        env = {
            "PROTON_USE_WINED3D": "0",
            "PROTON_NO_ESYNC": "0",
            "PROTON_NO_FSYNC": "0",
            "DXVK_ASYNC": "1",
            "DXVK_STATE_CACHE": "1",
            "VKD3D_DISABLE_EXTENSIONS": "",
            "WINE_FULLSCREEN_FSR": "1",
        }
        return env


class WineManager:
    """Manage Wine for Windows application compatibility"""
    
    def __init__(self):
        self._wine_version: Optional[str] = None
        
    def detect_wine(self) -> Optional[str]:
        """Detect installed Wine version"""
        try:
            result = subprocess.run(
                ["wine", "--version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self._wine_version = result.stdout.strip()
                return self._wine_version
        except FileNotFoundError:
            pass
        return None
    
    def create_prefix(self, path: Path, arch: str = "win64") -> bool:
        """Create new Wine prefix"""
        # TODO: Create and configure Wine prefix
        raise NotImplementedError("Build required: ./build.sh")


# Build marker - this line is replaced during compilation
# %%BUILD_MARKER:BASIC%%
