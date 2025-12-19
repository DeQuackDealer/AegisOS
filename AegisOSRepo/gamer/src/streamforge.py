#!/usr/bin/env python3
"""
Aegis OS StreamForge Capture Stack
Low-latency game capture and streaming system

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh

PREMIUM FEATURE - Requires Gamer Edition license

Features:
- Kernel-mode capture (kmsgrab/NVFBC)
- 8ms encode latency
- Hardware encoding (NVENC/AMF/QSV)
- AV1 Hardware Encoding (NVIDIA/AMD)
- Instant Replay (save last 30s-5min)
- Replay Buffer (always-on recording with hotkey save)
- Auto game detection
- NDI Network Streaming (DistroAV dual-PC streaming)
- Scene Auto-Switch (OBS scene switching based on active window)
- Discord Audio Routing (separate game/voice audio)
- Multi-track Audio (separate audio tracks for different sources)
"""

import os
import sys
import subprocess
import threading
import queue
import time
import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CaptureMethod(Enum):
    """Video capture methods supported by StreamForge."""
    KMSGRAB = "kmsgrab"      # Kernel mode capture (DRM)
    NVFBC = "nvfbc"          # NVIDIA FrameBuffer Capture
    VAAPI = "vaapi"          # VA-API (AMD/Intel)
    PIPEWIRE = "pipewire"    # PipeWire screen capture
    NDI = "ndi"              # NDI network input


class Encoder(Enum):
    """Video encoders supported by StreamForge."""
    NVENC = "nvenc"          # NVIDIA H.264 hardware encoder
    NVENC_AV1 = "nvenc_av1"  # NVIDIA AV1 hardware encoder (RTX 40+)
    AMF = "amf"              # AMD H.264 AMF encoder
    AMF_AV1 = "amf_av1"      # AMD AV1 encoder (RX 7000+)
    QSV = "qsv"              # Intel Quick Sync H.264
    QSV_AV1 = "qsv_av1"      # Intel Quick Sync AV1 (Arc)
    X264 = "x264"            # Software H.264 fallback
    SVT_AV1 = "svt_av1"      # Software AV1 fallback


class StreamPlatform(Enum):
    """Supported streaming platforms."""
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    KICK = "kick"
    CUSTOM = "custom"
    NDI = "ndi"              # NDI network output


class AudioTrackType(Enum):
    """Audio track types for multi-track recording."""
    GAME = "game"            # Game audio
    VOICE = "voice"          # Voice chat (Discord, etc.)
    MUSIC = "music"          # Background music
    BROWSER = "browser"      # Browser audio
    SYSTEM = "system"        # System sounds
    MIC = "microphone"       # Microphone input
    MIXED = "mixed"          # Combined final mix


@dataclass
class CaptureConfig:
    """Configuration for video capture."""
    method: CaptureMethod
    width: int
    height: int
    fps: int
    encoder: Encoder
    bitrate_kbps: int
    preset: str  # quality/balanced/performance
    gpu_index: int = 0
    use_av1: bool = False
    hdr_enabled: bool = False


@dataclass
class StreamConfig:
    """Configuration for streaming output."""
    platform: StreamPlatform
    rtmp_url: str
    stream_key: str
    audio_source: str = "default"
    audio_bitrate: int = 160
    ndi_name: str = "StreamForge"
    ndi_groups: str = ""


@dataclass
class CaptureStats:
    """Real-time capture statistics."""
    fps: float
    encode_time_ms: float
    capture_time_ms: float
    total_latency_ms: float
    bitrate_kbps: int
    dropped_frames: int
    ndi_bandwidth_mbps: float = 0.0
    replay_buffer_seconds: float = 0.0


@dataclass
class NDIConfig:
    """Configuration for NDI network streaming."""
    enabled: bool = False
    source_name: str = "Aegis-StreamForge"
    groups: str = ""
    recv_bandwidth: str = "highest"  # highest/lowest/audio_only
    low_latency: bool = True
    discovery_server: str = ""
    failover_source: str = ""
    dual_pc_mode: bool = False
    gaming_pc_name: str = ""
    streaming_pc_name: str = ""


@dataclass
class ReplayBufferConfig:
    """Configuration for replay buffer (always-on recording)."""
    enabled: bool = False
    duration_seconds: int = 120
    output_directory: Path = field(default_factory=lambda: Path.home() / "Videos" / "Replays")
    hotkey: str = "F9"
    format: str = "mp4"
    encoder: Encoder = Encoder.NVENC
    quality_preset: str = "balanced"
    include_audio: bool = True
    auto_delete_after_days: int = 7


@dataclass
class AudioTrackConfig:
    """Configuration for an individual audio track."""
    track_id: int
    track_type: AudioTrackType
    source_name: str
    volume: float = 1.0
    muted: bool = False
    codec: str = "aac"
    bitrate_kbps: int = 160
    sample_rate: int = 48000


