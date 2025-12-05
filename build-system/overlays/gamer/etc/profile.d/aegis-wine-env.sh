#!/bin/bash
# Aegis OS Wine/Proton Environment Variables
# Optimized for 90%+ Windows application effectiveness
# Version: 1.5.0
# Edition: Gamer / Gamer-AI / Server

# =============================================================================
# TIER DETECTION
# =============================================================================

AEGIS_TIER="freemium"
if [ -f /etc/aegis-gamer-ai-marker ]; then
    AEGIS_TIER="gamer_ai"
elif [ -f /etc/aegis-gamer-marker ]; then
    AEGIS_TIER="gamer"
elif [ -f /etc/aegis-server-marker ]; then
    AEGIS_TIER="server"
elif [ -f /etc/aegis-basic-marker ]; then
    AEGIS_TIER="basic"
elif [ -f /etc/aegis/license.json ]; then
    AEGIS_TIER=$(grep -oP '"edition"\s*:\s*"\K[^"]+' /etc/aegis/license.json 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo "freemium")
fi

export AEGIS_TIER

# =============================================================================
# WINE/PROTON CORE SETTINGS
# =============================================================================

# Enable large address awareness for 32-bit applications (access 4GB instead of 2GB)
export WINE_LARGE_ADDRESS_AWARE=1

# Enable staging shared memory for improved performance
export STAGING_SHARED_MEMORY=1

# Force large address aware in Proton
export PROTON_FORCE_LARGE_ADDRESS_AWARE=1

# Prefer system libraries when available for better performance
export WINEDLLOVERRIDES="${WINEDLLOVERRIDES:-};winemenubuilder.exe=d"

# =============================================================================
# SYNCHRONIZATION (FSYNC/ESYNC)
# =============================================================================

# Enable fsync (futex-based sync) - best performance, requires kernel 5.16+
# Fsync is preferred over esync when available
export PROTON_NO_FSYNC=0
export WINEFSYNC=1

# Enable esync (eventfd-based sync) as fallback
export PROTON_NO_ESYNC=0
export WINEESYNC=1

# =============================================================================
# NVIDIA SETTINGS
# =============================================================================

# Enable NVAPI for NVIDIA features (DLSS, RTX, etc.)
export PROTON_ENABLE_NVAPI=1
export DXVK_ENABLE_NVAPI=1

# Don't hide NVIDIA GPU from applications
export PROTON_HIDE_NVIDIA_GPU=0

# Enable threaded optimization for OpenGL
export __GL_THREADED_OPTIMIZATION=1

# Reduce CPU overhead in yield operations
export __GL_YIELD=NOTHING

# Enable shader disk cache
export __GL_SHADER_DISK_CACHE=1
export __GL_SHADER_DISK_CACHE_SKIP_CLEANUP=1

# Shader disk cache path
if [ -d "$HOME/.cache/aegis/gl-shader-cache" ] || mkdir -p "$HOME/.cache/aegis/gl-shader-cache" 2>/dev/null; then
    export __GL_SHADER_DISK_CACHE_PATH="$HOME/.cache/aegis/gl-shader-cache"
fi

# =============================================================================
# AMD SETTINGS
# =============================================================================

# Use RADV (Mesa Vulkan) for AMD GPUs - generally best performance
export AMD_VULKAN_ICD=RADV

# Enable RADV performance tests (GPL for shader compilation, rt for ray tracing)
export RADV_PERFTEST=gpl,rt

# Enable mesa threaded GL for OpenGL applications
export mesa_glthread=true

# =============================================================================
# DXVK SETTINGS (DirectX 9/10/11)
# =============================================================================

# Use DXVK instead of WineD3D
export PROTON_USE_WINED3D=0

# Enable async shader compilation to reduce stutter
export DXVK_ASYNC=1

# Enable state cache for faster shader loading
export DXVK_STATE_CACHE=1

# DXVK state cache path
if [ -d "$HOME/.cache/aegis/dxvk-state-cache" ] || mkdir -p "$HOME/.cache/aegis/dxvk-state-cache" 2>/dev/null; then
    export DXVK_STATE_CACHE_PATH="$HOME/.cache/aegis/dxvk-state-cache"
fi

# Log level for DXVK (none, error, warn, info, debug)
export DXVK_LOG_LEVEL=none

# =============================================================================
# VKD3D-PROTON SETTINGS (DirectX 12)
# =============================================================================

