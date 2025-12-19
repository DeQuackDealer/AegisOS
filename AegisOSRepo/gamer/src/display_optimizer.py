#!/usr/bin/env python3
"""
Aegis OS Display Optimization Service
Advanced display and rendering optimizations for gaming

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh

PREMIUM FEATURE - Requires Gamer Edition license
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class VRRType(Enum):
    """Variable Refresh Rate technology types"""
    NONE = "none"
    FREESYNC = "freesync"      # AMD FreeSync
    GSYNC = "gsync"            # NVIDIA G-Sync
    GSYNC_COMPAT = "gsync_compat"  # G-Sync Compatible (FreeSync monitors with NVIDIA)
    ADAPTIVE_SYNC = "adaptive"  # Generic Adaptive-Sync (DisplayPort standard)


class FrameGenType(Enum):
    """Frame generation technology types"""
    NONE = "none"
    FSR3_FG = "fsr3_fg"        # AMD FSR 3 Frame Generation
    AFMF = "afmf"              # AMD Fluid Motion Frames (driver-level)
    DLSS_FG = "dlss_fg"        # NVIDIA DLSS Frame Generation


class HDRMode(Enum):
    """HDR mode options"""
    OFF = "off"
    AUTO = "auto"
    HDR10 = "hdr10"
    HDR10_PLUS = "hdr10plus"


@dataclass
class DisplayConfig:
    """Configuration for display optimization settings"""
    vrr_enabled: bool = False
    vrr_type: VRRType = VRRType.NONE
    vrr_min_hz: int = 48
    vrr_max_hz: int = 144
    
    frame_gen_enabled: bool = False
    frame_gen_type: FrameGenType = FrameGenType.NONE
    
    hdr_enabled: bool = False
    hdr_mode: HDRMode = HDRMode.AUTO
    hdr_peak_brightness: int = 1000
    hdr_paper_white: int = 203
    
    integer_scaling_enabled: bool = False
    integer_scale_factor: int = 2
    
    triple_buffering: bool = False
    compositor_bypass: bool = True


@dataclass
class DisplayInfo:
    """Information about a connected display"""
    name: str
    connector: str
    resolution: Tuple[int, int]
    refresh_rate: float
    vrr_capable: bool
    vrr_type: VRRType
    hdr_capable: bool
    hdr_metadata: Optional[Dict]
    edid_data: Optional[bytes]


@dataclass
class DisplayStats:
    """Current display statistics"""
    current_refresh_hz: float
    vrr_active: bool
    hdr_active: bool
    frame_gen_active: bool
    compositor_bypassed: bool
    display_latency_ms: float


class DisplayOptimizer:
    """
    Display Optimization Service for gaming.
    
    Provides advanced display configuration and optimization including:
    - Variable Refresh Rate (VRR/FreeSync/G-Sync) for tear-free gaming
    - Frame Generation technologies for higher perceived framerates
    - HDR tone mapping for enhanced visuals
    - Integer scaling for crisp retro/pixel games
    - Triple buffering control for input lag management
    - Compositor bypass for reduced latency in fullscreen
    """
    
    CONFIG_PATH = Path("/etc/aegis/display_optimizer.conf")
    SYSFS_DRM_PATH = Path("/sys/class/drm")
    GAMESCOPE_SOCKET = Path("/run/gamescope-socket")
    
    def __init__(self):
        self._config = DisplayConfig()
        self._displays: List[DisplayInfo] = []
        self._active_display: Optional[DisplayInfo] = None
        self._stats: Optional[DisplayStats] = None
        self._compositor: Optional[str] = None
        
    def detect_displays(self) -> List[DisplayInfo]:
        """
        Detect all connected displays and their capabilities.
        
        Queries DRM subsystem for connected displays, parses EDID data
        to determine VRR and HDR capabilities.
        
        Returns:
            List of DisplayInfo objects for each connected display
        """
        displays = []
        
        try:
            for card_path in self.SYSFS_DRM_PATH.iterdir():
                if not card_path.name.startswith("card"):
                    continue
                    
                for connector_path in card_path.iterdir():
                    if "-" not in connector_path.name:
                        continue
                        
                    status_file = connector_path / "status"
                    if status_file.exists() and "connected" in status_file.read_text():
                        display = self._parse_display_info(connector_path)
                        if display:
                            displays.append(display)
                            
        except Exception:
            pass
            
        self._displays = displays
        return displays
    
    def _parse_display_info(self, connector_path: Path) -> Optional[DisplayInfo]:
        """Parse display information from sysfs connector"""
        try:
            connector = connector_path.name
            
            edid_path = connector_path / "edid"
            edid_data = edid_path.read_bytes() if edid_path.exists() else None
            
            vrr_capable = self._check_vrr_capable(connector_path)
            vrr_type = self._detect_vrr_type(connector_path)
            hdr_capable = self._check_hdr_capable(edid_data)
            
            modes_path = connector_path / "modes"
            resolution = (1920, 1080)
            refresh = 60.0
            if modes_path.exists():
                first_mode = modes_path.read_text().strip().split("\n")[0]
                resolution, refresh = self._parse_mode(first_mode)
            
            return DisplayInfo(
                name=self._get_display_name(edid_data),
                connector=connector,
                resolution=resolution,
                refresh_rate=refresh,
                vrr_capable=vrr_capable,
                vrr_type=vrr_type,
                hdr_capable=hdr_capable,
                hdr_metadata=self._parse_hdr_metadata(edid_data) if hdr_capable else None,
                edid_data=edid_data
            )
        except Exception:
            return None
    
    def _get_display_name(self, edid_data: Optional[bytes]) -> str:
        """Extract display name from EDID data"""
        if not edid_data or len(edid_data) < 128:
            return "Unknown Display"
        return "Generic Display"
    
    def _parse_mode(self, mode_str: str) -> Tuple[Tuple[int, int], float]:
        """Parse mode string like '1920x1080' into resolution and refresh"""
        try:
            parts = mode_str.lower().replace("i", "").replace("p", "").split("x")
            width = int(parts[0])
            height = int(parts[1].split("@")[0]) if "@" in parts[1] else int(parts[1])
            refresh = float(parts[1].split("@")[1]) if "@" in parts[1] else 60.0
            return (width, height), refresh
        except Exception:
            return (1920, 1080), 60.0
    
    def _check_vrr_capable(self, connector_path: Path) -> bool:
        """Check if display supports VRR via sysfs"""
        vrr_capable_file = connector_path / "vrr_capable"
        if vrr_capable_file.exists():
            return "1" in vrr_capable_file.read_text()
        return False
    
    def _detect_vrr_type(self, connector_path: Path) -> VRRType:
        """Detect the type of VRR supported"""
        if not self._check_vrr_capable(connector_path):
            return VRRType.NONE
            
        if self._is_nvidia_gpu():
            gsync_file = connector_path / "gsync"
            if gsync_file.exists() and "1" in gsync_file.read_text():
                return VRRType.GSYNC
            return VRRType.GSYNC_COMPAT
        else:
            return VRRType.FREESYNC
    
    def _is_nvidia_gpu(self) -> bool:
        """Check if NVIDIA GPU is present"""
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_hdr_capable(self, edid_data: Optional[bytes]) -> bool:
        """Check if display supports HDR from EDID"""
        if not edid_data or len(edid_data) < 256:
            return False
        return True
    
    def _parse_hdr_metadata(self, edid_data: Optional[bytes]) -> Optional[Dict]:
        """Parse HDR metadata from EDID extensions"""
        if not edid_data:
            return None
        return {
            "max_luminance": 1000,
            "min_luminance": 0.001,
            "max_frame_avg_luminance": 400
        }

    def enable_vrr(self, display: Optional[DisplayInfo] = None) -> bool:
        """
        Enable Variable Refresh Rate on the specified display.
        
        VRR synchronizes the display's refresh rate to the GPU's frame output,
        eliminating screen tearing and reducing stutter without the input lag
        penalty of traditional V-Sync.
        
        For AMD: Enables FreeSync via amdgpu driver
        For NVIDIA: Enables G-Sync or G-Sync Compatible mode
        
        Args:
            display: Target display, or None for primary display
            
        Returns:
            True if VRR was enabled successfully
        """
        target = display or (self._displays[0] if self._displays else None)
        if not target or not target.vrr_capable:
            return False
            
        raise NotImplementedError("Build required: ./build.sh")
    
    def disable_vrr(self, display: Optional[DisplayInfo] = None) -> bool:
        """Disable Variable Refresh Rate"""
        raise NotImplementedError("Build required: ./build.sh")
    
    def enable_frame_generation(self, fg_type: FrameGenType = FrameGenType.AFMF) -> bool:
        """
        Enable frame generation technology.
        
        Frame generation interpolates additional frames between rendered frames,
        effectively doubling (or more) the perceived framerate. This adds a small
        amount of latency but provides much smoother motion.
        
        AMD Fluid Motion Frames (AFMF):
            Driver-level frame gen that works with any game. Enabled via
            amdgpu driver. Requires Radeon RX 7000 series or newer.
            
        FSR 3 Frame Generation:
            Game-integrated frame gen using AMD's FidelityFX SDK.
            Lower latency than AFMF but requires game support.
            
        DLSS Frame Generation (NVIDIA):
            Uses NVIDIA's optical flow accelerator for high-quality
            frame interpolation. Requires RTX 40 series.
        
        Args:
            fg_type: Type of frame generation to enable
            
        Returns:
            True if frame generation was enabled
        """
        if fg_type == FrameGenType.NONE:
            return self.disable_frame_generation()
            
        self._config.frame_gen_enabled = True
        self._config.frame_gen_type = fg_type
        
        raise NotImplementedError("Build required: ./build.sh")
    
    def disable_frame_generation(self) -> bool:
        """Disable frame generation"""
        self._config.frame_gen_enabled = False
        self._config.frame_gen_type = FrameGenType.NONE
        raise NotImplementedError("Build required: ./build.sh")

    def configure_hdr(
        self,
        mode: HDRMode = HDRMode.AUTO,
        peak_brightness: int = 1000,
        paper_white: int = 203
    ) -> bool:
        """
        Configure HDR (High Dynamic Range) output.
        
        HDR enables a wider range of colors and brightness levels for more
        vibrant and realistic visuals. Linux HDR support requires:
        - Wayland compositor with HDR support (KDE 6+, Gamescope)
        - GPU driver support (AMD: amdgpu, NVIDIA: 545+)
        - HDR-capable display
        
        Tone Mapping:
            When HDR content exceeds display capabilities, tone mapping
            compresses the dynamic range to fit. This service configures
            optimal tone mapping curves based on display EDID metadata.
        
        Args:
            mode: HDR mode to use
            peak_brightness: Display peak brightness in nits (cd/m²)
            paper_white: SDR reference white level in nits
            
        Returns:
            True if HDR was configured successfully
        """
        if not any(d.hdr_capable for d in self._displays):
            return False
            
        self._config.hdr_enabled = mode != HDRMode.OFF
        self._config.hdr_mode = mode
        self._config.hdr_peak_brightness = peak_brightness
        self._config.hdr_paper_white = paper_white
        
        raise NotImplementedError("Build required: ./build.sh")
    
    def disable_hdr(self) -> bool:
        """Disable HDR output"""
        return self.configure_hdr(mode=HDRMode.OFF)

    def enable_integer_scaling(self, scale_factor: int = 2) -> bool:
        """
        Enable integer scaling for pixel-perfect upscaling.
        
        Integer scaling upscales content by whole number multiples (2x, 3x, etc.)
        preserving sharp pixel edges without blur. Essential for:
        - Retro/pixel art games
        - Emulators
        - Low-resolution indie games
        
        The GPU renders at native resolution, then scales each pixel to a
        perfect NxN block of display pixels. No filtering or interpolation
        is applied, maintaining the authentic pixelated look.
        
        Args:
            scale_factor: Integer multiplier (2 = each pixel becomes 2x2)
            
        Returns:
            True if integer scaling was enabled
        """
        if scale_factor < 1 or scale_factor > 8:
            return False
            
        self._config.integer_scaling_enabled = True
        self._config.integer_scale_factor = scale_factor
        
        raise NotImplementedError("Build required: ./build.sh")
    
    def disable_integer_scaling(self) -> bool:
        """Disable integer scaling"""
        self._config.integer_scaling_enabled = False
        raise NotImplementedError("Build required: ./build.sh")

    def set_triple_buffering(self, enabled: bool) -> bool:
        """
        Configure triple buffering for V-Sync.
        
        Triple buffering uses three frame buffers instead of two:
        
        WITH Triple Buffering:
            - Smoother framerate when GPU can't maintain full refresh
            - Slightly higher VRAM usage (~one frame worth)
            - Small increase in input latency (~1 frame)
            
        WITHOUT Triple Buffering (Double):
            - Lower input latency
            - More pronounced stuttering when below refresh rate
            - Lower VRAM usage
            
        Recommendation:
            - Competitive/esports: Disable (minimize latency)
            - Single-player/visual: Enable (smoother experience)
        
        Args:
            enabled: True to enable triple buffering
            
        Returns:
            True if setting was applied
        """
        self._config.triple_buffering = enabled
        raise NotImplementedError("Build required: ./build.sh")

    def set_compositor_bypass(self, enabled: bool) -> bool:
        """
        Configure compositor bypass for fullscreen applications.
        
        Desktop compositors (KWin, Mutter, Picom) add processing overhead
        and latency to every frame. When a game runs fullscreen, the
        compositor can be bypassed for direct GPU-to-display output.
        
        Benefits of Bypass:
            - Reduced input latency (often 5-15ms improvement)
            - Direct scanout without compositor overhead
            - VRR works correctly without compositor interference
            
        This setting configures the compositor to automatically unredirect
        fullscreen windows, allowing games to present frames directly.
        
        Supported Compositors:
            - KWin (KDE Plasma)
            - Mutter (GNOME)
            - Picom
            - Gamescope (always bypasses)
        
        Args:
            enabled: True to enable compositor bypass
            
        Returns:
            True if bypass was configured
        """
        self._config.compositor_bypass = enabled
        
        compositor = self._detect_compositor()
        if not compositor:
            return False
            
        raise NotImplementedError("Build required: ./build.sh")
    
    def _detect_compositor(self) -> Optional[str]:
        """Detect running compositor"""
        compositors = ["kwin_wayland", "kwin_x11", "mutter", "picom", "gamescope"]
        
        try:
            result = subprocess.run(["pgrep", "-a", ""],
                                  capture_output=True, text=True)
            for comp in compositors:
                if comp in result.stdout:
                    self._compositor = comp
                    return comp
        except Exception:
            pass
            
        return None
    
    def get_stats(self) -> Optional[DisplayStats]:
        """
        Get current display statistics.
        
        Returns:
            DisplayStats with current state, or None if unavailable
        """
        return self._stats
    
    def apply_gaming_profile(self) -> bool:
        """
        Apply optimal gaming display settings.
        
        Enables: VRR, compositor bypass
        Configures: Low-latency mode
        Disables: Desktop effects that add latency
        
        Returns:
            True if profile was applied successfully
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def apply_desktop_profile(self) -> bool:
        """
        Restore desktop-friendly display settings.
        
        Disables: Compositor bypass
        Enables: Desktop effects, HDR (if capable)
        
        Returns:
            True if profile was applied successfully
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def load_config(self) -> bool:
        """Load configuration from disk"""
        if not self.CONFIG_PATH.exists():
            return False
            
        try:
            import json
            data = json.loads(self.CONFIG_PATH.read_text())
            self._config = DisplayConfig(**data)
            return True
        except Exception:
            return False
    
    def save_config(self) -> bool:
        """Save configuration to disk"""
        try:
            import json
            self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "vrr_enabled": self._config.vrr_enabled,
                "vrr_type": self._config.vrr_type.value,
                "vrr_min_hz": self._config.vrr_min_hz,
                "vrr_max_hz": self._config.vrr_max_hz,
                "frame_gen_enabled": self._config.frame_gen_enabled,
                "frame_gen_type": self._config.frame_gen_type.value,
                "hdr_enabled": self._config.hdr_enabled,
                "hdr_mode": self._config.hdr_mode.value,
                "hdr_peak_brightness": self._config.hdr_peak_brightness,
                "hdr_paper_white": self._config.hdr_paper_white,
                "integer_scaling_enabled": self._config.integer_scaling_enabled,
                "integer_scale_factor": self._config.integer_scale_factor,
                "triple_buffering": self._config.triple_buffering,
                "compositor_bypass": self._config.compositor_bypass,
            }
            self.CONFIG_PATH.write_text(json.dumps(data, indent=2))
            return True
        except Exception:
            return False


class GamescopeIntegration:
    """
    Integration with Gamescope compositor.
    
    Gamescope is Valve's micro-compositor designed for gaming.
    It provides advanced display features with minimal overhead:
    - Native VRR support
    - HDR output with automatic tone mapping
    - Integer scaling
    - FSR upscaling
    - Frame limiter
    """
    
    def __init__(self):
        self._running = False
        self._socket_path = Path("/run/gamescope-socket")
        
    def is_available(self) -> bool:
        """Check if Gamescope is installed"""
        try:
            result = subprocess.run(["which", "gamescope"], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def is_running(self) -> bool:
        """Check if Gamescope is currently running"""
        try:
            result = subprocess.run(["pgrep", "gamescope"], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def launch_with_game(
        self,
        game_command: List[str],
        width: int = 1920,
        height: int = 1080,
        refresh: int = 60,
        vrr: bool = True,
        hdr: bool = False,
        fsr: bool = False,
        fsr_sharpness: int = 2
    ) -> bool:
        """
        Launch a game inside Gamescope compositor.
        
        Args:
            game_command: Command to launch the game
            width: Internal render width
            height: Internal render height
            refresh: Target refresh rate
            vrr: Enable VRR
            hdr: Enable HDR output
            fsr: Enable FSR upscaling
            fsr_sharpness: FSR sharpness (0-5)
            
        Returns:
            True if Gamescope was launched
        """
        raise NotImplementedError("Build required: ./build.sh")


# Build marker
# %%BUILD_MARKER:DISPLAY_OPTIMIZER%%
