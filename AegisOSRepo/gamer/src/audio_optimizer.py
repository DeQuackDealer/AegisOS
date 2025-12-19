#!/usr/bin/env python3
"""
Aegis OS Audio Optimizer - Advanced Audio Processing for Gamer Edition

Comprehensive audio optimization system featuring:
- Zero-Latency PipeWire optimization (2.7ms competitive mode)
- Spatial Audio with virtual surround for headphones
- AI Noise Suppression via RNNoise integration
- Voice Chat Optimization for Discord/TeamSpeak
- Gaming-optimized EQ Presets
- Per-Application Volume Management
- Microphone Enhancement for streaming

WARNING: This is raw source code. Do not run directly.
Build with: ./build.sh

PREMIUM FEATURE - Requires Gamer Edition license
"""

from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import json


class SpatialAudioMode(Enum):
    """Spatial audio processing modes."""
    STEREO = "stereo"
    VIRTUAL_SURROUND_51 = "surround_5.1"
    VIRTUAL_SURROUND_71 = "surround_7.1"
    HRTF_BINAURAL = "hrtf_binaural"
    DOLBY_ATMOS = "dolby_atmos"


class EQPreset(Enum):
    """Gaming-optimized equalizer presets."""
    FPS = "fps"
    IMMERSIVE = "immersive"
    COMPETITIVE = "competitive"
    MUSIC = "music"
    MOVIE = "movie"
    FLAT = "flat"
    BASS_BOOST = "bass_boost"
    VOICE_CLARITY = "voice_clarity"


class VoiceChatApp(Enum):
    """Supported voice chat applications."""
    DISCORD = "discord"
    TEAMSPEAK = "teamspeak"
    MUMBLE = "mumble"
    STEAM_VOICE = "steam_voice"
    VENTRILO = "ventrilo"
    GENERIC = "generic"


@dataclass
class AudioProfile:
    """Audio latency profile configuration."""
    name: str
    quantum: int
    sample_rate: int
    latency_ms: float


@dataclass
class EQBand:
    """Equalizer band configuration."""
    frequency: int
    gain: float
    q_factor: float = 1.0


@dataclass
class SpatialAudioConfig:
    """Spatial audio processing configuration."""
    mode: SpatialAudioMode
    hrtf_profile: str = "default"
    room_size: float = 0.5
    distance_model: str = "inverse"
    enabled: bool = True


@dataclass
class NoiseSuppressionConfig:
    """AI noise suppression configuration."""
    enabled: bool = True
    strength: float = 0.85
    voice_activity_detection: bool = True
    model: str = "rnnoise"
    adaptive_threshold: bool = True


@dataclass
class VoiceChatConfig:
    """Voice chat optimization configuration."""
    app: VoiceChatApp
    priority_routing: bool = True
    latency_mode: str = "low"
    noise_gate_enabled: bool = True
    auto_ducking: bool = True
    ducking_level: float = 0.3


@dataclass
class MicrophoneConfig:
    """Microphone enhancement configuration."""
    auto_gain: bool = True
    target_level_db: float = -18.0
    noise_gate_threshold_db: float = -50.0
    noise_gate_release_ms: float = 200.0
    compressor_enabled: bool = True
    compressor_threshold_db: float = -20.0
    compressor_ratio: float = 4.0
    compressor_attack_ms: float = 5.0
    compressor_release_ms: float = 100.0
    de_esser_enabled: bool = False
    de_esser_frequency: int = 6000


@dataclass
class AppVolumeRule:
    """Per-application volume rule."""
    app_name: str
    app_type: str
    volume_percent: int
    priority: int = 0
    auto_duck_others: bool = False


