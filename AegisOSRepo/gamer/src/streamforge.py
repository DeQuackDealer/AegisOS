#!/usr/bin/env python3
"""
Aegis OS StreamForge Capture Stack
Low-latency game capture and streaming system

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh

PREMIUM FEATURE - Requires Gamer Edition license
"""

import os
import sys
import subprocess
import threading
import queue
import time
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum


class CaptureMethod(Enum):
    KMSGRAB = "kmsgrab"     # Kernel mode capture (DRM)
    NVFBC = "nvfbc"          # NVIDIA FrameBuffer Capture
    VAAPI = "vaapi"          # VA-API (AMD/Intel)
    PIPEWIRE = "pipewire"    # PipeWire screen capture


class Encoder(Enum):
    NVENC = "nvenc"          # NVIDIA hardware encoder
    AMF = "amf"              # AMD AMF encoder
    QSV = "qsv"              # Intel Quick Sync
    X264 = "x264"            # Software fallback


class StreamPlatform(Enum):
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    CUSTOM = "custom"


@dataclass
class CaptureConfig:
    method: CaptureMethod
    width: int
    height: int
    fps: int
    encoder: Encoder
    bitrate_kbps: int
    preset: str  # quality/balanced/performance
    gpu_index: int = 0


@dataclass
class StreamConfig:
    platform: StreamPlatform
    rtmp_url: str
    stream_key: str
    audio_source: str = "default"
    audio_bitrate: int = 160


@dataclass
class CaptureStats:
    fps: float
    encode_time_ms: float
    capture_time_ms: float
    total_latency_ms: float
    bitrate_kbps: int
    dropped_frames: int


