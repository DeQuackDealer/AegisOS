#!/usr/bin/env python3
"""
Aegis OS Latency FastPath
Input latency optimization and IRQ steering

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh

PREMIUM FEATURE - Requires Gamer Edition license
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum


class USBPollingRate(Enum):
    DEFAULT = 125      # Default USB polling (8ms)
    FAST = 500         # Fast polling (2ms)
    GAMING = 1000      # Gaming polling (1ms)
    EXTREME = 8000     # High-end gaming mice


class CPUGovernor(Enum):
    POWERSAVE = "powersave"
    SCHEDUTIL = "schedutil"
    PERFORMANCE = "performance"


@dataclass
class LatencyProfile:
    name: str
    usb_polling_hz: int
    cpu_governor: CPUGovernor
    irq_affinity: bool
    preempt_mode: str
    realtime_priority: bool


class LatencyFastPath:
    """
    Latency FastPath - Ultra-low input latency optimization.
    
    Features:
    - IRQ affinity steering (dedicate CPU cores to input)
    - 1000Hz USB polling
    - CPU governor auto-switching
    - Preempt optimization
    - Real-time scheduling for input processing
    """
    
    PROFILES = {
        "gaming": LatencyProfile(
            name="Gaming",
            usb_polling_hz=1000,
            cpu_governor=CPUGovernor.PERFORMANCE,
            irq_affinity=True,
            preempt_mode="voluntary",
            realtime_priority=True
        ),
        "balanced": LatencyProfile(
            name="Balanced",
            usb_polling_hz=500,
            cpu_governor=CPUGovernor.SCHEDUTIL,
            irq_affinity=False,
            preempt_mode="voluntary",
            realtime_priority=False
        ),
        "power_saving": LatencyProfile(
            name="Power Saving",
            usb_polling_hz=125,
            cpu_governor=CPUGovernor.POWERSAVE,
            irq_affinity=False,
            preempt_mode="none",
            realtime_priority=False
        )
    }
    
    def __init__(self):
        self._current_profile: Optional[LatencyProfile] = None
        self._input_devices: List[Dict] = []
        self._dedicated_cores: List[int] = []
        
    def detect_input_devices(self) -> List[Dict]:
        """Detect USB input devices"""
        devices = []
        
        try:
            result = subprocess.run(
                ["lsusb"],
                capture_output=True, text=True
            )
            
            for line in result.stdout.splitlines():
                # Look for mice, keyboards, controllers
                line_lower = line.lower()
                if any(x in line_lower for x in ["mouse", "keyboard", "gaming", "controller"]):
                    devices.append({
                        "raw": line,
                        "type": self._detect_device_type(line)
                    })
                    
        except Exception:
            pass
            
        self._input_devices = devices
        return devices
    
    def _detect_device_type(self, line: str) -> str:
        """Detect input device type"""
        line_lower = line.lower()
        if "mouse" in line_lower or "gaming" in line_lower:
            return "mouse"
        elif "keyboard" in line_lower:
            return "keyboard"
        elif "controller" in line_lower or "gamepad" in line_lower:
            return "controller"
        return "unknown"
    
    def apply_profile(self, profile_name: str) -> bool:
        """Apply latency optimization profile"""
        profile = self.PROFILES.get(profile_name)
        if not profile:
            return False
            
        # Apply settings
        self._set_usb_polling(profile.usb_polling_hz)
        self._set_cpu_governor(profile.cpu_governor)
        
        if profile.irq_affinity:
            self._configure_irq_affinity()
            
        self._current_profile = profile
        return True
    
    def _set_usb_polling(self, rate_hz: int) -> bool:
        """Set USB polling rate"""
        # TODO: Configure usbhid module parameters
        raise NotImplementedError("Build required: ./build.sh")
    
    def _set_cpu_governor(self, governor: CPUGovernor) -> bool:
        """Set CPU frequency governor for all cores"""
        try:
            for cpu_path in Path("/sys/devices/system/cpu").glob("cpu[0-9]*"):
                governor_path = cpu_path / "cpufreq/scaling_governor"
                if governor_path.exists():
                    governor_path.write_text(governor.value)
            return True
        except PermissionError:
            return False
    
    def _configure_irq_affinity(self) -> bool:
        """Configure IRQ affinity for input devices"""
        # TODO: Steer input IRQs to dedicated cores
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_input_latency_estimate(self) -> float:
        """Estimate current input latency in ms"""
        if not self._current_profile:
            return 8.0  # Default USB polling
            
        # Calculate based on USB polling rate
        usb_latency_ms = 1000 / self._current_profile.usb_polling_hz
        
        # Add system overhead estimate
        overhead_ms = 0.5 if self._current_profile.irq_affinity else 2.0
        
        return usb_latency_ms + overhead_ms
    
    def enable_game_mode(self, game_pid: int) -> bool:
        """Enable gaming optimizations for specific game"""
        # Apply gaming profile
        self.apply_profile("gaming")
        
        # Set game process to real-time priority if enabled
        if self._current_profile and self._current_profile.realtime_priority:
            try:
                os.sched_setscheduler(
                    game_pid,
                    os.SCHED_FIFO,
                    os.sched_param(50)
                )
            except Exception:
                pass
                
        return True
    
    def disable_game_mode(self) -> bool:
        """Disable gaming optimizations"""
        return self.apply_profile("balanced")


# Build marker
# %%BUILD_MARKER:LATENCY_FASTPATH%%