class AudioOptimizer:
    """
    Advanced Audio Optimizer for Aegis OS Gamer Edition.
    
    Provides comprehensive audio processing and optimization including:
    - Zero-latency PipeWire configuration (2.7ms competitive mode)
    - Virtual surround sound and spatial audio for headphones
    - AI-powered noise suppression using RNNoise
    - Voice chat priority routing for Discord/TeamSpeak
    - Gaming-optimized equalizer presets
    - Per-application volume management
    - Professional microphone enhancement for streaming
    
    Configuration Files:
    - /etc/aegis/audio/pipewire.conf.d/
    - /etc/aegis/audio/spatial.conf
    - /etc/aegis/audio/eq-presets/
    - /etc/aegis/audio/app-volumes.json
    
    Attributes:
        config_dir: Path to audio configuration directory
        current_profile: Currently active audio latency profile
        spatial_config: Spatial audio processing settings
        noise_suppression: AI noise suppression settings
        mic_config: Microphone enhancement settings
    """
    
    LATENCY_PROFILES = {
        "competitive": AudioProfile(
            name="Competitive",
            quantum=128,
            sample_rate=48000,
            latency_ms=2.7
        ),
        "balanced": AudioProfile(
            name="Balanced",
            quantum=512,
            sample_rate=48000,
            latency_ms=10.7
        ),
        "quality": AudioProfile(
            name="Quality",
            quantum=1024,
            sample_rate=48000,
            latency_ms=21.3
        ),
        "ultra_low": AudioProfile(
            name="Ultra Low",
            quantum=64,
            sample_rate=48000,
            latency_ms=1.3
        ),
        "streaming": AudioProfile(
            name="Streaming",
            quantum=256,
            sample_rate=48000,
            latency_ms=5.3
        )
    }
    
    EQ_PRESETS = {
        EQPreset.FPS: [
            EQBand(frequency=60, gain=-3.0),
            EQBand(frequency=150, gain=-2.0),
            EQBand(frequency=400, gain=0.0),
            EQBand(frequency=1000, gain=2.0),
            EQBand(frequency=2500, gain=4.0),
            EQBand(frequency=6000, gain=3.0),
            EQBand(frequency=12000, gain=2.0),
        ],
        EQPreset.IMMERSIVE: [
            EQBand(frequency=60, gain=4.0),
            EQBand(frequency=150, gain=3.0),
            EQBand(frequency=400, gain=1.0),
            EQBand(frequency=1000, gain=0.0),
            EQBand(frequency=2500, gain=1.0),
            EQBand(frequency=6000, gain=2.0),
            EQBand(frequency=12000, gain=3.0),
        ],
        EQPreset.COMPETITIVE: [
            EQBand(frequency=60, gain=-6.0),
            EQBand(frequency=150, gain=-4.0),
            EQBand(frequency=400, gain=-1.0),
            EQBand(frequency=1000, gain=3.0),
            EQBand(frequency=2500, gain=5.0),
            EQBand(frequency=6000, gain=4.0),
            EQBand(frequency=12000, gain=1.0),
        ],
        EQPreset.MUSIC: [
            EQBand(frequency=60, gain=2.0),
            EQBand(frequency=150, gain=1.0),
            EQBand(frequency=400, gain=0.0),
            EQBand(frequency=1000, gain=0.0),
            EQBand(frequency=2500, gain=1.0),
            EQBand(frequency=6000, gain=2.0),
            EQBand(frequency=12000, gain=3.0),
        ],
        EQPreset.MOVIE: [
            EQBand(frequency=60, gain=5.0),
            EQBand(frequency=150, gain=3.0),
            EQBand(frequency=400, gain=0.0),
            EQBand(frequency=1000, gain=1.0),
            EQBand(frequency=2500, gain=2.0),
            EQBand(frequency=6000, gain=1.0),
            EQBand(frequency=12000, gain=2.0),
        ],
        EQPreset.FLAT: [
            EQBand(frequency=60, gain=0.0),
            EQBand(frequency=150, gain=0.0),
            EQBand(frequency=400, gain=0.0),
            EQBand(frequency=1000, gain=0.0),
            EQBand(frequency=2500, gain=0.0),
            EQBand(frequency=6000, gain=0.0),
            EQBand(frequency=12000, gain=0.0),
        ],
        EQPreset.BASS_BOOST: [
            EQBand(frequency=60, gain=6.0),
            EQBand(frequency=150, gain=4.0),
            EQBand(frequency=400, gain=1.0),
            EQBand(frequency=1000, gain=0.0),
            EQBand(frequency=2500, gain=0.0),
            EQBand(frequency=6000, gain=0.0),
            EQBand(frequency=12000, gain=0.0),
        ],
        EQPreset.VOICE_CLARITY: [
            EQBand(frequency=60, gain=-4.0),
            EQBand(frequency=150, gain=-2.0),
            EQBand(frequency=400, gain=1.0),
            EQBand(frequency=1000, gain=3.0),
            EQBand(frequency=2500, gain=4.0),
            EQBand(frequency=6000, gain=2.0),
            EQBand(frequency=12000, gain=0.0),
        ],
    }
    
    DEFAULT_APP_VOLUMES = {
        "game": AppVolumeRule("*", "game", 100, priority=10, auto_duck_others=True),
        "voice_chat": AppVolumeRule("*", "voice_chat", 85, priority=20),
        "music": AppVolumeRule("*", "music", 60, priority=5),
        "browser": AppVolumeRule("*", "browser", 70, priority=3),
        "notification": AppVolumeRule("*", "notification", 50, priority=1),
        "system": AppVolumeRule("*", "system", 80, priority=0),
    }
    
    VOICE_CHAT_APPS = {
        "discord": VoiceChatApp.DISCORD,
        "teamspeak3": VoiceChatApp.TEAMSPEAK,
        "ts3client": VoiceChatApp.TEAMSPEAK,
        "mumble": VoiceChatApp.MUMBLE,
        "steam": VoiceChatApp.STEAM_VOICE,
        "ventrilo": VoiceChatApp.VENTRILO,
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize Audio Optimizer.
        
        Args:
            config_dir: Path to configuration directory.
                       Defaults to /etc/aegis/audio/
        """
        self.config_dir = config_dir or Path("/etc/aegis/audio")
        self._current_profile: Optional[AudioProfile] = None
        self._spatial_config: Optional[SpatialAudioConfig] = None
        self._noise_suppression: Optional[NoiseSuppressionConfig] = None
        self._mic_config: Optional[MicrophoneConfig] = None
        self._voice_chat_config: Optional[VoiceChatConfig] = None
        self._eq_preset: Optional[EQPreset] = None
        self._app_volumes: Dict[str, AppVolumeRule] = {}
        self._custom_eq: List[EQBand] = []
        
    def apply_latency_profile(self, profile_name: str) -> bool:
        """
        Apply audio latency profile for PipeWire.
        
        Configures PipeWire quantum and sample rate for optimal
        gaming latency. Competitive mode achieves 2.7ms latency.
        
        Args:
            profile_name: Name of profile ('competitive', 'balanced', 
                         'quality', 'ultra_low', 'streaming')
        
        Returns:
            True if profile applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        profile = self.LATENCY_PROFILES.get(profile_name)
        if not profile:
            return False
        
        self._current_profile = profile
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_current_latency(self) -> float:
        """
        Get current audio latency in milliseconds.
        
        Returns:
            Current latency in ms, or default 21.3ms
        """
        if self._current_profile:
            return self._current_profile.latency_ms
        return 21.3
    
    def enable_spatial_audio(
        self,
        mode: SpatialAudioMode = SpatialAudioMode.VIRTUAL_SURROUND_71,
        hrtf_profile: str = "default"
    ) -> bool:
        """
        Enable spatial audio processing for headphones.
        
        Provides virtual surround sound using PipeWire spatial audio
        plugins. Supports multiple modes including 5.1/7.1 virtual
        surround and HRTF-based binaural processing.
        
        Args:
            mode: Spatial audio processing mode
            hrtf_profile: HRTF profile name for binaural processing
                         ('default', 'small_room', 'large_room', 'outdoor')
        
        Returns:
            True if spatial audio enabled successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        self._spatial_config = SpatialAudioConfig(
            mode=mode,
            hrtf_profile=hrtf_profile,
            enabled=True
        )
        raise NotImplementedError("Build required: ./build.sh")
    
    def disable_spatial_audio(self) -> bool:
        """
        Disable spatial audio processing.
        
        Returns:
            True if spatial audio disabled successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if self._spatial_config:
            self._spatial_config.enabled = False
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_spatial_audio(
        self,
        room_size: float = 0.5,
        distance_model: str = "inverse"
    ) -> bool:
        """
        Configure spatial audio parameters.
        
        Args:
            room_size: Virtual room size (0.0 to 1.0)
            distance_model: Distance attenuation model
                           ('linear', 'inverse', 'exponential')
        
        Returns:
            True if configuration applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if self._spatial_config:
            self._spatial_config.room_size = room_size
            self._spatial_config.distance_model = distance_model
        raise NotImplementedError("Build required: ./build.sh")
    
    def enable_noise_suppression(
        self,
        strength: float = 0.85,
        model: str = "rnnoise"
    ) -> bool:
        """
        Enable AI-powered noise suppression.
        
        Uses RNNoise machine learning model for real-time
        background noise removal without affecting voice quality.
        
        Args:
            strength: Suppression strength (0.0 to 1.0)
                     Higher values = more aggressive filtering
            model: Noise suppression model ('rnnoise', 'speexdsp')
        
        Returns:
            True if noise suppression enabled successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        self._noise_suppression = NoiseSuppressionConfig(
            enabled=True,
            strength=strength,
            model=model
        )
        raise NotImplementedError("Build required: ./build.sh")
    
    def disable_noise_suppression(self) -> bool:
        """
        Disable AI noise suppression.
        
        Returns:
            True if noise suppression disabled successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if self._noise_suppression:
            self._noise_suppression.enabled = False
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_noise_suppression(
        self,
        voice_activity_detection: bool = True,
        adaptive_threshold: bool = True
    ) -> bool:
        """
        Configure noise suppression parameters.
        
        Args:
            voice_activity_detection: Enable VAD for smart filtering
            adaptive_threshold: Automatically adjust noise threshold
        
        Returns:
            True if configuration applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if self._noise_suppression:
            self._noise_suppression.voice_activity_detection = voice_activity_detection
            self._noise_suppression.adaptive_threshold = adaptive_threshold
        raise NotImplementedError("Build required: ./build.sh")
    
    def enable_voice_chat_optimization(
        self,
        app: VoiceChatApp = VoiceChatApp.DISCORD
    ) -> bool:
        """
        Enable voice chat optimization for specific application.
        
        Provides priority routing and specialized processing for
        voice chat applications like Discord and TeamSpeak.
        
        Args:
            app: Voice chat application to optimize for
        
        Returns:
            True if optimization enabled successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        self._voice_chat_config = VoiceChatConfig(
            app=app,
            priority_routing=True,
            latency_mode="low"
        )
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_voice_chat(
        self,
        priority_routing: bool = True,
        latency_mode: str = "low",
        auto_ducking: bool = True,
        ducking_level: float = 0.3
    ) -> bool:
        """
        Configure voice chat optimization parameters.
        
        Args:
            priority_routing: Enable priority audio routing
            latency_mode: Latency mode ('ultra_low', 'low', 'balanced')
            auto_ducking: Automatically reduce other audio during voice
            ducking_level: Volume level for ducked audio (0.0 to 1.0)
        
        Returns:
            True if configuration applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if self._voice_chat_config:
            self._voice_chat_config.priority_routing = priority_routing
            self._voice_chat_config.latency_mode = latency_mode
            self._voice_chat_config.auto_ducking = auto_ducking
            self._voice_chat_config.ducking_level = ducking_level
        raise NotImplementedError("Build required: ./build.sh")
    
    def detect_voice_chat_app(self) -> Optional[VoiceChatApp]:
        """
        Detect running voice chat applications.
        
        Scans running processes to identify active voice chat
        applications for automatic optimization.
        
        Returns:
            Detected VoiceChatApp or None if not found
            
        Raises:
            NotImplementedError: When run without building
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def apply_eq_preset(self, preset: EQPreset) -> bool:
        """
        Apply gaming-optimized equalizer preset.
        
        Presets are tuned for specific gaming scenarios:
        - FPS: Enhanced footsteps and gunfire
        - IMMERSIVE: Rich bass for atmospheric games
        - COMPETITIVE: Focused mid-high for clarity
        - MUSIC: Balanced for music playback
        - MOVIE: Enhanced bass and dialogue
        - FLAT: No EQ processing
        - BASS_BOOST: Enhanced low frequencies
        - VOICE_CLARITY: Optimized for voice chat
        
        Args:
            preset: EQ preset to apply
        
        Returns:
            True if preset applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if preset not in self.EQ_PRESETS:
            return False
        
        self._eq_preset = preset
        self._custom_eq = self.EQ_PRESETS[preset].copy()
        raise NotImplementedError("Build required: ./build.sh")
    
    def set_custom_eq(self, bands: List[EQBand]) -> bool:
        """
        Set custom equalizer bands.
        
        Args:
            bands: List of EQBand configurations
        
        Returns:
            True if EQ applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        self._custom_eq = bands
        self._eq_preset = None
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_current_eq(self) -> Tuple[Optional[EQPreset], List[EQBand]]:
        """
        Get current equalizer settings.
        
        Returns:
            Tuple of (current preset or None, list of EQ bands)
        """
        return (self._eq_preset, self._custom_eq)
    
    def set_app_volume(
        self,
        app_name: str,
        volume_percent: int,
        app_type: str = "generic"
    ) -> bool:
        """
        Set volume for specific application.
        
        Per-application volume control with automatic adjustment
        based on application type and priority.
        
        Args:
            app_name: Application name or pattern
            volume_percent: Volume level (0-100)
            app_type: Application type ('game', 'voice_chat', 
                     'music', 'browser', 'notification', 'system')
        
        Returns:
            True if volume set successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        rule = AppVolumeRule(
            app_name=app_name,
            app_type=app_type,
            volume_percent=volume_percent
        )
        self._app_volumes[app_name] = rule
        raise NotImplementedError("Build required: ./build.sh")
    
    def set_app_type_volume(
        self,
        app_type: str,
        volume_percent: int,
        auto_duck: bool = False
    ) -> bool:
        """
        Set volume for all applications of a type.
        
        Args:
            app_type: Application type category
            volume_percent: Volume level (0-100)
            auto_duck: Automatically duck other apps when this type plays
        
        Returns:
            True if volume set successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if app_type in self.DEFAULT_APP_VOLUMES:
            self.DEFAULT_APP_VOLUMES[app_type].volume_percent = volume_percent
            self.DEFAULT_APP_VOLUMES[app_type].auto_duck_others = auto_duck
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_app_volumes(self) -> Dict[str, AppVolumeRule]:
        """
        Get current per-application volume rules.
        
        Returns:
            Dictionary of app name to volume rules
        """
        return {**self.DEFAULT_APP_VOLUMES, **self._app_volumes}
    
    def enable_microphone_enhancement(self) -> bool:
        """
        Enable microphone enhancement for streaming.
        
        Applies professional audio processing chain:
        - Auto-gain: Automatic level normalization
        - Noise gate: Remove background noise during silence
        - Compressor: Dynamic range control
        
        Returns:
            True if enhancement enabled successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        self._mic_config = MicrophoneConfig(
            auto_gain=True,
            compressor_enabled=True,
            noise_gate_threshold_db=-50.0
        )
        raise NotImplementedError("Build required: ./build.sh")
    
    def disable_microphone_enhancement(self) -> bool:
        """
        Disable all microphone enhancement.
        
        Returns:
            True if enhancement disabled successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        self._mic_config = None
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_microphone_auto_gain(
        self,
        enabled: bool = True,
        target_level_db: float = -18.0
    ) -> bool:
        """
        Configure microphone auto-gain.
        
        Automatically normalizes microphone input level to
        maintain consistent volume.
        
        Args:
            enabled: Enable/disable auto-gain
            target_level_db: Target RMS level in dB (-30 to 0)
        
        Returns:
            True if configuration applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if not self._mic_config:
            self._mic_config = MicrophoneConfig()
        self._mic_config.auto_gain = enabled
        self._mic_config.target_level_db = target_level_db
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_microphone_noise_gate(
        self,
        threshold_db: float = -50.0,
        release_ms: float = 200.0
    ) -> bool:
        """
        Configure microphone noise gate.
        
        Reduces background noise during silence by muting
        audio below threshold.
        
        Args:
            threshold_db: Gate threshold in dB (-80 to 0)
            release_ms: Gate release time in milliseconds
        
        Returns:
            True if configuration applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if not self._mic_config:
            self._mic_config = MicrophoneConfig()
        self._mic_config.noise_gate_threshold_db = threshold_db
        self._mic_config.noise_gate_release_ms = release_ms
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_microphone_compressor(
        self,
        enabled: bool = True,
        threshold_db: float = -20.0,
        ratio: float = 4.0,
        attack_ms: float = 5.0,
        release_ms: float = 100.0
    ) -> bool:
        """
        Configure microphone compressor for streaming.
        
        Provides dynamic range compression to maintain
        consistent audio levels during streaming.
        
        Args:
            enabled: Enable/disable compressor
            threshold_db: Compression threshold in dB (-60 to 0)
            ratio: Compression ratio (1:1 to 20:1)
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
        
        Returns:
            True if configuration applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if not self._mic_config:
            self._mic_config = MicrophoneConfig()
        self._mic_config.compressor_enabled = enabled
        self._mic_config.compressor_threshold_db = threshold_db
        self._mic_config.compressor_ratio = ratio
        self._mic_config.compressor_attack_ms = attack_ms
        self._mic_config.compressor_release_ms = release_ms
        raise NotImplementedError("Build required: ./build.sh")
    
    def configure_microphone_de_esser(
        self,
        enabled: bool = True,
        frequency: int = 6000
    ) -> bool:
        """
        Configure de-esser for reducing sibilance.
        
        Reduces harsh 's' and 'sh' sounds in voice recordings.
        
        Args:
            enabled: Enable/disable de-esser
            frequency: Target frequency in Hz (4000-10000)
        
        Returns:
            True if configuration applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        if not self._mic_config:
            self._mic_config = MicrophoneConfig()
        self._mic_config.de_esser_enabled = enabled
        self._mic_config.de_esser_frequency = frequency
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_microphone_config(self) -> Optional[MicrophoneConfig]:
        """
        Get current microphone enhancement configuration.
        
        Returns:
            MicrophoneConfig or None if not configured
        """
        return self._mic_config
    
    def apply_streaming_preset(self) -> bool:
        """
        Apply optimized settings for game streaming.
        
        Configures:
        - Streaming latency profile (5.3ms)
        - Full microphone enhancement
        - Voice chat optimization
        - EQ preset for voice clarity
        
        Returns:
            True if preset applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def apply_competitive_preset(self) -> bool:
        """
        Apply optimized settings for competitive gaming.
        
        Configures:
        - Ultra-low latency profile (1.3ms)
        - Competitive EQ preset
        - Spatial audio for positional awareness
        - Voice chat priority routing
        
        Returns:
            True if preset applied successfully
            
        Raises:
            NotImplementedError: When run without building
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def get_pipewire_config(self) -> Dict:
        """
        Generate PipeWire configuration based on current settings.
        
        Returns:
            Dictionary with PipeWire configuration
        """
        config = {
            "context.properties": {},
            "context.modules": [],
            "stream.properties": {},
        }
        
        if self._current_profile:
            config["context.properties"]["default.clock.quantum"] = self._current_profile.quantum
            config["context.properties"]["default.clock.rate"] = self._current_profile.sample_rate
            
        return config
    
    def export_config(self, path: Optional[Path] = None) -> bool:
        """
        Export current configuration to file.
        
        Args:
            path: Path to export configuration
        
        Returns:
            True if export successful
            
        Raises:
            NotImplementedError: When run without building
        """
        raise NotImplementedError("Build required: ./build.sh")
    
    def import_config(self, path: Path) -> bool:
        """
        Import configuration from file.
        
        Args:
            path: Path to configuration file
        
        Returns:
            True if import successful
            
        Raises:
            NotImplementedError: When run without building
        """
        raise NotImplementedError("Build required: ./build.sh")


# Build marker
# %%BUILD_MARKER:AUDIO_OPTIMIZER%%
