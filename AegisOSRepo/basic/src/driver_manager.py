#!/usr/bin/env python3
"""
Aegis OS Driver Manager
GPU driver detection and installation

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class GPUVendor(Enum):
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    UNKNOWN = "unknown"


class DriverStatus(Enum):
    INSTALLED = "installed"
    NOT_INSTALLED = "not_installed"
    OUTDATED = "outdated"
    INCOMPATIBLE = "incompatible"


@dataclass
class GPUInfo:
    vendor: GPUVendor
    model: str
    pci_id: str
    driver_loaded: Optional[str]
    driver_status: DriverStatus
    vram_mb: Optional[int]
    supports_vulkan: bool


class DriverManager:
    """
    GPU driver detection and management.
    Supports NVIDIA, AMD, and Intel GPUs.
    """
    
    NVIDIA_PACKAGES = [
        "nvidia-dkms",
        "nvidia-utils",
        "lib32-nvidia-utils",
        "nvidia-settings",
        "cuda",  # Optional
        "cudnn",  # Optional
    ]
    
    AMD_PACKAGES = [
        "mesa",
        "lib32-mesa",
        "vulkan-radeon",
        "lib32-vulkan-radeon",
        "libva-mesa-driver",
        "mesa-vdpau",
    ]
    
    INTEL_PACKAGES = [
        "mesa",
        "lib32-mesa",
        "vulkan-intel",
        "lib32-vulkan-intel",
        "intel-media-driver",
    ]
    
    def __init__(self):
        self._detected_gpus: List[GPUInfo] = []
        self._primary_gpu: Optional[GPUInfo] = None
        
    def detect_gpus(self) -> List[GPUInfo]:
        """Detect all installed GPUs"""
        gpus = []
        
        try:
            # Use lspci to detect GPUs
            result = subprocess.run(
                ["lspci", "-nn", "-d", "::0300"],  # VGA controllers
                capture_output=True, text=True
            )
            
            for line in result.stdout.splitlines():
                gpu = self._parse_gpu_line(line)
                if gpu:
                    gpus.append(gpu)
                    
            # Also check for 3D controllers (some NVIDIA cards)
            result = subprocess.run(
                ["lspci", "-nn", "-d", "::0302"],
                capture_output=True, text=True
            )
            
            for line in result.stdout.splitlines():
                gpu = self._parse_gpu_line(line)
                if gpu:
                    gpus.append(gpu)
                    
        except FileNotFoundError:
            pass
            
        self._detected_gpus = gpus
        if gpus:
            self._primary_gpu = gpus[0]
            
        return gpus
    
    def _parse_gpu_line(self, line: str) -> Optional[GPUInfo]:
        """Parse lspci output line to GPUInfo"""
        # Format: 00:02.0 VGA compatible controller [0300]: Intel Corporation ... [8086:xxxx]
        
        vendor = GPUVendor.UNKNOWN
        model = "Unknown GPU"
        pci_id = ""
        
        # Detect vendor
        line_upper = line.upper()
        if "NVIDIA" in line_upper:
            vendor = GPUVendor.NVIDIA
        elif "AMD" in line_upper or "ATI" in line_upper or "RADEON" in line_upper:
            vendor = GPUVendor.AMD
        elif "INTEL" in line_upper:
            vendor = GPUVendor.INTEL
            
        # Extract PCI ID
        if "[" in line and "]" in line:
            try:
                pci_part = line.split("[")[-1].split("]")[0]
                if ":" in pci_part:
                    pci_id = pci_part
            except IndexError:
                pass
                
        # Extract model name
        if ":" in line:
            parts = line.split(":")
            if len(parts) >= 3:
                model = parts[2].split("[")[0].strip()
                
        # Check driver status
        driver_loaded = self._get_loaded_driver(vendor)
        driver_status = DriverStatus.INSTALLED if driver_loaded else DriverStatus.NOT_INSTALLED
        
        return GPUInfo(
            vendor=vendor,
            model=model,
            pci_id=pci_id,
            driver_loaded=driver_loaded,
            driver_status=driver_status,
            vram_mb=None,  # Detected separately
            supports_vulkan=vendor != GPUVendor.UNKNOWN
        )
    
    def _get_loaded_driver(self, vendor: GPUVendor) -> Optional[str]:
        """Check which driver is currently loaded"""
        driver_map = {
            GPUVendor.NVIDIA: ["nvidia", "nouveau"],
            GPUVendor.AMD: ["amdgpu", "radeon"],
            GPUVendor.INTEL: ["i915", "xe"],
        }
        
        for driver in driver_map.get(vendor, []):
            try:
                result = subprocess.run(
                    ["lsmod"],
                    capture_output=True, text=True
                )
                if driver in result.stdout:
                    return driver
            except Exception:
                pass
                
        return None
    
    def install_drivers(self, gpu: GPUInfo) -> bool:
        """Install appropriate drivers for GPU"""
        # TODO: Implement driver installation
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_recommended_packages(self, vendor: GPUVendor) -> List[str]:
        """Get recommended packages for vendor"""
        if vendor == GPUVendor.NVIDIA:
            return self.NVIDIA_PACKAGES
        elif vendor == GPUVendor.AMD:
            return self.AMD_PACKAGES
        elif vendor == GPUVendor.INTEL:
            return self.INTEL_PACKAGES
        return []
    
    def check_vulkan_support(self) -> Dict[str, Any]:
        """Check Vulkan support status"""
        result = {
            "vulkan_available": False,
            "vulkan_version": None,
            "devices": [],
        }
        
        try:
            vk_result = subprocess.run(
                ["vulkaninfo", "--summary"],
                capture_output=True, text=True
            )
            if vk_result.returncode == 0:
                result["vulkan_available"] = True
                # Parse version and devices
                for line in vk_result.stdout.splitlines():
                    if "Vulkan Instance Version" in line:
                        result["vulkan_version"] = line.split(":")[-1].strip()
                    elif "deviceName" in line:
                        result["devices"].append(line.split("=")[-1].strip())
        except FileNotFoundError:
            pass
            
        return result


# Build marker
# %%BUILD_MARKER:DRIVER_MANAGER%%