# VKD3D shader cache path
if [ -d "$HOME/.cache/aegis/vkd3d-shader-cache" ] || mkdir -p "$HOME/.cache/aegis/vkd3d-shader-cache" 2>/dev/null; then
    export VKD3D_SHADER_CACHE_PATH="$HOME/.cache/aegis/vkd3d-shader-cache"
fi

# VKD3D feature level (12_0, 12_1, 12_2)
export VKD3D_FEATURE_LEVEL=12_1

# VKD3D shader model
export VKD3D_SHADER_MODEL=6_6

# Enable DXR (DirectX Raytracing)
export VKD3D_CONFIG=dxr11,dxr

# VKD3D log level
export VKD3D_DEBUG=none

# =============================================================================
# SHADER CACHE PATHS
# =============================================================================

# Create shader cache directories
mkdir -p "$HOME/.cache/aegis/dxvk-state-cache" 2>/dev/null
mkdir -p "$HOME/.cache/aegis/vkd3d-shader-cache" 2>/dev/null
mkdir -p "$HOME/.cache/aegis/gl-shader-cache" 2>/dev/null
mkdir -p "$HOME/.cache/mesa_shader_cache" 2>/dev/null

# Mesa shader cache
export MESA_SHADER_CACHE_DIR="$HOME/.cache/mesa_shader_cache"
export MESA_SHADER_CACHE_MAX_SIZE=10G

# Radeon shader cache
export RADV_PERFTEST=gpl

# =============================================================================
# FSR (FIDELITYFX SUPER RESOLUTION) SETTINGS
# =============================================================================

# Enable Wine FSR for fullscreen applications (when supported)
# 0 = disabled, 1 = enabled
export WINE_FULLSCREEN_FSR=0

# FSR sharpening strength (0-5, higher = sharper)
export WINE_FULLSCREEN_FSR_STRENGTH=2

# FSR mode (ultra_quality, quality, balanced, performance, ultra_performance)
export WINE_FULLSCREEN_FSR_MODE=balanced

# =============================================================================
# AUDIO SETTINGS
# =============================================================================

# Prefer PipeWire for audio
if command -v pipewire &> /dev/null; then
    export PULSE_LATENCY_MSEC=20
fi

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================

# Disable VSync at driver level (games can still enable it)
export vblank_mode=0
export __GL_SYNC_TO_VBLANK=0

# Enable fullscreen optimizations
export SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS=0

# Gamepad/controller settings
export SDL_GAMECONTROLLER_ALLOW_STEAM_VIRTUAL_GAMEPAD=1

# =============================================================================
# TIER-SPECIFIC FEATURES
# =============================================================================

case "$AEGIS_TIER" in
    "gamer"|"gamer_ai"|"server")
        # Full Wine/Proton features enabled
        export AEGIS_WINE_FEATURES="full"
        
        # Enable all upscaling technologies
        export AEGIS_DLSS_ENABLED=1
        export AEGIS_FSR_ENABLED=1
        export AEGIS_XESS_ENABLED=1
        
        # Enable ray tracing
        export AEGIS_RAY_TRACING=1
        
        # Enable shader pre-caching
        export AEGIS_SHADER_PRECACHE=1
        
        # Enable per-game profiles
        export AEGIS_PER_GAME_PROFILES=1
        
        # Enable Gamescope integration
        export AEGIS_GAMESCOPE=1
        
        # Proton paths
        export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam"
        export STEAM_COMPAT_DATA_PATH="$HOME/.local/share/Steam/steamapps/compatdata"
        
        # GE-Proton path
        if [ -d "$HOME/.local/share/Steam/compatibilitytools.d" ]; then
            export PROTON_GE_PATH="$HOME/.local/share/Steam/compatibilitytools.d"
        fi
        ;;
        
    "basic")
        # Basic Wine features only
        export AEGIS_WINE_FEATURES="basic"
        
        # Disable advanced features
        export AEGIS_DLSS_ENABLED=0
        export AEGIS_FSR_ENABLED=0
        export AEGIS_RAY_TRACING=0
        export AEGIS_SHADER_PRECACHE=0
        export AEGIS_PER_GAME_PROFILES=0
        
        # Disable DXVK (use WineD3D)
        export PROTON_USE_WINED3D=1
        export DXVK_ASYNC=0
        ;;
        
    "freemium"|*)
        # Wine disabled for freemium
        export AEGIS_WINE_FEATURES="disabled"
        export AEGIS_WINE_MESSAGE="Wine/Proton features require BASIC edition or higher"
        ;;
