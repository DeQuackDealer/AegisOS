#!/usr/bin/env python3
"""
Aegis OS Proton Setup
Proton/Wine configuration and management

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh
"""

import os
import json
import shutil
import tarfile
import urllib.request
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class ProtonVersion:
    name: str
    version: str
    path: Path
    is_ge: bool  # Proton-GE (community version)
    is_default: bool


class ProtonSetup:
    """
    Proton/Wine setup and configuration.
    Handles DXVK, VKD3D-Proton, and environment variables.
    """
    
    STEAM_COMPAT_PATH = Path.home() / ".steam/steam/compatibilitytools.d"
    PROTON_GE_API = "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest"
    
    DEFAULT_ENV = {
        # Proton settings
        "PROTON_USE_WINED3D": "0",
        "PROTON_NO_ESYNC": "0",
        "PROTON_NO_FSYNC": "0",
        "PROTON_ENABLE_NVAPI": "1",
        "PROTON_HIDE_NVIDIA_GPU": "0",
        
        # DXVK settings
        "DXVK_ASYNC": "1",
        "DXVK_STATE_CACHE": "1",
        "DXVK_STATE_CACHE_PATH": "",  # Set per-game
        "DXVK_LOG_LEVEL": "none",
        
        # VKD3D settings
        "VKD3D_SHADER_CACHE_PATH": "",  # Set per-game
        "VKD3D_DEBUG": "none",
        
        # FSR (AMD FidelityFX Super Resolution)
        "WINE_FULLSCREEN_FSR": "1",
        "WINE_FULLSCREEN_FSR_STRENGTH": "2",
        
        # Performance
        "RADV_PERFTEST": "gpl",
        "mesa_glthread": "true",
    }
    
    def __init__(self):
        self._installed_versions: List[ProtonVersion] = []
        self._default_version: Optional[ProtonVersion] = None
        
    def scan_installed_versions(self) -> List[ProtonVersion]:
        """Scan for installed Proton versions"""
        versions = []
        
        # Steam's built-in Proton versions
        steam_proton = Path.home() / ".steam/steam/steamapps/common"
        if steam_proton.exists():
            for path in steam_proton.iterdir():
                if path.name.startswith("Proton"):
                    versions.append(ProtonVersion(
                        name=path.name,
                        version=self._parse_version(path.name),
                        path=path,
                        is_ge=False,
                        is_default=False
                    ))
                    
        # Custom Proton versions (including Proton-GE)
        if self.STEAM_COMPAT_PATH.exists():
            for path in self.STEAM_COMPAT_PATH.iterdir():
                if path.is_dir():
                    is_ge = "GE" in path.name.upper()
                    versions.append(ProtonVersion(
                        name=path.name,
                        version=self._parse_version(path.name),
                        path=path,
                        is_ge=is_ge,
                        is_default=False
                    ))
                    
        self._installed_versions = versions
        return versions
    
    def _parse_version(self, name: str) -> str:
        """Extract version number from Proton directory name"""
        # Examples: "Proton 8.0", "GE-Proton8-25", "Proton - Experimental"
        import re
        match = re.search(r"(\d+[\.\-]\d+(?:[\.\-]\d+)?)", name)
        if match:
            return match.group(1)
        if "Experimental" in name:
            return "experimental"
        return "unknown"
    
    def download_proton_ge(self, version: str = "latest") -> Optional[Path]:
        """Download Proton-GE from GitHub"""
        # TODO: Implement download logic
        # This requires network access and is stubbed for raw source
        raise NotImplementedError("Build required: ./build.sh")
    
    def install_proton_ge(self, archive_path: Path) -> bool:
        """Install Proton-GE from downloaded archive"""
        # TODO: Extract and install
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_env_for_game(self, game_id: str, custom_settings: Optional[Dict] = None) -> Dict[str, str]:
        """Get environment variables for specific game"""
        env = self.DEFAULT_ENV.copy()
        
        # Set game-specific cache paths
        cache_base = Path.home() / ".cache/aegis/games" / game_id
        cache_base.mkdir(parents=True, exist_ok=True)
        
        env["DXVK_STATE_CACHE_PATH"] = str(cache_base / "dxvk")
        env["VKD3D_SHADER_CACHE_PATH"] = str(cache_base / "vkd3d")
        
        # Apply custom settings
        if custom_settings:
            env.update(custom_settings)
            
        return env
    
    def configure_dxvk(self, prefix_path: Path, version: str = "latest") -> bool:
        """Configure DXVK for DirectX 9/10/11 translation"""
        # TODO: Download and install DXVK DLLs
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_vkd3d(self, prefix_path: Path, version: str = "latest") -> bool:
        """Configure VKD3D-Proton for DirectX 12"""
        # TODO: Download and install VKD3D-Proton
        raise NotImplementedError("Build required: ./build.sh")
    
    def create_game_prefix(self, game_id: str, arch: str = "win64") -> Path:
        """Create isolated Wine prefix for game"""
        prefix_path = Path.home() / ".local/share/aegis/prefixes" / game_id
        prefix_path.mkdir(parents=True, exist_ok=True)
        
        # TODO: Initialize Wine prefix
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_recommended_settings(self, game_name: str) -> Dict[str, Any]:
        """Get recommended Proton settings for specific game"""
        # TODO: Load from game database
        return {
            "proton_version": "latest-ge",
            "enable_esync": True,
            "enable_fsync": True,
            "enable_fsr": True,
            "custom_env": {}
        }


class DXVKManager:
    """DXVK shader cache and configuration"""
    
    DXVK_RELEASES = "https://api.github.com/repos/doitsujin/dxvk/releases/latest"
    
    def __init__(self):
        self._version: Optional[str] = None
        self._cache_path = Path.home() / ".cache/aegis/dxvk"
        
    def get_cached_shaders(self, game_id: str) -> int:
        """Get number of cached shaders for game"""
        cache_file = self._cache_path / game_id / "dxvk-state-cache"
        if cache_file.exists():
            # Count entries (rough estimate)
            return cache_file.stat().st_size // 1024  # Approximate
        return 0
    
    def clear_shader_cache(self, game_id: Optional[str] = None) -> bool:
        """Clear shader cache for game or all games"""
        try:
            if game_id:
                cache = self._cache_path / game_id
                if cache.exists():
                    shutil.rmtree(cache)
            else:
                if self._cache_path.exists():
                    shutil.rmtree(self._cache_path)
            return True
        except Exception:
            return False


# Build marker
# %%BUILD_MARKER:PROTON_SETUP%%
