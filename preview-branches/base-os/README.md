# Aegis OS Base System (preview/base-os)

## What This Branch Contains

This is the **foundation layer** of Aegis OS - the core operating system that all other editions build upon. Contributors working on this branch are improving the base infrastructure that benefits ALL editions.

## Included Components

### Core Desktop Environment
```
usr/local/bin/
├── aegis-theme-manager        # GTK theme switching (Win10 light/dark)
├── aegis-wallpaper-manager    # Static wallpaper management
├── aegis-welcome              # First-run wizard
├── aegis-upgrade-prompt       # Shows upgrade options
├── aegis-license-manager      # License activation system
├── aegis-feature-gate         # Premium feature access control
└── aegis-fullscreen-toggle    # F11 fullscreen support
```

### System Configuration
```
etc/
├── aegis/
│   ├── tier.json              # Edition tier configuration
│   ├── tier-features.json     # Feature flags per tier
│   ├── public-key.pem         # RSA key for license verification
│   └── freemium-config.json   # Freemium-specific settings
├── lightdm/
│   └── lightdm.conf.d/
│       └── 50-aegis.conf      # Login screen configuration
├── xdg/
│   └── xfce4/                 # XFCE desktop configuration
│       └── xfconf/
│           └── xfce-perchannel-xml/
│               ├── xfce4-panel.xml         # Taskbar layout
│               ├── xfce4-keyboard-shortcuts.xml  # Windows-like shortcuts
│               └── xfwm4.xml               # Window manager settings
└── systemd/
    └── system/
        └── aegis-license-check.service  # License verification daemon
```

### GTK Themes
```
usr/share/themes/
├── Aegis-Win10/              # Light theme (Windows 10 style)
│   └── gtk-3.0/gtk.css
└── Aegis-Win10-Dark/         # Dark theme
    └── gtk-3.0/gtk.css
```

### Icons
```
usr/share/icons/
└── Aegis-Win10/
    └── index.theme           # Icon theme definition
```

## What You Can Contribute

### Priority Areas
1. **Theme Improvements** - Better Windows 10 fidelity, new accent colors
2. **Welcome Wizard** - Better onboarding experience
3. **License System** - Security improvements, offline activation
4. **Keyboard Shortcuts** - More Windows-compatible shortcuts
5. **Desktop Defaults** - Better XFCE panel layout, default apps

### How to Contribute

1. Fork and clone the repository
2. Switch to this branch:
   ```bash
   git checkout preview/base-os
   ```
3. Make your changes
4. Test locally (run the scripts, check themes)
5. Submit a pull request to `preview/base-os`

### Testing Your Changes

```bash
# Test theme manager
python3 usr/local/bin/aegis-theme-manager --test

# Validate Python syntax
python3 -m py_compile usr/local/bin/aegis-welcome

# Check GTK CSS
gtk3-widget-factory  # Opens theme preview
```

## Files NOT in This Branch

This branch does NOT contain:
- Gaming tools (those are in `preview/gamer`)
- AI/ML tools (those are in `preview/aidev`)
- Website code (`aegis-promotional/`)
- Build system (only in `main`)
- Other edition overlays (basic, workplace, server, gamer-ai)

## Syncing with Main

Maintainers periodically sync shared components from `main`:
```bash
# This is done by maintainers only
git checkout preview/base-os
git merge main --no-commit
# Manually select only base-os relevant changes
git commit
```

## Package List

The base system includes these Arch packages (defined in `packages/base.txt` and `packages/freemium.txt`):

### Core System
- `base`, `linux`, `linux-firmware`
- `networkmanager`, `dhcpcd`
- `sudo`, `nano`, `vim`

### Desktop
- `xorg-server`, `xorg-xinit`
- `xfce4`, `xfce4-goodies`
- `lightdm`, `lightdm-gtk-greeter`

### Applications
- `firefox` - Web browser
- `libreoffice-still` - Office suite
- `vlc` - Media player
- `thunar` - File manager
- `file-roller` - Archive manager

### Wine (Windows Compatibility)
- `wine`, `wine-mono`, `wine-gecko`
- `winetricks`

### Audio
- `pipewire`, `pipewire-pulse`, `pipewire-alsa`
- `wireplumber`

## Questions?

- Open an issue with the `base-os` label
- Join [Discord #base-development](https://discord.gg/aegis-os)
