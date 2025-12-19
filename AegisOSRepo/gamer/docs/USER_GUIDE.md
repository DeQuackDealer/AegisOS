# 🎮 Aegis OS Gamer Edition - User Guide

Welcome to Aegis OS Gamer Edition! This guide will help you get the most out of your gaming experience.

---

## 📋 Table of Contents

1. [Getting Started](#-getting-started)
2. [Aegis Game Library](#-aegis-game-library)
3. [The 11 System Services](#-the-11-system-services)
4. [Optimization Settings Panel](#-optimization-settings-panel)
5. [Exclusive Apps](#-exclusive-apps)
6. [Troubleshooting](#-troubleshooting)
7. [Keyboard Shortcuts](#-keyboard-shortcuts)

---

## 🚀 Getting Started

### What is Aegis OS Gamer Edition?

Aegis OS Gamer Edition is a premium gaming operating system designed to give you the best possible gaming experience on Linux. It includes:

- ✅ **11 automatic optimization services** that run in the background
- ✅ **Built-in game upscaling** (FSR, DLSS, XeSS) for any game
- ✅ **Dual GPU support** for maximum performance
- ✅ **One-click streaming** with ultra-low latency
- ✅ **22+ console emulators** pre-configured
- ✅ **Windows game compatibility** via Wine/Proton

### First Boot Setup

When you first start Aegis OS Gamer Edition:

1. **🖥️ Welcome Screen** - A friendly wizard will guide you through initial setup
2. **🌐 Network Connection** - Connect to WiFi or plug in an ethernet cable
3. **🎮 Gaming Profile** - Choose your gaming style (Competitive, Casual, or Balanced)
4. **📁 Game Folders** - Point the system to where your games are stored
5. **🎨 Desktop Style** - Pick from 12 pre-built desktop layouts

The setup takes about 5 minutes, and you'll be gaming right after!

### License Activation

Your Gamer Edition license needs to be activated once:

1. **Open** the Aegis License Manager from the application menu
2. **Enter** your license key (found in your purchase email)
3. **Click** "Activate" and wait a few seconds
4. **Done!** Your license is now tied to your computer

💡 **Tips:**
- Your license works on one computer at a time
- Lost your key? Check your email or contact support
- You can transfer your license if you get a new computer

---

## 🎮 Aegis Game Library

The Aegis Game Library is your central hub for all games. It finds and organizes games from multiple sources automatically.

### How to Launch It

- **Click** the Aegis Game Library icon on your desktop or taskbar
- **Or** open the application menu and search for "Game Library"
- **Or** press `Super + G` (Windows key + G)

### Scanning for Games

The Game Library automatically finds games from:

| Source | What It Finds |
|--------|---------------|
| 🎮 **Steam** | All your Steam games, including Proton titles |
| 🍷 **Lutris** | Wine games, GOG games, Epic games via Lutris |
| 🦸 **Heroic** | Epic Games Store and GOG Galaxy games |
| 📀 **GOG** | Native Linux GOG games |
| 🐧 **Native** | Any Linux games installed on your system |

**To manually scan:**
1. Click the ⚙️ **Settings** icon in the top-right
2. Select **"Scan for Games"**
3. Add custom folders if your games are in unusual locations
4. Click **"Start Scan"**

### SD Card and External Drive Support

Perfect for Steam Deck users or anyone with external storage!

**Adding an external drive:**
1. Plug in your SD card or external drive
2. Open Game Library → Settings → **Storage**
3. Click **"Add Storage Location"**
4. Select your external drive
5. Games on that drive will now appear in your library

💡 **The system remembers your drives** - just plug them in and your games appear automatically!

### Console Mode (Big Picture Style)

Console Mode transforms your PC into a couch-friendly gaming console:

**To enter Console Mode:**
- Press `F11` in the Game Library
- Or click the **🎮 Console Mode** button in the top-right

**Console Mode Features:**
- 🕹️ Full controller navigation
- 📺 Big, TV-friendly interface
- 🚀 Quick launch from your recently played
- ⚙️ Easy access to per-game settings
- 🎬 Background video previews for games

**To exit Console Mode:**
- Press `Escape` on your keyboard
- Or press the **Xbox/PlayStation button** on your controller

### Game Profiles and Per-Game Settings

Every game can have its own custom settings:

**Creating a Game Profile:**
1. Right-click any game in your library
2. Select **"Game Settings"**
3. Customize:
   - 🎛️ **Performance preset** (Quality, Balanced, Performance)
   - 🔧 **Proton version** (for Windows games)
   - 📊 **Upscaling** (FSR, DLSS, XeSS, or Off)
   - 🎯 **Frame limit** (for battery saving or sync)
   - 🔊 **Audio profile** (headphones, speakers, surround)

💡 Settings are saved per-game - Aegis remembers them for next time!

---

## ⚙️ The 11 System Services

These services run automatically in the background. You don't need to do anything - they just work! But here's what each one does if you're curious.

### 1. 🧠 Adaptive RAM Guardian

**What it does:** Keeps your memory clean and fast while gaming.

**In plain language:** Think of RAM like your desk space. This service keeps it tidy, making sure your game has plenty of room to work. It moves unimportant stuff out of the way and prevents memory "leaks" (when programs forget to clean up after themselves).

**When it helps:**
- ✅ Long gaming sessions (4+ hours)
- ✅ Running multiple games/apps
- ✅ Games that use lots of memory
- ✅ Older computers with less RAM

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **Memory** tab
3. Options:
   - **Aggressive** - Maximum memory savings (might close background apps)
   - **Balanced** - Good for most users (default)
   - **Gentle** - Keeps all apps running, lighter optimization

---

### 2. 📹 StreamForge Capture Stack

**What it does:** Records and streams your gameplay with extremely low impact on performance.

**In plain language:** This is like having a professional video studio built into your computer. It can record your gameplay, stream to Twitch/YouTube, or save the last 30 seconds when something amazing happens (Replay Buffer).

**Key features:**
- **NDI Streaming** - Send video to another PC for streaming (zero CPU impact!)
- **AV1 Encoding** - Smaller files, same quality (if your GPU supports it)
- **Replay Buffer** - Always-on recording that saves only when you want it

**When it helps:**
- ✅ Streaming to Twitch, YouTube, etc.
- ✅ Recording gameplay clips
- ✅ Capturing "did you see that?!" moments
- ✅ Dual-PC streaming setups

**How to configure:**
1. Open **StreamForge Studio** from your apps
2. Choose your mode:
   - **Replay Buffer** - Press a hotkey to save the last 30-120 seconds
   - **Recording** - Traditional recording to a file
   - **Streaming** - Go live on your platform
   - **NDI Output** - Send to another computer

---

### 3. ⚡ Latency FastPath

**What it does:** Reduces the delay between your actions and what happens on screen.

**In plain language:** When you click your mouse, this service makes sure the game responds as fast as physically possible. It's like giving your inputs a VIP express lane to the game.

**What it optimizes:**
- 🖱️ Mouse/keyboard input processing
- 🎮 Controller polling rate
- 💻 CPU scheduling for games
- ⚡ USB device priority

**When it helps:**
- ✅ Competitive/esports games
- ✅ Fast-paced action games
- ✅ Rhythm games
- ✅ Any game where reaction time matters

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **Latency** tab
3. Options:
   - **Ultra** - Minimum latency, maximum power usage
   - **Balanced** - Good latency with reasonable power (default)
   - **Eco** - Save power, slightly higher latency

---

### 4. 🎨 VRAM Heatmap Balancer

**What it does:** Manages your graphics card's memory efficiently.

**In plain language:** Your GPU has its own memory (VRAM) separate from your main RAM. This service acts like a smart storage manager, keeping frequently-used textures ready and cleaning out old stuff to prevent stutters.

**What it does:**
- 📊 Monitors VRAM usage in real-time
- 🧹 Cleans up old shader cache files
- ⚖️ Balances memory between games and desktop
- 🚨 Warns you before VRAM runs out

**When it helps:**
- ✅ High-resolution gaming (1440p, 4K)
- ✅ Games with lots of textures
- ✅ Running multiple monitors
- ✅ Using video editing apps alongside games

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **GPU Memory** tab
3. View the live VRAM heatmap
4. Set warning threshold (default: 90% full)

---

### 5. 🌐 NetBoost Network Optimizer

**What it does:** Prioritizes your game's network traffic over everything else.

**In plain language:** When you're gaming online, this service makes sure your game data gets priority over downloads, streaming, or other devices on your network. It's like having a dedicated fast lane on the internet just for your game.

**What it optimizes:**
- 📶 Game traffic prioritization (QoS)
- 🔧 Network congestion control (BBR)
- 📊 Packet scheduling
- 🎯 Route optimization

**When it helps:**
- ✅ Online multiplayer games
- ✅ Competitive gaming
- ✅ Streaming while gaming
- ✅ Shared household internet

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **Network** tab
3. Options:
   - **Gaming Mode** - Maximum priority for games
   - **Streaming Mode** - Balance between game and stream
   - **Download Mode** - Prioritize downloads over games

---

### 6. 🔧 Shader Pre-Cache Engine

**What it does:** Compiles game shaders in the background before you play.

**In plain language:** Games need to prepare special graphics instructions called "shaders." Normally this causes stuttering when you first play. This service does all that preparation ahead of time, so your game runs smooth from the first second.

**How it works:**
- 📥 Downloads pre-compiled shaders from the community
- 🔨 Compiles new shaders in the background
- 💾 Stores shaders for instant access next time
- 🔄 Updates when games are patched

**When it helps:**
- ✅ First time playing any game
- ✅ After game updates
- ✅ Games using Vulkan (DXVK/VKD3D)
- ✅ Eliminating stutter in general

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **Shaders** tab
3. Options:
   - View shader cache size
   - Force recompile for specific games
   - Enable/disable community shader downloads

---

### 7. 🎵 Audio Zero-Latency

**What it does:** Provides crystal-clear, instant audio with special effects.

**In plain language:** This service makes your game audio respond instantly with no delay. It also adds cool features like 3D spatial audio (hear enemies behind you!) and removes background noise from your microphone.

**Features:**
- ⚡ **Ultra-low latency** - Audio responds instantly
- 🎧 **Spatial Audio** - 3D sound positioning for any headphones
- 🤫 **AI Noise Suppression** - Removes keyboard clicks, fans, etc. from your mic
- 🎛️ **EQ Presets** - Pre-tuned profiles for different games

**When it helps:**
- ✅ Competitive shooters (hear footsteps clearly)
- ✅ Horror games (immersive 3D audio)
- ✅ Voice chat (clean microphone audio)
- ✅ Music/rhythm games (perfect sync)

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **Audio** tab
3. Options:
   - Enable/disable Spatial Audio
   - Adjust Noise Suppression strength
   - Choose EQ preset (FPS, Immersive, Music, etc.)

---

### 8. 🌡️ Thermal Guard

**What it does:** Keeps your computer cool and prevents overheating.

**In plain language:** Gaming makes your computer hot. This service monitors temperatures and automatically adjusts fans to keep everything cool. It prevents your computer from throttling (slowing down) due to heat.

**What it monitors:**
- 🔥 CPU temperature
- 🎮 GPU temperature
- 💨 Fan speeds
- ⚡ Power consumption

**When it helps:**
- ✅ Long gaming sessions
- ✅ Hot environments
- ✅ Laptops (especially important!)
- ✅ Quiet operation when not gaming

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **Thermal** tab
3. Options:
   - **Silent** - Quiet fans, higher temps allowed
   - **Balanced** - Good balance (default)
   - **Performance** - Maximum cooling, louder fans
   - **Custom** - Set your own fan curves

---

### 9. 🖱️ Input Optimizer

**What it does:** Makes your mouse and keyboard respond as fast as possible.

**In plain language:** This service removes any delay or "smoothing" from your mouse, making it feel direct and responsive. It also increases how often your mouse reports its position - up to 8000 times per second!

**What it optimizes:**
- 🖱️ **8000Hz polling** - Your mouse updates 8000x per second (if supported)
- ➡️ **Flat acceleration** - No mouse acceleration, pure 1:1 movement
- ⚡ **USB IRQ pinning** - Dedicated processing for your input devices
- 🔧 **Debounce tuning** - Prevents double-clicks from worn switches

**When it helps:**
- ✅ FPS/shooter games
- ✅ Fast-paced competitive games
- ✅ Precision aiming
- ✅ Any game where mouse accuracy matters

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **Input** tab
3. Options:
   - Set polling rate (1000Hz-8000Hz)
   - Enable/disable acceleration
   - Adjust debounce timing
   - Configure per-game sensitivity

---

### 10. 🖥️ Display Optimizer

**What it does:** Gets the best possible image from your monitor.

**In plain language:** This service makes sure your games look amazing. It enables smooth variable refresh rates, HDR colors, and even AI-powered frame generation to boost your FPS.

**Features:**
- 🔄 **VRR (Variable Refresh Rate)** - Smooth gameplay with FreeSync/G-Sync
- 🌈 **HDR Support** - Vibrant colors and deep blacks
- 🚀 **Frame Generation** - AI creates extra frames for smoother motion
- 📐 **Integer Scaling** - Pixel-perfect upscaling for retro games

**When it helps:**
- ✅ Any gaming (VRR eliminates tearing)
- ✅ HDR-supported games and monitors
- ✅ Getting extra FPS via frame generation
- ✅ Playing old pixel-art games

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **Display** tab
3. Options:
   - Enable/disable VRR
   - Configure HDR settings
   - Choose frame generation mode (FSR 3, AFMF, DLSS FG)
   - Enable integer scaling for specific games

---

### 11. 🧬 Kernel Optimizer

**What it does:** Fine-tunes the core of the operating system for gaming.

**In plain language:** The kernel is the "brain" of your operating system. This service tells it to give your game top priority for CPU time, dedicate specific CPU cores just for gaming, and use special scheduling tricks to reduce stuttering.

**What it optimizes:**
- 🎯 **CPU Isolation** - Reserve cores exclusively for games
- 📊 **LAVD Scheduler** - Smart CPU scheduling that prioritizes games
- ⏱️ **Tickless Mode** - Reduce CPU interruptions during gameplay
- ⚡ **Power Management** - Keep CPUs at gaming speeds

**When it helps:**
- ✅ CPU-heavy games
- ✅ Streaming while gaming (separate cores)
- ✅ Reducing micro-stutters
- ✅ Consistent frame times

**How to configure:**
1. Open **Aegis Performance Tuner**
2. Go to **Kernel** tab
3. Options:
   - Set number of cores to isolate for gaming
   - Choose scheduler profile
   - Enable/disable tickless mode
   - Configure power profile

---

## 🎛️ Optimization Settings Panel

### How to Access It

The Optimization Settings Panel is available in multiple ways:

1. **From Game Library:**
   - Right-click any game → "Optimize"
   - Or click the ⚡ icon next to a game

2. **From System:**
   - Open **Aegis Performance Tuner** from your apps
   - Or right-click the system tray icon → "Performance Settings"

3. **Quick Access:**
   - Press `Super + P` (Windows key + P)

### Recommended Settings by Scenario

#### 🎯 Competitive FPS Gaming

For games like CS2, Valorant, Apex Legends where every millisecond counts:

| Setting | Recommendation |
|---------|---------------|
| **Latency FastPath** | Ultra |
| **Input Optimizer** | 8000Hz, No acceleration |
| **Display Optimizer** | VRR On, Frame Gen Off |
| **Audio** | Spatial Audio On, Low latency mode |
| **Kernel** | 2-4 cores isolated for game |
| **RAM Guardian** | Aggressive |
| **Upscaling** | Off or Performance mode |

💡 **Priority:** Low latency > High FPS > Graphics quality

---

#### 🌟 Single-Player / Immersive Gaming

For games like Cyberpunk 2077, Elden Ring, or story-driven adventures:

| Setting | Recommendation |
|---------|---------------|
| **Display Optimizer** | HDR On, Frame Gen On |
| **Upscaling** | Quality mode (FSR/DLSS) |
| **Audio** | Spatial Audio On, High quality |
| **Thermal Guard** | Balanced |
| **Latency FastPath** | Balanced |
| **Shaders** | Pre-cache enabled |

💡 **Priority:** Visual quality > Smooth frame rate > Low latency

---

#### 📺 Streaming Setup

For streaming to Twitch, YouTube, or recording content:

| Setting | Recommendation |
|---------|---------------|
| **StreamForge** | AV1 encoding (or NVENC/AMF) |
| **Kernel** | Isolate 2 cores for streaming |
| **NetBoost** | Streaming Mode |
| **RAM Guardian** | Balanced |
| **Audio** | Noise suppression On |
| **Replay Buffer** | 60-120 seconds |

💡 **Priority:** Stream stability > Game performance > Quality

---

#### 🔋 Power Saving / Laptop Mode

For gaming on battery or keeping your laptop cool and quiet:

| Setting | Recommendation |
|---------|---------------|
| **Thermal Guard** | Silent mode |
| **Latency FastPath** | Eco |
| **Display Optimizer** | VRR On, Frame Gen Off |
| **Frame Limit** | 60 FPS cap |
| **Kernel** | Power saver governor |
| **Upscaling** | Performance mode |

💡 **Priority:** Battery life > Thermals > Performance

---

## 📱 Exclusive Apps

### 🎮 Aegis Game Library

Your unified game launcher with all your games in one place.

**Key Features:**
- 📚 **Unified Library** - Steam, Epic, GOG, Lutris, Native games together
- 🎮 **Console Mode** - Couch-friendly, controller-navigated interface
- 💾 **External Storage** - SD cards and USB drives supported
- ⚙️ **Per-Game Settings** - Custom optimization for each game
- 📊 **Play Statistics** - Track your gaming time
- 🖼️ **Custom Artwork** - Set your own banners and icons
- 🔍 **Smart Search** - Find games by name, genre, or platform

---

### 📹 StreamForge Studio

One-click streaming with professional features.

**Key Features:**
- 🎬 **One-Click Go Live** - Stream to Twitch/YouTube instantly
- 🔴 **Replay Buffer** - Save the last 30-120 seconds anytime
- 📡 **NDI Output** - Send video to a second streaming PC
- 🎨 **Built-in Overlays** - Add webcam, alerts, chat
- 🎤 **Dual Audio** - Separate game and microphone tracks
- 📊 **Stream Dashboard** - Monitor bitrate, viewers, chat

**Quick Start:**
1. Open StreamForge Studio
2. Connect your Twitch/YouTube account
3. Click **Go Live**
4. That's it!

---

### 🎨 Aegis Wallpaper Engine

Animated and interactive desktop wallpapers.

**Key Features:**
- 🎬 **Video Wallpapers** - Use any video as wallpaper
- 🌐 **Web Wallpapers** - Interactive HTML5 wallpapers
- 🎮 **Game Integration** - Wallpapers react to game status
- 🔇 **Smart Pause** - Pauses when gaming to save resources
- 📁 **Workshop** - Download wallpapers from the community

**To set a wallpaper:**
1. Open Aegis Wallpaper Engine
2. Browse or search for a wallpaper
3. Click **Apply**
4. Enjoy your animated desktop!

---

### 🖥️ Desktop Style Manager

12 pre-built desktop layouts to customize your experience.

**Available Styles:**
1. 🪟 **Windows 10** - Classic taskbar, familiar layout
2. 🪟 **Windows 11** - Centered taskbar, modern widgets
3. 🍎 **macOS** - Top menu bar, dock at bottom
4. 🐧 **GNOME** - Clean, minimal, activities overview
5. 🎮 **Gaming Console** - Big tiles, controller-friendly
6. 📺 **Media Center** - Perfect for HTPCs
7. 🖥️ **Classic Desktop** - Traditional icons and taskbar
8. ⌨️ **Keyboard Warrior** - Minimal, tiling-window style
9. 🎨 **Cyberpunk** - Neon, futuristic aesthetic
10. 🌲 **Nature Calm** - Soft colors, relaxing theme
11. 🌙 **Dark Minimal** - Pure black, minimal distractions
12. ☀️ **Light & Bright** - Clean white, easy on eyes

**To change your style:**
1. Open Desktop Style Manager
2. Preview any style
3. Click **Apply**
4. Your desktop transforms instantly!

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 🎮 Game won't launch

**Try these steps:**
1. Right-click the game → **"Verify Game Files"**
2. Try a different Proton version (for Windows games)
3. Check if the game requires specific dependencies
4. Look at the game log: Right-click → **"View Log"**

#### 🖥️ Poor performance / low FPS

**Try these steps:**
1. Make sure you're using the correct GPU (check Settings → Display)
2. Enable upscaling (FSR/DLSS) to boost FPS
3. Lower in-game graphics settings
4. Check Thermal Guard - you might be overheating
5. Close background applications

#### 🔊 No audio or crackling sound

**Try these steps:**
1. Open Aegis Performance Tuner → Audio tab
2. Try increasing audio buffer size
3. Check your output device is correct
4. Restart the PipeWire service:
   ```
   systemctl --user restart pipewire
   ```

#### 🎮 Controller not recognized

**Try these steps:**
1. Unplug and replug the controller
2. Check if it appears in Game Library → Settings → Controllers
3. For Xbox controllers, ensure `xpadneo` driver is loaded
4. For PlayStation controllers, ensure `hid_playstation` is loaded

#### 📺 Screen tearing or stuttering

**Try these steps:**
1. Enable VRR in Display Optimizer
2. Set a frame limit matching your refresh rate
3. Disable compositor during gaming (should be automatic)
4. Update your GPU drivers

#### 🌐 High ping / lag in online games

**Try these steps:**
1. Open Aegis Performance Tuner → Network
2. Enable **Gaming Mode**
3. Check your network connection
4. Temporarily disable downloads
5. Consider using ethernet instead of WiFi

### How to Reset Settings

If things go wrong, you can reset to defaults:

**Reset a single service:**
1. Open Aegis Performance Tuner
2. Go to the relevant tab
3. Click **"Reset to Default"**

**Reset all settings:**
1. Open a terminal
2. Run: `aegis-reset-config --all`
3. Reboot your computer

**Factory reset (nuclear option):**
1. Open Settings → System → Reset
2. Choose **"Reset Aegis Configuration"**
3. This keeps your games but resets all optimizations

### Log Locations

When reporting issues, these logs are helpful:

| Log Type | Location |
|----------|----------|
| **System logs** | `journalctl -xe` |
| **Game logs** | `~/.local/share/aegis/logs/games/` |
| **Service logs** | `journalctl -u aegis-*` |
| **Crash reports** | `~/.local/share/aegis/crashes/` |
| **Performance logs** | `~/.local/share/aegis/logs/performance/` |

**Quick log export:**
```bash
aegis-support-bundle
```
This creates a ZIP file with all relevant logs for support tickets.

---

## ⌨️ Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Super + G` | Open Aegis Game Library |
| `Super + P` | Open Performance Tuner |
| `Super + S` | Open StreamForge Studio |
| `F10` | Save Replay Buffer (last 30 seconds) |
| `F9` | Toggle Recording |
| `F8` | Take Screenshot |
| `Super + Shift + O` | Toggle Performance Overlay |

### Console Mode Navigation

| Control | Action |
|---------|--------|
| `D-Pad / Left Stick` | Navigate menus |
| `A / Cross` | Select / Launch |
| `B / Circle` | Back / Cancel |
| `X / Square` | Game Options |
| `Y / Triangle` | Search |
| `Start` | Menu |
| `Select / Share` | Quick Settings |
| `LB/RB` | Switch Categories |
| `LT/RT` | Scroll Pages |
| `Xbox/PS Button` | Exit Console Mode |

### Game Library Shortcuts

| Shortcut | Action |
|----------|--------|
| `F11` | Toggle Console Mode |
| `Ctrl + F` | Search Games |
| `Ctrl + R` | Refresh Library |
| `Delete` | Hide Selected Game |
| `Enter` | Launch Selected Game |
| `Space` | Quick View Details |

### StreamForge Shortcuts

| Shortcut | Action |
|----------|--------|
| `F10` | Save Replay Buffer |
| `F9` | Toggle Recording |
| `Ctrl + Shift + S` | Go Live / End Stream |
| `Ctrl + M` | Mute Microphone |
| `Ctrl + Shift + M` | Mute Desktop Audio |

---

## 💡 Quick Tips

1. **Let the services work** - They're designed to be hands-off. Don't disable them unless troubleshooting.

2. **Use presets** - The optimization presets (Competitive, Immersive, etc.) are well-tested starting points.

3. **Check temperatures** - If performance drops during long sessions, check Thermal Guard for overheating.

4. **Keep shaders cached** - Don't clear your shader cache unless troubleshooting - it prevents stutter.

5. **Use Console Mode** - It's not just for controllers! It's great for a focused, distraction-free gaming experience.

6. **Set up Replay Buffer** - You never know when you'll pull off something amazing. Keep it running!

7. **Update regularly** - Aegis updates bring new optimizations and game-specific fixes.

---

## 📞 Getting Help

- **In-App Help:** Press `F1` in any Aegis app
- **Community Discord:** [Join our Discord server]
- **Documentation:** This guide and online wiki
- **Support Email:** Available to licensed users

---

*Aegis OS Gamer Edition - Play Without Limits* 🎮
