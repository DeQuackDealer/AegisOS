# Aegis OS - Base OS Tools

This branch contains the core base OS tools for Aegis OS.

## What's Included

| Tool | Description |
|------|-------------|
| `aegis-theme-manager` | GTK theme switcher (Light/Dark modes) |
| `aegis-wallpaper-manager` | Desktop wallpaper manager |
| `aegis-welcome` | First-run welcome wizard |
| `aegis-license-manager` | License key management |
| `aegis-feature-gate` | Feature tier verification |
| `aegis-fullscreen-toggle` | Quick fullscreen mode toggle |

## Configuration Files

- `tier.json` - Edition tier configuration
- `tier-features.json` - Feature availability per tier
- `public-key.pem` - License verification key

## For Contributors

### Getting Started

1. Clone this branch:
   ```bash
   git clone -b preview/base-os https://github.com/DeQuackDealer/AegisOSRepo.git aegis-base
   cd aegis-base
   ```

2. Tools are Python scripts - test locally:
   ```bash
   python3 aegis-theme-manager
   ```

### Code Style

- Python 3.8+ compatible
- Use `tkinter` for GUI components
- Use `subprocess` for system commands
- Add `#!/usr/bin/env python3` shebang
- Include docstrings for functions

### Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a Pull Request to `preview/base-os`

### File Structure

```
usr/
  local/
    bin/           # Executable tools
  share/
    applications/  # .desktop files
    icons/         # Icon themes
    themes/        # GTK themes
etc/
  aegis/           # Configuration files
```

## Questions?

Open an issue on the main repository: https://github.com/DeQuackDealer/AegisOS

## License

See the main repository for license information.