esac

# =============================================================================
# AI-ENHANCED FEATURES (GAMER_AI ONLY)
# =============================================================================

if [ "$AEGIS_TIER" = "gamer_ai" ]; then
    export AEGIS_AI_OPTIMIZATION=1
    export AEGIS_AUTO_TUNING=1
    export AEGIS_PREDICTIVE_CACHING=1
fi

# =============================================================================
# SERVER-SPECIFIC FEATURES
# =============================================================================

if [ "$AEGIS_TIER" = "server" ]; then
    export AEGIS_HEADLESS_MODE=1
    export AEGIS_REMOTE_MANAGEMENT=1
fi

# =============================================================================
# WINE PREFIX DEFAULTS
# =============================================================================

# Default Wine prefix location
export WINEPREFIX="${WINEPREFIX:-$HOME/.wine}"

# Default Wine architecture
export WINEARCH="${WINEARCH:-win64}"

# Aegis Wine prefixes directory
export AEGIS_WINE_PREFIXES="$HOME/.local/share/aegis/wine-prefixes"

# =============================================================================
# PROTON SETTINGS
# =============================================================================

# Proton compatibility tools directory
export PROTON_COMPAT_TOOLS_DIR="$HOME/.local/share/Steam/compatibilitytools.d"

# Enable Proton media foundation workaround
export PROTON_USE_WINE_GSTREAMER=1

# =============================================================================
# MANGOHUD DEFAULTS
# =============================================================================

if command -v mangohud &> /dev/null; then
    export MANGOHUD_CONFIG="fps,frametime,cpu_temp,gpu_temp,ram,vram"
fi

# =============================================================================
# GAMEMODE DEFAULTS
# =============================================================================

if command -v gamemoderun &> /dev/null; then
    export AEGIS_GAMEMODE_AVAILABLE=1
fi

# =============================================================================
# DEBUG/DEVELOPMENT (Disabled by default)
# =============================================================================

# Uncomment for debugging:
# export WINEDEBUG=+all
# export DXVK_LOG_LEVEL=debug
# export VKD3D_DEBUG=all
# export PROTON_LOG=1

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Function to run Windows applications with optimized settings
aegis-wine-run() {
    if [ "$AEGIS_TIER" = "freemium" ]; then
        echo "Wine/Proton features require BASIC edition or higher"
        echo "Upgrade at: https://aegis-os.com/pricing"
        return 1
    fi
    
    local exe="$1"
    shift
    
    if command -v gamemoderun &> /dev/null && [ "$AEGIS_TIER" != "basic" ]; then
        gamemoderun wine "$exe" "$@"
    else
        wine "$exe" "$@"
    fi
}

# Function to run with MangoHUD overlay
aegis-wine-hud() {
    if [ "$AEGIS_TIER" = "freemium" ] || [ "$AEGIS_TIER" = "basic" ]; then
        echo "MangoHUD features require GAMER edition or higher"
        return 1
    fi
    
    if command -v mangohud &> /dev/null; then
        MANGOHUD=1 aegis-wine-run "$@"
    else
        echo "MangoHUD not installed"
        aegis-wine-run "$@"
    fi
}

# Function to run with maximum performance settings
aegis-wine-perf() {
    if [ "$AEGIS_TIER" != "gamer" ] && [ "$AEGIS_TIER" != "gamer_ai" ] && [ "$AEGIS_TIER" != "server" ]; then
        echo "Performance mode requires GAMER edition or higher"
        return 1
    fi
    
    DXVK_FRAME_RATE=0 \
    __GL_YIELD=NOTHING \
    vblank_mode=0 \
    __GL_SYNC_TO_VBLANK=0 \
    gamemoderun wine "$@"
}

# Export helper functions
export -f aegis-wine-run 2>/dev/null || true
export -f aegis-wine-hud 2>/dev/null || true
export -f aegis-wine-perf 2>/dev/null || true

# =============================================================================
# STARTUP MESSAGE (DEBUG)
# =============================================================================

# Uncomment for startup debugging:
# echo "[Aegis Wine] Tier: $AEGIS_TIER, Features: $AEGIS_WINE_FEATURES"