class StreamForge:
    """
    StreamForge Capture Stack - Ultra-low-latency game capture.
    
    Features:
    - Kernel-mode capture (kmsgrab/NVFBC)
    - 8ms encode latency
    - Hardware encoding (NVENC/AMF/QSV)
    - Instant Replay (save last 30s-5min)
    - Auto game detection
    """
    
    TARGET_LATENCY_MS = 8.0
    INSTANT_REPLAY_MAX_SECONDS = 300  # 5 minutes
    
    def __init__(self):
        self._capture_config: Optional[CaptureConfig] = None
        self._stream_config: Optional[StreamConfig] = None
        self._capturing: bool = False
        self._streaming: bool = False
        self._instant_replay_buffer: queue.Queue = queue.Queue()
        self._stats: Optional[CaptureStats] = None
        self._ffmpeg_process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        
    def detect_best_capture_method(self) -> CaptureMethod:
        """Auto-detect best capture method for system"""
        # Check NVIDIA first
        if self._has_nvidia():
            return CaptureMethod.NVFBC
            
        # Check for DRM/KMS support
        if self._has_kmsgrab():
            return CaptureMethod.KMSGRAB
            
        # Fall back to PipeWire
        return CaptureMethod.PIPEWIRE
    
    def _has_nvidia(self) -> bool:
        """Check for NVIDIA GPU with NVFBC support"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _has_kmsgrab(self) -> bool:
        """Check for kmsgrab support"""
        return Path("/dev/dri/card0").exists()
    
    def detect_best_encoder(self) -> Encoder:
        """Auto-detect best hardware encoder"""
        # NVIDIA
        if self._has_nvidia():
            return Encoder.NVENC
            
        # AMD
        if self._check_vaapi_encoder("h264_vaapi"):
            return Encoder.AMF
            
        # Intel
        if self._check_vaapi_encoder("h264_qsv"):
            return Encoder.QSV
            
        return Encoder.X264
    
    def _check_vaapi_encoder(self, encoder: str) -> bool:
        """Check if VA-API encoder is available"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True, text=True
            )
            return encoder in result.stdout
        except Exception:
            return False
    
    def configure_capture(
        self,
        width: int = 1920,
        height: int = 1080,
        fps: int = 60,
        bitrate_kbps: int = 6000,
        preset: str = "balanced"
    ) -> CaptureConfig:
        """Configure capture settings"""
        self._capture_config = CaptureConfig(
            method=self.detect_best_capture_method(),
            width=width,
            height=height,
            fps=fps,
            encoder=self.detect_best_encoder(),
            bitrate_kbps=bitrate_kbps,
            preset=preset
        )
        return self._capture_config
    
    def configure_stream(
        self,
        platform: StreamPlatform,
        stream_key: str,
        rtmp_url: Optional[str] = None
    ) -> StreamConfig:
        """Configure streaming settings"""
        if rtmp_url is None:
            rtmp_url = self._get_rtmp_url(platform)
            
        self._stream_config = StreamConfig(
            platform=platform,
            rtmp_url=rtmp_url,
            stream_key=stream_key
        )
        return self._stream_config
    
    def _get_rtmp_url(self, platform: StreamPlatform) -> str:
        """Get RTMP ingest URL for platform"""
        urls = {
            StreamPlatform.TWITCH: "rtmp://live.twitch.tv/app",
            StreamPlatform.YOUTUBE: "rtmp://a.rtmp.youtube.com/live2",
        }
        return urls.get(platform, "")
    
    def start_capture(self) -> bool:
        """Start screen capture"""
        # TODO: Build FFmpeg command and start capture
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_capture(self) -> bool:
        """Stop screen capture"""
        with self._lock:
            if self._ffmpeg_process:
                self._ffmpeg_process.terminate()
                self._ffmpeg_process = None
            self._capturing = False
        return True
    
    def start_stream(self) -> bool:
        """Start streaming to platform"""
        # TODO: Start RTMP stream
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_stream(self) -> bool:
        """Stop streaming"""
        with self._lock:
            self._streaming = False
        return True
    
    def enable_instant_replay(self, duration_seconds: int = 30) -> bool:
        """Enable instant replay buffer"""
        if duration_seconds > self.INSTANT_REPLAY_MAX_SECONDS:
            duration_seconds = self.INSTANT_REPLAY_MAX_SECONDS
            
        # TODO: Configure ring buffer for instant replay
        raise NotImplementedError("Build required: ./build.sh")
    
    def save_instant_replay(self, output_path: Path) -> bool:
        """Save instant replay buffer to file"""
        # TODO: Dump buffer to file
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_stats(self) -> Optional[CaptureStats]:
        """Get capture statistics"""
        return self._stats
    
    def _build_ffmpeg_command(self) -> List[str]:
        """Build FFmpeg command for capture"""
        if not self._capture_config:
            return []
            
        cfg = self._capture_config
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning"]
        
        # Input based on capture method
        if cfg.method == CaptureMethod.KMSGRAB:
            cmd.extend([
                "-device", "/dev/dri/card0",
                "-f", "kmsgrab",
                "-framerate", str(cfg.fps),
                "-i", "-"
            ])
        elif cfg.method == CaptureMethod.NVFBC:
            cmd.extend([
                "-f", "x11grab",
                "-framerate", str(cfg.fps),
                "-video_size", f"{cfg.width}x{cfg.height}",
                "-i", ":0"
            ])
            
        # Encoder settings
        if cfg.encoder == Encoder.NVENC:
            cmd.extend([
                "-c:v", "h264_nvenc",
                "-preset", "p4" if cfg.preset == "balanced" else "p7",
                "-tune", "ll",  # Low latency
                "-rc", "cbr",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
        elif cfg.encoder == Encoder.AMF:
            cmd.extend([
                "-c:v", "h264_amf",
                "-quality", "balanced",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
            
        return cmd


class InstantReplayBuffer:
    """Ring buffer for instant replay functionality"""
    
    def __init__(self, max_seconds: int, fps: int):
        self._max_frames = max_seconds * fps
        self._buffer: List[bytes] = []
        self._lock = threading.Lock()
        
    def add_frame(self, frame: bytes) -> None:
        """Add frame to ring buffer"""
        with self._lock:
            self._buffer.append(frame)
            if len(self._buffer) > self._max_frames:
                self._buffer.pop(0)
                
    def get_frames(self, last_n: Optional[int] = None) -> List[bytes]:
        """Get frames from buffer"""
        with self._lock:
            if last_n:
                return self._buffer[-last_n:]
            return list(self._buffer)
            
    def clear(self) -> None:
        """Clear buffer"""
        with self._lock:
            self._buffer.clear()


# Build marker
# %%BUILD_MARKER:STREAMFORGE%%
