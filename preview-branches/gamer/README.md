# Aegis OS - Gamer Tools

This branch contains gaming-focused tools for Aegis OS Gamer Edition.

## What's Included

### Gaming Launchers & Managers
| Tool | Description |
|------|-------------|
| `aegis-game-launcher` | Unified game launcher with upscaler injection |
| `aegis-game-center` | Central hub for all game libraries |
| `aegis-wine-optimizer` | Wine prefix management and optimization |
| `aegis-performance-tuner` | System performance optimization |

### Streaming & Recording
| Tool | Description |
|------|-------------|
| `aegis-stream` | Live streaming to Twitch/YouTube |
| `aegis-stream-deck` | Stream deck controller interface |
| `aegis-wallpaper-engine` | Animated desktop wallpapers |

### AI Upscaling
| Tool | Description |
|------|-------------|
| `aegis-upscaler` | Real-time AI upscaling (2x/4x/8x) |
| `aegis-render-orchestrator` | Multi-GPU render management |

### Hardware & Performance
| Tool | Description |
|------|-------------|
| `aegis-gamer-performance` | CPU/GPU performance profiles |
| `aegis-audio-router` | Audio routing for streaming |
| `aegis-external-media-handler` | External game drive management |

## For Contributors

### Getting Started

1. Clone this branch:
   ```bash
   git clone -b preview/gamer https://github.com/DeQuackDealer/AegisOSRepo.git aegis-gamer
   cd aegis-gamer
   ```

2. Dependencies:
   - Python 3.8+
   - GTK3 (gi.repository)
   - MangoHUD, GameMode
   - Wine, Proton

### Testing

```bash
# Test a tool
python3 usr/local/bin/aegis-game-launcher

# Check syntax
python3 -m py_compile usr/local/bin/aegis-upscaler
```

### Key Features to Work On

- [ ] Add more game library integrations (GOG, Epic)
- [ ] Improve upscaler model selection
- [ ] Better controller mapping UI
- [ ] Per-game performance profiles

### Submitting Changes

1. Fork the repository
2. Create a feature branch from `preview/gamer`
3. Test with actual games if possible
4. Submit a Pull Request

## File Structure

```
usr/
  local/
    bin/           # Gaming tools
  share/
    applications/  # .desktop launchers
etc/
  aegis/           # Game configs, upscaler settings
  profile.d/       # Environment variables
  udev/rules.d/    # Controller rules
  systemd/         # Background services
```

## Performance Tips

- Enable GameMode for all games
- Use MangoHUD for FPS monitoring
- Configure upscaler per-game for best results

## Questions?

Open an issue: https://github.com/DeQuackDealer/AegisOS/issues

## License

See the main repository for license information.