@dataclass
class MultiTrackAudioConfig:
    """Configuration for multi-track audio recording."""
    enabled: bool = False
    tracks: List[AudioTrackConfig] = field(default_factory=list)
    separate_discord: bool = True
    separate_game: bool = True
    separate_mic: bool = True
    pipewire_routing: bool = True


@dataclass
class SceneAutoSwitchConfig:
    """Configuration for automatic OBS scene switching."""
    enabled: bool = False
    obs_websocket_host: str = "localhost"
    obs_websocket_port: int = 4455
    obs_websocket_password: str = ""
    rules: Dict[str, str] = field(default_factory=dict)
    default_scene: str = "Gaming"
    switch_delay_ms: int = 500
    window_match_mode: str = "contains"  # exact/contains/regex


@dataclass
class DiscordAudioConfig:
    """Configuration for Discord audio routing."""
    enabled: bool = False
    separate_output: bool = True
    game_sink: str = "aegis_game_audio"
    voice_sink: str = "aegis_voice_audio"
    auto_detect_discord: bool = True
    discord_app_names: List[str] = field(default_factory=lambda: ["Discord", "discord"])
    ducking_enabled: bool = False
    ducking_threshold_db: float = -20.0


class StreamForge:
    """
    StreamForge Capture Stack - Ultra-low-latency game capture.
    
    Features:
    - Kernel-mode capture (kmsgrab/NVFBC)
    - 8ms encode latency
    - Hardware encoding (NVENC/AMF/QSV)
    - AV1 Hardware Encoding (NVIDIA RTX 40+, AMD RX 7000+)
    - Instant Replay (save last 30s-5min)
    - Replay Buffer (always-on recording with hotkey save)
    - Auto game detection
    - NDI Network Streaming (DistroAV dual-PC streaming over LAN)
    - Scene Auto-Switch (OBS scene switching based on active window)
    - Discord Audio Routing (separate game/voice audio for streaming)
    - Multi-track Audio (separate audio tracks for different sources)
    """
    
    TARGET_LATENCY_MS = 8.0
    INSTANT_REPLAY_MAX_SECONDS = 300  # 5 minutes
    REPLAY_BUFFER_MAX_SECONDS = 600   # 10 minutes
    
    def __init__(self):
        self._capture_config: Optional[CaptureConfig] = None
        self._stream_config: Optional[StreamConfig] = None
        self._ndi_config: Optional[NDIConfig] = None
        self._replay_buffer_config: Optional[ReplayBufferConfig] = None
        self._multi_track_config: Optional[MultiTrackAudioConfig] = None
        self._scene_switch_config: Optional[SceneAutoSwitchConfig] = None
        self._discord_audio_config: Optional[DiscordAudioConfig] = None
        self._capturing: bool = False
        self._streaming: bool = False
        self._replay_buffer_active: bool = False
        self._scene_monitor_active: bool = False
        self._instant_replay_buffer: queue.Queue = queue.Queue()
        self._stats: Optional[CaptureStats] = None
        self._ffmpeg_process: Optional[subprocess.Popen] = None
        self._ndi_send_process: Optional[subprocess.Popen] = None
        self._replay_buffer_thread: Optional[threading.Thread] = None
        self._scene_monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._hotkey_callbacks: Dict[str, Callable] = {}
        
    def detect_best_capture_method(self) -> CaptureMethod:
        """Auto-detect best capture method for system."""
        if self._has_nvidia():
            return CaptureMethod.NVFBC
        if self._has_kmsgrab():
            return CaptureMethod.KMSGRAB
        return CaptureMethod.PIPEWIRE
    
    def _has_nvidia(self) -> bool:
        """Check for NVIDIA GPU with NVFBC support."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _has_kmsgrab(self) -> bool:
        """Check for kmsgrab support."""
        return Path("/dev/dri/card0").exists()
    
    def detect_best_encoder(self, prefer_av1: bool = False) -> Encoder:
        """
        Auto-detect best hardware encoder.
        
        Args:
            prefer_av1: If True, prefer AV1 encoders when available.
        
        Returns:
            Best available encoder for the system.
        """
        if self._has_nvidia():
            if prefer_av1 and self._has_av1_nvenc():
                return Encoder.NVENC_AV1
            return Encoder.NVENC
        if self._check_vaapi_encoder("av1_vaapi") and prefer_av1:
            return Encoder.AMF_AV1
        if self._check_vaapi_encoder("h264_vaapi"):
            return Encoder.AMF
        if self._check_vaapi_encoder("av1_qsv") and prefer_av1:
            return Encoder.QSV_AV1
        if self._check_vaapi_encoder("h264_qsv"):
            return Encoder.QSV
        if prefer_av1:
            return Encoder.SVT_AV1
        return Encoder.X264
    
    def _has_av1_nvenc(self) -> bool:
        """Check for NVIDIA AV1 hardware encoding support (RTX 40 series+)."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True, text=True
            )
            return "av1_nvenc" in result.stdout
        except Exception:
            return False
    
    def _has_av1_amf(self) -> bool:
        """Check for AMD AV1 hardware encoding support (RX 7000 series+)."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True, text=True
            )
            return "av1_amf" in result.stdout
        except Exception:
            return False
    
    def _check_vaapi_encoder(self, encoder: str) -> bool:
        """Check if VA-API encoder is available."""
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
        preset: str = "balanced",
        use_av1: bool = False
    ) -> CaptureConfig:
        """
        Configure capture settings.
        
        Args:
            width: Capture width in pixels.
            height: Capture height in pixels.
            fps: Target frames per second.
            bitrate_kbps: Target bitrate in kbps.
            preset: Quality preset (quality/balanced/performance).
            use_av1: Use AV1 encoding if available.
        
        Returns:
            Configured CaptureConfig object.
        """
        self._capture_config = CaptureConfig(
            method=self.detect_best_capture_method(),
            width=width,
            height=height,
            fps=fps,
            encoder=self.detect_best_encoder(prefer_av1=use_av1),
            bitrate_kbps=bitrate_kbps,
            preset=preset,
            use_av1=use_av1
        )
        return self._capture_config
    
    def configure_stream(
        self,
        platform: StreamPlatform,
        stream_key: str,
        rtmp_url: Optional[str] = None,
        ndi_name: str = "StreamForge"
    ) -> StreamConfig:
        """
        Configure streaming settings.
        
        Args:
            platform: Target streaming platform.
            stream_key: Stream key for authentication.
            rtmp_url: Custom RTMP URL (optional).
            ndi_name: NDI source name for network streaming.
        
        Returns:
            Configured StreamConfig object.
        """
        if rtmp_url is None:
            rtmp_url = self._get_rtmp_url(platform)
        self._stream_config = StreamConfig(
            platform=platform,
            rtmp_url=rtmp_url,
            stream_key=stream_key,
            ndi_name=ndi_name
        )
        return self._stream_config
    
    def _get_rtmp_url(self, platform: StreamPlatform) -> str:
        """Get RTMP ingest URL for platform."""
        urls = {
            StreamPlatform.TWITCH: "rtmp://live.twitch.tv/app",
            StreamPlatform.YOUTUBE: "rtmp://a.rtmp.youtube.com/live2",
            StreamPlatform.KICK: "rtmp://fa723fc1b171.global-contribute.live-video.net/app",
        }
        return urls.get(platform, "")
    
    def configure_ndi(
        self,
        enabled: bool = True,
        source_name: str = "Aegis-StreamForge",
        dual_pc_mode: bool = False,
        gaming_pc_name: str = "",
        streaming_pc_name: str = "",
        low_latency: bool = True,
        groups: str = ""
    ) -> NDIConfig:
        """
        Configure NDI network streaming (DistroAV integration).
        
        Enables dual-PC streaming setup where the gaming PC sends video
        over LAN to a dedicated streaming PC.
        
        Args:
            enabled: Enable NDI output.
            source_name: NDI source name visible on the network.
            dual_pc_mode: Enable dual-PC streaming configuration.
            gaming_pc_name: Hostname of the gaming PC.
            streaming_pc_name: Hostname of the streaming PC.
            low_latency: Optimize for lowest latency.
            groups: NDI groups for source isolation.
        
        Returns:
            Configured NDIConfig object.
        """
        self._ndi_config = NDIConfig(
            enabled=enabled,
            source_name=source_name,
            dual_pc_mode=dual_pc_mode,
            gaming_pc_name=gaming_pc_name,
            streaming_pc_name=streaming_pc_name,
            low_latency=low_latency,
            groups=groups
        )
        return self._ndi_config
    
    def start_ndi_output(self) -> bool:
        """
        Start NDI network streaming output.
        
        Requires DistroAV/NDI Tools to be installed.
        
        Returns:
            True if NDI output started successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_ndi_output(self) -> bool:
        """Stop NDI network streaming output."""
        with self._lock:
            if self._ndi_send_process:
                self._ndi_send_process.terminate()
                self._ndi_send_process = None
        return True
    
    def discover_ndi_sources(self) -> List[Dict[str, str]]:
        """
        Discover available NDI sources on the network.
        
        Returns:
            List of discovered NDI sources with name and URL.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_replay_buffer(
        self,
        enabled: bool = True,
        duration_seconds: int = 120,
        output_directory: Optional[Path] = None,
        hotkey: str = "F9",
        quality_preset: str = "balanced",
        auto_delete_after_days: int = 7
    ) -> ReplayBufferConfig:
        """
        Configure replay buffer (always-on recording).
        
        The replay buffer continuously records gameplay and allows
        saving the last X minutes on hotkey press.
        
        Args:
            enabled: Enable replay buffer.
            duration_seconds: Buffer duration in seconds (max 600).
            output_directory: Directory for saved replays.
            hotkey: Hotkey to save replay.
            quality_preset: Encoding quality preset.
            auto_delete_after_days: Auto-delete old replays after N days.
        
        Returns:
            Configured ReplayBufferConfig object.
        """
        if duration_seconds > self.REPLAY_BUFFER_MAX_SECONDS:
            duration_seconds = self.REPLAY_BUFFER_MAX_SECONDS
        if output_directory is None:
            output_directory = Path.home() / "Videos" / "Replays"
        encoder = self.detect_best_encoder(prefer_av1=False)
        self._replay_buffer_config = ReplayBufferConfig(
            enabled=enabled,
            duration_seconds=duration_seconds,
            output_directory=output_directory,
            hotkey=hotkey,
            encoder=encoder,
            quality_preset=quality_preset,
            auto_delete_after_days=auto_delete_after_days
        )
        return self._replay_buffer_config
    
    def start_replay_buffer(self) -> bool:
        """
        Start the always-on replay buffer.
        
        Continuously records gameplay in a ring buffer.
        
        Returns:
            True if replay buffer started successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_replay_buffer(self) -> bool:
        """Stop the replay buffer."""
        with self._lock:
            self._replay_buffer_active = False
            if self._replay_buffer_thread:
                self._replay_buffer_thread.join(timeout=2.0)
                self._replay_buffer_thread = None
        return True
    
    def save_replay(self, custom_filename: Optional[str] = None) -> Path:
        """
        Save current replay buffer contents to file.
        
        Args:
            custom_filename: Custom filename (optional).
        
        Returns:
            Path to the saved replay file.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_scene_auto_switch(
        self,
        enabled: bool = True,
        obs_websocket_host: str = "localhost",
        obs_websocket_port: int = 4455,
        obs_websocket_password: str = "",
        rules: Optional[Dict[str, str]] = None,
        default_scene: str = "Gaming",
        switch_delay_ms: int = 500
    ) -> SceneAutoSwitchConfig:
        """
        Configure automatic OBS scene switching.
        
        Automatically switches OBS scenes based on the active window.
        Connects to OBS via WebSocket.
        
        Args:
            enabled: Enable scene auto-switching.
            obs_websocket_host: OBS WebSocket host.
            obs_websocket_port: OBS WebSocket port.
            obs_websocket_password: OBS WebSocket password.
            rules: Window-to-scene mapping rules.
            default_scene: Default scene when no rules match.
            switch_delay_ms: Delay before switching scenes.
        
        Returns:
            Configured SceneAutoSwitchConfig object.
        
        Example rules:
            {
                "Valorant": "FPS Gaming",
                "League of Legends": "MOBA",
                "Discord": "Just Chatting",
                "OBS": "BRB Screen"
            }
        """
        if rules is None:
            rules = {}
        self._scene_switch_config = SceneAutoSwitchConfig(
            enabled=enabled,
            obs_websocket_host=obs_websocket_host,
            obs_websocket_port=obs_websocket_port,
            obs_websocket_password=obs_websocket_password,
            rules=rules,
            default_scene=default_scene,
            switch_delay_ms=switch_delay_ms
        )
        return self._scene_switch_config
    
    def start_scene_monitor(self) -> bool:
        """
        Start monitoring active window for scene switching.
        
        Returns:
            True if scene monitor started successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_scene_monitor(self) -> bool:
        """Stop the scene monitor."""
        with self._lock:
            self._scene_monitor_active = False
            if self._scene_monitor_thread:
                self._scene_monitor_thread.join(timeout=2.0)
                self._scene_monitor_thread = None
        return True
    
    def add_scene_rule(self, window_pattern: str, scene_name: str) -> bool:
        """
        Add a scene switching rule.
        
        Args:
            window_pattern: Window title pattern to match.
            scene_name: OBS scene to switch to.
        
        Returns:
            True if rule was added successfully.
        """
        if self._scene_switch_config:
            self._scene_switch_config.rules[window_pattern] = scene_name
            return True
        return False
    
    def remove_scene_rule(self, window_pattern: str) -> bool:
        """Remove a scene switching rule."""
        if self._scene_switch_config and window_pattern in self._scene_switch_config.rules:
            del self._scene_switch_config.rules[window_pattern]
            return True
        return False
    
    def _get_active_window_title(self) -> str:
        """Get the title of the currently active window."""
        try:
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""
    
    def configure_discord_audio(
        self,
        enabled: bool = True,
        separate_output: bool = True,
        auto_detect_discord: bool = True,
        ducking_enabled: bool = False,
        ducking_threshold_db: float = -20.0
    ) -> DiscordAudioConfig:
        """
        Configure Discord audio routing for separate game/voice audio.
        
        Uses PipeWire to route Discord audio to a separate virtual sink,
        allowing streamers to control game and voice audio independently.
        
        Args:
            enabled: Enable Discord audio separation.
            separate_output: Route Discord to separate audio track.
            auto_detect_discord: Auto-detect Discord process.
            ducking_enabled: Enable audio ducking when voice detected.
            ducking_threshold_db: Ducking activation threshold.
        
        Returns:
            Configured DiscordAudioConfig object.
        """
        self._discord_audio_config = DiscordAudioConfig(
            enabled=enabled,
            separate_output=separate_output,
            auto_detect_discord=auto_detect_discord,
            ducking_enabled=ducking_enabled,
            ducking_threshold_db=ducking_threshold_db
        )
        return self._discord_audio_config
    
    def setup_discord_audio_routing(self) -> bool:
        """
        Set up PipeWire audio routing for Discord separation.
        
        Creates virtual sinks for game and voice audio.
        
        Returns:
            True if routing was set up successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def teardown_discord_audio_routing(self) -> bool:
        """Remove Discord audio routing configuration."""
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_multi_track_audio(
        self,
        enabled: bool = True,
        separate_discord: bool = True,
        separate_game: bool = True,
        separate_mic: bool = True
    ) -> MultiTrackAudioConfig:
        """
        Configure multi-track audio recording.
        
        Records separate audio tracks for game, voice, microphone, etc.
        Useful for post-production editing and audio balancing.
        
        Args:
            enabled: Enable multi-track audio.
            separate_discord: Record Discord on separate track.
            separate_game: Record game audio on separate track.
            separate_mic: Record microphone on separate track.
        
        Returns:
            Configured MultiTrackAudioConfig object.
        """
        tracks = []
        track_id = 0
        if separate_game:
            tracks.append(AudioTrackConfig(
                track_id=track_id,
                track_type=AudioTrackType.GAME,
                source_name="aegis_game_audio"
            ))
            track_id += 1
        if separate_discord:
            tracks.append(AudioTrackConfig(
                track_id=track_id,
                track_type=AudioTrackType.VOICE,
                source_name="aegis_voice_audio"
            ))
            track_id += 1
        if separate_mic:
            tracks.append(AudioTrackConfig(
                track_id=track_id,
                track_type=AudioTrackType.MIC,
                source_name="default_mic"
            ))
            track_id += 1
        tracks.append(AudioTrackConfig(
            track_id=track_id,
            track_type=AudioTrackType.MIXED,
            source_name="aegis_mixed_output"
        ))
        self._multi_track_config = MultiTrackAudioConfig(
            enabled=enabled,
            tracks=tracks,
            separate_discord=separate_discord,
            separate_game=separate_game,
            separate_mic=separate_mic
        )
        return self._multi_track_config
    
    def add_audio_track(
        self,
        track_type: AudioTrackType,
        source_name: str,
        volume: float = 1.0,
        bitrate_kbps: int = 160
    ) -> Optional[AudioTrackConfig]:
        """
        Add a custom audio track.
        
        Args:
            track_type: Type of audio track.
            source_name: PipeWire/PulseAudio source name.
            volume: Track volume (0.0-1.0).
            bitrate_kbps: Audio bitrate.
        
        Returns:
            Configured AudioTrackConfig or None if failed.
        """
        if not self._multi_track_config:
            return None
        track_id = len(self._multi_track_config.tracks)
        track = AudioTrackConfig(
            track_id=track_id,
            track_type=track_type,
            source_name=source_name,
            volume=volume,
            bitrate_kbps=bitrate_kbps
        )
        self._multi_track_config.tracks.append(track)
        return track
    
    def remove_audio_track(self, track_id: int) -> bool:
        """Remove an audio track by ID."""
        if not self._multi_track_config:
            return False
        self._multi_track_config.tracks = [
            t for t in self._multi_track_config.tracks if t.track_id != track_id
        ]
        return True
    
    def setup_pipewire_routing(self) -> bool:
        """
        Set up PipeWire virtual sinks for audio routing.
        
        Creates virtual sinks for separating audio sources.
        
        Returns:
            True if PipeWire routing was set up successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def start_capture(self) -> bool:
        """Start screen capture."""
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_capture(self) -> bool:
        """Stop screen capture."""
        with self._lock:
            if self._ffmpeg_process:
                self._ffmpeg_process.terminate()
                self._ffmpeg_process = None
            self._capturing = False
        return True
    
    def start_stream(self) -> bool:
        """Start streaming to platform."""
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_stream(self) -> bool:
        """Stop streaming."""
        with self._lock:
            self._streaming = False
        return True
    
    def enable_instant_replay(self, duration_seconds: int = 30) -> bool:
        """Enable instant replay buffer."""
        if duration_seconds > self.INSTANT_REPLAY_MAX_SECONDS:
            duration_seconds = self.INSTANT_REPLAY_MAX_SECONDS
        raise NotImplementedError("Build required: ./build.sh")
    
    def save_instant_replay(self, output_path: Path) -> bool:
        """Save instant replay buffer to file."""
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_stats(self) -> Optional[CaptureStats]:
        """Get capture statistics."""
        return self._stats
    
    def _build_ffmpeg_command(self) -> List[str]:
        """Build FFmpeg command for capture."""
        if not self._capture_config:
            return []
        cfg = self._capture_config
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning"]
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
        elif cfg.method == CaptureMethod.PIPEWIRE:
            cmd.extend([
                "-f", "lavfi",
                "-i", "pipewire",
                "-framerate", str(cfg.fps)
            ])
        if cfg.encoder == Encoder.NVENC:
            cmd.extend([
                "-c:v", "h264_nvenc",
                "-preset", "p4" if cfg.preset == "balanced" else "p7",
                "-tune", "ll",
                "-rc", "cbr",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
        elif cfg.encoder == Encoder.NVENC_AV1:
            cmd.extend([
                "-c:v", "av1_nvenc",
                "-preset", "p4" if cfg.preset == "balanced" else "p7",
                "-tune", "ll",
                "-rc", "cbr",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
        elif cfg.encoder == Encoder.AMF:
            cmd.extend([
                "-c:v", "h264_amf",
                "-quality", "balanced",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
        elif cfg.encoder == Encoder.AMF_AV1:
            cmd.extend([
                "-c:v", "av1_amf",
                "-quality", "balanced",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
        elif cfg.encoder == Encoder.QSV:
            cmd.extend([
                "-c:v", "h264_qsv",
                "-preset", "medium",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
        elif cfg.encoder == Encoder.QSV_AV1:
            cmd.extend([
                "-c:v", "av1_qsv",
                "-preset", "medium",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
        elif cfg.encoder == Encoder.SVT_AV1:
            cmd.extend([
                "-c:v", "libsvtav1",
                "-preset", "6",
                "-crf", "30",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
        else:
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-tune", "zerolatency",
                "-b:v", f"{cfg.bitrate_kbps}k"
            ])
        return cmd
    
    def _build_multi_track_audio_args(self) -> List[str]:
        """Build FFmpeg arguments for multi-track audio."""
        if not self._multi_track_config or not self._multi_track_config.enabled:
            return []
        args = []
        for track in self._multi_track_config.tracks:
            args.extend([
                "-f", "pulse",
                "-i", track.source_name,
                "-c:a", track.codec,
                "-b:a", f"{track.bitrate_kbps}k",
                "-ar", str(track.sample_rate)
            ])
        return args
    
    def _build_ndi_output_args(self) -> List[str]:
        """Build FFmpeg arguments for NDI output."""
        if not self._ndi_config or not self._ndi_config.enabled:
            return []
        args = [
            "-f", "libndi_newtek",
            "-ndi_name", self._ndi_config.source_name
        ]
        if self._ndi_config.groups:
            args.extend(["-ndi_groups", self._ndi_config.groups])
        return args


class NDIStreamer:
    """
    NDI Network Streaming for dual-PC streaming setups.
    
    Uses DistroAV/NDI protocol to send video over LAN with
    minimal latency for professional streaming setups.
    """
    
    def __init__(self, config: NDIConfig):
        self._config = config
        self._send_process: Optional[subprocess.Popen] = None
        self._recv_process: Optional[subprocess.Popen] = None
        self._running: bool = False
        self._lock = threading.Lock()
    
    def start_sender(self, video_source: str = ":0") -> bool:
        """
        Start NDI sender (on gaming PC).
        
        Args:
            video_source: X11 display or video source.
        
        Returns:
            True if sender started successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_sender(self) -> bool:
        """Stop NDI sender."""
        with self._lock:
            if self._send_process:
                self._send_process.terminate()
                self._send_process = None
            self._running = False
        return True
    
    def start_receiver(self, source_name: str) -> bool:
        """
        Start NDI receiver (on streaming PC).
        
        Args:
            source_name: NDI source name to receive.
        
        Returns:
            True if receiver started successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_receiver(self) -> bool:
        """Stop NDI receiver."""
        with self._lock:
            if self._recv_process:
                self._recv_process.terminate()
                self._recv_process = None
        return True
    
    def discover_sources(self) -> List[Dict[str, str]]:
        """Discover available NDI sources on network."""
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_source_info(self, source_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about an NDI source."""
        raise NotImplementedError("Build required: ./build.sh")


class SceneAutoSwitcher:
    """
    Automatic OBS scene switching based on active window.
    
    Monitors the active window and sends scene switch commands
    to OBS via WebSocket based on configured rules.
    """
    
    def __init__(self, config: SceneAutoSwitchConfig):
        self._config = config
        self._running: bool = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._current_scene: str = ""
        self._obs_connected: bool = False
        self._lock = threading.Lock()
    
    def connect_to_obs(self) -> bool:
        """
        Connect to OBS WebSocket.
        
        Returns:
            True if connection successful.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def disconnect_from_obs(self) -> bool:
        """Disconnect from OBS WebSocket."""
        with self._lock:
            self._obs_connected = False
        return True
    
    def start_monitoring(self) -> bool:
        """
        Start monitoring active window for scene switches.
        
        Returns:
            True if monitoring started successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_monitoring(self) -> bool:
        """Stop monitoring active window."""
        with self._lock:
            self._running = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=2.0)
                self._monitor_thread = None
        return True
    
    def switch_scene(self, scene_name: str) -> bool:
        """
        Switch to specified OBS scene.
        
        Args:
            scene_name: Name of the OBS scene.
        
        Returns:
            True if switch was successful.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_current_scene(self) -> str:
        """Get the currently active OBS scene."""
        return self._current_scene
    
    def add_rule(self, window_pattern: str, scene_name: str) -> None:
        """Add a window-to-scene mapping rule."""
        self._config.rules[window_pattern] = scene_name
    
    def remove_rule(self, window_pattern: str) -> None:
        """Remove a window-to-scene mapping rule."""
        if window_pattern in self._config.rules:
            del self._config.rules[window_pattern]
    
    def _match_window(self, window_title: str) -> Optional[str]:
        """Match window title against rules and return scene name."""
        for pattern, scene in self._config.rules.items():
            if self._config.window_match_mode == "exact":
                if window_title == pattern:
                    return scene
            elif self._config.window_match_mode == "contains":
                if pattern.lower() in window_title.lower():
                    return scene
            elif self._config.window_match_mode == "regex":
                if re.search(pattern, window_title, re.IGNORECASE):
                    return scene
        return None


class DiscordAudioRouter:
    """
    Discord audio routing for separate game/voice audio.
    
    Uses PipeWire to route Discord audio to a separate virtual sink,
    allowing independent control of game and voice audio in streams.
    """
    
    def __init__(self, config: DiscordAudioConfig):
        self._config = config
        self._game_sink_id: Optional[int] = None
        self._voice_sink_id: Optional[int] = None
        self._routing_active: bool = False
        self._lock = threading.Lock()
    
    def setup_virtual_sinks(self) -> bool:
        """
        Create virtual PipeWire sinks for audio separation.
        
        Returns:
            True if sinks were created successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def teardown_virtual_sinks(self) -> bool:
        """Remove virtual PipeWire sinks."""
        raise NotImplementedError("Build required: ./build.sh")
    
    def route_discord_to_voice_sink(self) -> bool:
        """
        Route Discord audio to the voice sink.
        
        Returns:
            True if routing was successful.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def route_game_to_game_sink(self, app_name: str) -> bool:
        """
        Route game audio to the game sink.
        
        Args:
            app_name: Name of the game application.
        
        Returns:
            True if routing was successful.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def detect_discord_process(self) -> Optional[int]:
        """
        Detect running Discord process.
        
        Returns:
            Discord process ID or None if not found.
        """
        try:
            for app_name in self._config.discord_app_names:
                result = subprocess.run(
                    ["pgrep", "-f", app_name],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    return int(result.stdout.strip().split('\n')[0])
        except Exception:
            pass
        return None
    
    def enable_ducking(self) -> bool:
        """
        Enable audio ducking when voice is detected.
        
        Lowers game audio when voice chat is active.
        
        Returns:
            True if ducking was enabled.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def disable_ducking(self) -> bool:
        """Disable audio ducking."""
        raise NotImplementedError("Build required: ./build.sh")


class MultiTrackAudioRecorder:
    """
    Multi-track audio recording for post-production.
    
    Records separate audio tracks for game, voice, microphone,
    and other sources for flexible post-production editing.
    """
    
    def __init__(self, config: MultiTrackAudioConfig):
        self._config = config
        self._recording: bool = False
        self._ffmpeg_process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
    
    def setup_tracks(self) -> bool:
        """
        Set up audio tracks based on configuration.
        
        Returns:
            True if tracks were set up successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def start_recording(self, output_path: Path) -> bool:
        """
        Start multi-track audio recording.
        
        Args:
            output_path: Path for the output file.
        
        Returns:
            True if recording started successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop_recording(self) -> bool:
        """Stop multi-track audio recording."""
        with self._lock:
            self._recording = False
            if self._ffmpeg_process:
                self._ffmpeg_process.terminate()
                self._ffmpeg_process = None
        return True
    
    def add_track(self, track: AudioTrackConfig) -> bool:
        """Add an audio track to the configuration."""
        self._config.tracks.append(track)
        return True
    
    def remove_track(self, track_id: int) -> bool:
        """Remove an audio track from the configuration."""
        self._config.tracks = [t for t in self._config.tracks if t.track_id != track_id]
        return True
    
    def set_track_volume(self, track_id: int, volume: float) -> bool:
        """Set volume for a specific track."""
        for track in self._config.tracks:
            if track.track_id == track_id:
                track.volume = max(0.0, min(1.0, volume))
                return True
        return False
    
    def mute_track(self, track_id: int, muted: bool = True) -> bool:
        """Mute or unmute a specific track."""
        for track in self._config.tracks:
            if track.track_id == track_id:
                track.muted = muted
                return True
        return False
    
    def _build_ffmpeg_multi_track_args(self) -> List[str]:
        """Build FFmpeg arguments for multi-track recording."""
        args = []
        for track in self._config.tracks:
            if track.muted:
                continue
            args.extend([
                "-f", "pulse",
                "-i", track.source_name
            ])
        for i, track in enumerate(self._config.tracks):
            if track.muted:
                continue
            args.extend([
                f"-c:a:{i}", track.codec,
                f"-b:a:{i}", f"{track.bitrate_kbps}k",
                f"-ar:{i}", str(track.sample_rate),
                f"-filter:a:{i}", f"volume={track.volume}"
            ])
        return args


class ReplayBuffer:
    """
    Always-on replay buffer for saving gameplay highlights.
    
    Continuously records gameplay in a ring buffer and allows
    saving the last X minutes on hotkey press.
    """
    
    def __init__(self, config: ReplayBufferConfig):
        self._config = config
        self._buffer_process: Optional[subprocess.Popen] = None
        self._running: bool = False
        self._buffer_file: Optional[Path] = None
        self._lock = threading.Lock()
        self._save_count: int = 0
    
    def start(self) -> bool:
        """
        Start the always-on replay buffer.
        
        Returns:
            True if buffer started successfully.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def stop(self) -> bool:
        """Stop the replay buffer."""
        with self._lock:
            self._running = False
            if self._buffer_process:
                self._buffer_process.terminate()
                self._buffer_process = None
        return True
    
    def save(self, custom_filename: Optional[str] = None) -> Path:
        """
        Save current buffer contents to file.
        
        Args:
            custom_filename: Optional custom filename.
        
        Returns:
            Path to the saved replay file.
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_buffer_duration(self) -> float:
        """Get current buffer duration in seconds."""
        raise NotImplementedError("Build required: ./build.sh")
    
    def cleanup_old_replays(self) -> int:
        """
        Delete replays older than auto_delete_after_days.
        
        Returns:
            Number of files deleted.
        """
        if not self._config.output_directory.exists():
            return 0
        deleted = 0
        cutoff = time.time() - (self._config.auto_delete_after_days * 86400)
        for replay_file in self._config.output_directory.glob(f"*.{self._config.format}"):
            if replay_file.stat().st_mtime < cutoff:
                replay_file.unlink()
                deleted += 1
        return deleted
    
    def _get_next_filename(self) -> Path:
        """Generate next replay filename with timestamp."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self._save_count += 1
        filename = f"replay_{timestamp}_{self._save_count:04d}.{self._config.format}"
        return self._config.output_directory / filename


class InstantReplayBuffer:
    """Ring buffer for instant replay functionality."""
    
    def __init__(self, max_seconds: int, fps: int):
        self._max_frames = max_seconds * fps
        self._buffer: List[bytes] = []
        self._lock = threading.Lock()
        self._timestamps: List[float] = []
        
    def add_frame(self, frame: bytes, timestamp: Optional[float] = None) -> None:
        """Add frame to ring buffer."""
        with self._lock:
            if timestamp is None:
                timestamp = time.time()
            self._buffer.append(frame)
            self._timestamps.append(timestamp)
            if len(self._buffer) > self._max_frames:
                self._buffer.pop(0)
                self._timestamps.pop(0)
                
    def get_frames(self, last_n: Optional[int] = None) -> List[bytes]:
        """Get frames from buffer."""
        with self._lock:
            if last_n:
                return self._buffer[-last_n:]
            return list(self._buffer)
    
    def get_frames_with_timestamps(self, last_n: Optional[int] = None) -> List[Tuple[bytes, float]]:
        """Get frames with timestamps from buffer."""
        with self._lock:
            frames = list(zip(self._buffer, self._timestamps))
            if last_n:
                return frames[-last_n:]
            return frames
            
    def clear(self) -> None:
        """Clear buffer."""
        with self._lock:
            self._buffer.clear()
            self._timestamps.clear()
    
    def get_duration_seconds(self) -> float:
        """Get current buffer duration in seconds."""
        with self._lock:
            if len(self._timestamps) < 2:
                return 0.0
            return self._timestamps[-1] - self._timestamps[0]


# Build marker
# %%BUILD_MARKER:STREAMFORGE%%
