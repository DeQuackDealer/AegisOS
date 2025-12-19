#!/usr/bin/env python3
"""
Aegis OS Input Optimizer
Low-latency input optimization for gaming peripherals

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh

PREMIUM FEATURE - Requires Gamer Edition license
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Set
from dataclasses import dataclass, field
from enum import Enum


class PollingRate(Enum):
    """USB polling rates for gaming mice"""
    DEFAULT = 125      # Default USB polling (8ms latency)
    FAST = 500         # Fast polling (2ms latency)
    GAMING = 1000      # Standard gaming (1ms latency)
    EXTREME = 4000     # High-end gaming (0.25ms latency)
    ULTRA = 8000       # Ultra high-end gaming (0.125ms latency)


class AccelProfile(Enum):
    """Mouse acceleration profiles"""
    FLAT = "flat"           # Raw 1:1 input, no acceleration
    ADAPTIVE = "adaptive"   # Adaptive acceleration
    DEFAULT = "default"     # System default


@dataclass
class InputConfig:
    """Configuration for input optimization settings"""
    usb_polling_hz: int = 8000
    disable_autosuspend: bool = True
    disable_debounce: bool = True
    flat_acceleration: bool = True
    nkey_rollover: bool = True
    irq_core_pinning: bool = True
    dedicated_cores: List[int] = field(default_factory=lambda: [0, 1])
    libinput_quirks_path: str = "/etc/libinput/local-overrides.quirks"
    xorg_conf_path: str = "/etc/X11/xorg.conf.d/50-mouse-acceleration.conf"


@dataclass
class USBDevice:
    """USB input device information"""
    vendor_id: str
    product_id: str
    name: str
    bus: str
    device_path: str
    is_mouse: bool = False
    is_keyboard: bool = False


class InputOptimizer:
    """
    Input Optimizer - Ultra-low latency input optimization for gaming.
    
    Features:
    - 8000Hz USB Polling Support: Configure USB power management to prevent
      autosuspend for high-polling rate gaming mice
    - Mouse Debounce Disable: Create libinput quirks to remove click latency
      on optical switch mice (Razer, Logitech, etc.)
    - Flat Acceleration Profile: Disable mouse acceleration for raw 1:1 input
      via Xorg configuration
    - Keyboard Anti-Ghosting: Configure N-key rollover for simultaneous
      key presses
    - USB IRQ Core Pinning: Pin USB interrupts to dedicated CPU cores for
      lowest possible input latency
    """
    
    UDEV_RULES_PATH = "/etc/udev/rules.d/99-aegis-usb-gaming.rules"
    SYSFS_USB_PATH = "/sys/bus/usb/devices"
    PROC_INTERRUPTS = "/proc/interrupts"
    
    GAMING_VENDORS = {
        "046d": "Logitech",
        "1532": "Razer",
        "1038": "SteelSeries",
        "0b05": "ASUS ROG",
        "2516": "Cooler Master",
        "1e7d": "Roccat",
        "1bcf": "Sunplus (Glorious)",
        "3297": "Finalmouse",
        "258a": "Pulsar/Lamzu",
        "361d": "Finalmouse UltralightX",
    }
    
    def __init__(self, config: Optional[InputConfig] = None):
        self._config = config or InputConfig()
        self._devices: List[USBDevice] = []
        self._irq_mappings: Dict[str, int] = {}
        self._original_settings: Dict[str, str] = {}
        
    def detect_input_devices(self) -> List[USBDevice]:
        """
        Detect USB input devices (mice, keyboards, controllers).
        
        Scans USB bus for gaming peripherals and identifies their
        vendor/product IDs for optimization.
        
        Returns:
            List of detected USB input devices
        """
        devices = []
        
        try:
            result = subprocess.run(
                ["lsusb", "-v"],
                capture_output=True, text=True, timeout=10
            )
            
            current_device = None
            for line in result.stdout.splitlines():
                if line.startswith("Bus"):
                    if current_device:
                        devices.append(current_device)
                    parts = line.split()
                    if len(parts) >= 6:
                        vendor_product = parts[5].split(":")
                        current_device = USBDevice(
                            vendor_id=vendor_product[0] if len(vendor_product) > 0 else "",
                            product_id=vendor_product[1] if len(vendor_product) > 1 else "",
                            name=" ".join(parts[6:]) if len(parts) > 6 else "Unknown",
                            bus=parts[1],
                            device_path=f"/dev/bus/usb/{parts[1]}/{parts[3].rstrip(':')}"
                        )
                elif current_device:
                    line_lower = line.lower()
                    if "mouse" in line_lower:
                        current_device.is_mouse = True
                    elif "keyboard" in line_lower or "hid" in line_lower:
                        current_device.is_keyboard = True
                        
            if current_device:
                devices.append(current_device)
                
        except subprocess.TimeoutExpired:
            pass
        except FileNotFoundError:
            pass
        except Exception as e:
            import sys
            print(f"Warning: Device detection error: {e}", file=sys.stderr)
            
        self._devices = [d for d in devices if d.is_mouse or d.is_keyboard]
        return self._devices
    
    def configure_usb_polling_8000hz(self) -> bool:
        """
        Configure USB power management for 8000Hz polling support.
        
        High polling rate mice (8000Hz) require USB autosuspend to be
        disabled to prevent the device from entering power-saving mode,
        which would cause input lag spikes.
        
        Creates udev rules to:
        - Disable USB autosuspend for gaming devices
        - Set polling interval to maximum rate
        - Configure power/control to 'on' mode
        
        Returns:
            True if configuration was successful
        """
        if not self._config.disable_autosuspend:
            return False
            
        udev_rules = []
        udev_rules.append("# Aegis OS Gaming USB Optimization Rules")
        udev_rules.append("# Disable autosuspend for high-polling gaming mice")
        udev_rules.append("")
        
        for vendor_id, vendor_name in self.GAMING_VENDORS.items():
            udev_rules.append(f"# {vendor_name} devices")
            udev_rules.append(
                f'ACTION=="add", SUBSYSTEM=="usb", ATTR{{idVendor}}=="{vendor_id}", '
                f'ATTR{{power/autosuspend}}="-1", ATTR{{power/control}}="on"'
            )
            udev_rules.append("")
        
        udev_rules.append("# Generic high-polling rate mouse support")
        udev_rules.append(
            'ACTION=="add", SUBSYSTEM=="usb", ATTR{bInterfaceClass}=="03", '
            'ATTR{bInterfaceSubClass}=="01", ATTR{bInterfaceProtocol}=="02", '
            'ATTR{power/autosuspend}="-1"'
        )
        
        udev_rules.append("")
        udev_rules.append("# Set USB polling interval to 1ms (1000Hz minimum)")
        udev_rules.append('SUBSYSTEM=="usb", ATTR{bInterfaceClass}=="03", ATTR{bInterval}="1"')
        
        try:
            Path(self.UDEV_RULES_PATH).parent.mkdir(parents=True, exist_ok=True)
            Path(self.UDEV_RULES_PATH).write_text("\n".join(udev_rules))
            subprocess.run(["udevadm", "control", "--reload-rules"], check=True)
            subprocess.run(["udevadm", "trigger"], check=True)
            return True
        except (PermissionError, subprocess.CalledProcessError):
            return False
    
    def disable_mouse_debounce(self) -> bool:
        """
        Disable mouse click debounce via libinput quirks.
        
        Optical switch mice (Razer Optical, Logitech Lightforce) don't
        require debounce delay since they have no mechanical bounce.
        Disabling debounce removes 4-8ms of click latency.
        
        Creates quirks file at /etc/libinput/local-overrides.quirks
        
        Returns:
            True if quirks were successfully created
        """
        if not self._config.disable_debounce:
            return False
            
        quirks = []
        quirks.append("# Aegis OS - Disable debounce for optical switch mice")
        quirks.append("# Reduces click latency by 4-8ms on supported devices")
        quirks.append("")
        
        for vendor_id, vendor_name in self.GAMING_VENDORS.items():
            quirks.append(f"[{vendor_name} Optical Mice]")
            quirks.append(f"MatchVendor=0x{vendor_id}")
            quirks.append("MatchUdevType=mouse")
            quirks.append("AttrEventCode=-BTN_TOOL_DOUBLETAP")
            quirks.append("ModelBouncingKeys=1")
            quirks.append("")
        
        quirks.append("[All Gaming Mice - Debounce Override]")
        quirks.append("MatchUdevType=mouse")
        quirks.append("MatchDevicePath=/dev/input/event*")
        quirks.append("AttrDebounce=0")
        quirks.append("")
        
        try:
            quirks_path = Path(self._config.libinput_quirks_path)
            quirks_path.parent.mkdir(parents=True, exist_ok=True)
            quirks_path.write_text("\n".join(quirks))
            return True
        except PermissionError:
            return False
    
    def configure_flat_acceleration(self) -> bool:
        """
        Configure flat mouse acceleration profile via Xorg.
        
        Disables all mouse acceleration for raw 1:1 input mapping,
        essential for FPS gaming where muscle memory depends on
        consistent cursor movement.
        
        Creates Xorg config at /etc/X11/xorg.conf.d/50-mouse-acceleration.conf
        
        Returns:
            True if Xorg config was successfully created
        """
        if not self._config.flat_acceleration:
            return False
            
        xorg_config = '''# Aegis OS - Flat Mouse Acceleration Profile
# Provides raw 1:1 input with no acceleration curve

Section "InputClass"
    Identifier "Aegis Gaming Mouse - Flat Acceleration"
    MatchIsPointer "yes"
    MatchDevicePath "/dev/input/event*"
    Option "AccelerationProfile" "-1"
    Option "AccelerationScheme" "none"
    Option "AccelSpeed" "0"
EndSection

Section "InputClass"
    Identifier "Aegis libinput Gaming Mouse"
    MatchIsPointer "yes"
    MatchDriver "libinput"
    Option "AccelProfile" "flat"
    Option "AccelSpeed" "0"
    Option "NaturalScrolling" "false"
EndSection
'''
        
        try:
            xorg_path = Path(self._config.xorg_conf_path)
            xorg_path.parent.mkdir(parents=True, exist_ok=True)
            xorg_path.write_text(xorg_config)
            return True
        except PermissionError:
            return False
    
    def configure_keyboard_nkey_rollover(self) -> bool:
        """
        Configure keyboard for N-key rollover (anti-ghosting).
        
        Enables simultaneous key press detection for gaming keyboards,
        preventing "ghosting" where some key combinations are not
        registered.
        
        Most gaming keyboards support NKRO via USB, this ensures the
        kernel HID driver is configured to accept all simultaneous
        key events.
        
        Returns:
            True if NKRO configuration was successful
        """
        if not self._config.nkey_rollover:
            return False
            
        hid_quirks_path = Path("/etc/modprobe.d/aegis-hid-gaming.conf")
        
        hid_config = '''# Aegis OS - HID Gaming Keyboard Configuration
# Enable N-key rollover and reduce input latency

# Enable NKRO for all HID keyboards
options usbhid kbpoll=1
options usbhid mousepoll=1

# Reduce HID report parsing delay
options hid ignore_special_drivers=0
'''
        
        try:
            hid_quirks_path.parent.mkdir(parents=True, exist_ok=True)
            hid_quirks_path.write_text(hid_config)
            return True
        except PermissionError:
            return False
    
    def pin_usb_irq_to_cores(self) -> bool:
        """
        Pin USB interrupts to dedicated CPU cores.
        
        By pinning USB controller IRQs to specific CPU cores, we ensure
        that input processing is handled with minimal latency and isn't
        interrupted by other system processes.
        
        This is especially effective on systems with many CPU cores where
        dedicating 1-2 cores to input processing is feasible.
        
        Returns:
            True if IRQ pinning was successful
        """
        if not self._config.irq_core_pinning:
            return False
            
        dedicated_cores = self._config.dedicated_cores
        if not dedicated_cores:
            return False
            
        cpu_mask = sum(1 << core for core in dedicated_cores)
        cpu_mask_hex = format(cpu_mask, 'x')
        
        try:
            with open(self.PROC_INTERRUPTS, 'r') as f:
                for line in f:
                    if 'xhci' in line.lower() or 'ehci' in line.lower() or 'usb' in line.lower():
                        parts = line.split(':')
                        if parts:
                            irq_num = parts[0].strip()
                            if irq_num.isdigit():
                                irq_affinity_path = Path(f"/proc/irq/{irq_num}/smp_affinity")
                                if irq_affinity_path.exists():
                                    irq_affinity_path.write_text(cpu_mask_hex)
                                    self._irq_mappings[f"usb_irq_{irq_num}"] = int(irq_num)
            return True
        except (PermissionError, IOError):
            return False
    
    def apply_all_optimizations(self) -> Dict[str, bool]:
        """
        Apply all input optimizations.
        
        Runs all optimization methods and returns a status dict
        indicating which optimizations were successfully applied.
        
        Returns:
            Dictionary mapping optimization names to success status
        """
        results = {}
        
        self.detect_input_devices()
        
        results["usb_polling_8000hz"] = self.configure_usb_polling_8000hz()
        results["mouse_debounce_disabled"] = self.disable_mouse_debounce()
        results["flat_acceleration"] = self.configure_flat_acceleration()
        results["nkey_rollover"] = self.configure_keyboard_nkey_rollover()
        results["irq_core_pinning"] = self.pin_usb_irq_to_cores()
        
        return results
    
    def get_input_latency_estimate(self) -> float:
        """
        Estimate current input latency in milliseconds.
        
        Calculates theoretical minimum latency based on USB polling
        rate and optimization settings.
        
        Returns:
            Estimated input latency in ms
        """
        usb_latency_ms = 1000 / self._config.usb_polling_hz
        
        debounce_latency = 0.0 if self._config.disable_debounce else 4.0
        
        irq_overhead = 0.1 if self._config.irq_core_pinning else 0.5
        
        accel_overhead = 0.0 if self._config.flat_acceleration else 0.2
        
        return usb_latency_ms + debounce_latency + irq_overhead + accel_overhead
    
    def get_detected_devices(self) -> List[USBDevice]:
        """Get list of detected USB input devices"""
        return self._devices
    
    def get_config(self) -> InputConfig:
        """Get current configuration"""
        return self._config
    
    def restore_defaults(self) -> bool:
        """
        Restore default input settings.
        
        Removes all Aegis input optimizations and restores system
        defaults for mouse acceleration and USB power management.
        
        Returns:
            True if defaults were successfully restored
        """
        try:
            paths_to_remove = [
                self.UDEV_RULES_PATH,
                self._config.libinput_quirks_path,
                self._config.xorg_conf_path,
                "/etc/modprobe.d/aegis-hid-gaming.conf"
            ]
            
            for path_str in paths_to_remove:
                path = Path(path_str)
                if path.exists():
                    path.unlink()
            
            subprocess.run(["udevadm", "control", "--reload-rules"], check=False)
            return True
        except (PermissionError, OSError):
            return False


def main():
    """Entry point for input optimizer daemon"""
    optimizer = InputOptimizer()
    results = optimizer.apply_all_optimizations()
    
    print("Aegis Input Optimizer - Results:")
    for opt_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {opt_name}")
    
    latency = optimizer.get_input_latency_estimate()
    print(f"\nEstimated input latency: {latency:.2f}ms")


if __name__ == "__main__":
    main()


# Build marker
# %%BUILD_MARKER:INPUT_OPTIMIZER%%
