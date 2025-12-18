#!/usr/bin/env python3
"""
Aegis OS Thermal Guard
Smart temperature monitoring and fan control

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh

PREMIUM FEATURE - Requires Gamer Edition license
"""

import subprocess
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class ThermalStats:
    cpu_temp_c: float
    gpu_temp_c: float
    fan_speed_percent: int
    throttling: bool


class ThermalGuard:
    """
    Thermal Guard - Temperature monitoring and fan control.
    
    Features:
    - Real-time temperature monitoring
    - Automatic fan curve adjustment
    - Thermal throttling prevention
    - Gaming thermal profiles
    """
    
    CPU_TEMP_WARNING = 85
    GPU_TEMP_WARNING = 83
    
    def __init__(self):
        self._enabled: bool = False
        
    def get_stats(self) -> Optional[ThermalStats]:
        """Get current thermal statistics"""
        cpu_temp = self._get_cpu_temp()
        gpu_temp = self._get_gpu_temp()
        
        return ThermalStats(
            cpu_temp_c=cpu_temp,
            gpu_temp_c=gpu_temp,
            fan_speed_percent=self._get_fan_speed(),
            throttling=cpu_temp > self.CPU_TEMP_WARNING or gpu_temp > self.GPU_TEMP_WARNING
        )
    
    def _get_cpu_temp(self) -> float:
        """Get CPU temperature"""
        try:
            # Try hwmon
            for hwmon in Path("/sys/class/hwmon").iterdir():
                name_file = hwmon / "name"
                if name_file.exists() and "coretemp" in name_file.read_text():
                    temp_file = hwmon / "temp1_input"
                    if temp_file.exists():
                        return int(temp_file.read_text().strip()) / 1000
        except Exception:
            pass
        return 0.0
    
    def _get_gpu_temp(self) -> float:
        """Get GPU temperature"""
        # Try NVIDIA
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass
        return 0.0
    
    def _get_fan_speed(self) -> int:
        """Get fan speed percentage"""
        return 50  # Placeholder
    
    def apply_gaming_profile(self) -> bool:
        """Apply aggressive cooling profile"""
        # TODO: Configure fan curves
        raise NotImplementedError("Build required: ./build.sh")


# Build marker
# %%BUILD_MARKER:THERMAL_GUARD%%
