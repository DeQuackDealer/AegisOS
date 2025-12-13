# Aegis OS

**A commercial Linux distribution based on Arch Linux with 7 distinct editions**

[![Build Status](https://img.shields.io/badge/Build-GitHub%20Actions-blue)]()
[![License](https://img.shields.io/badge/Preview-Open%20Source-green)]()
[![Arch Linux](https://img.shields.io/badge/Based%20on-Arch%20Linux-1793D1)]()

---

## Overview

Aegis OS is a commercial Linux distribution offering a Windows 10-inspired experience with optimized gaming through Wine/Proton, AI-powered security, and over 50 custom utilities. Built on Arch Linux for rolling releases and cutting-edge software.

---

## Editions

| Edition | Price | Target Audience | Key Features |
|---------|-------|-----------------|--------------|
| **Freemium** | Free | New Linux users | 30-day trial, Wine/Proton basics |
| **Basic** | $69 | General users | Full productivity suite |
| **Workplace** | $49 | Business users | Office 365 compatibility, VPN |
| **Gamer** | $69 | PC gamers | Steam, Lutris, Proton-GE, MangoHUD |
| **AI Developer** | $89 | ML engineers | CUDA, PyTorch, JupyterLab |
| **Gamer+AI** | $129 | Power users | Gaming + ML workstation |
| **Server** | $129 | Enterprise | XDR security, Kubernetes |

---

## Open Source Preview Editions

We offer three open-source preview editions for community development:

### Available Branches

| Branch | Description | Documentation |
|--------|-------------|---------------|
| `preview/freemium` | Base edition with Wine/Proton | [Freemium Docs](docs/editions/freemium/README.md) |
| `preview/gamer` | Gaming-focused edition | [Gamer Docs](docs/editions/gamer/README.md) |
| `preview/aidev` | AI/ML development edition | [AI Dev Docs](docs/editions/aidev/README.md) |

---

## Getting Started

### For Users

1. Download the ISO from [Releases](https://github.com/DeQuackDealer/AegisOSRepo/releases)
2. Create bootable USB with [Rufus](https://rufus.ie/) or `dd`
3. Boot and install

### For Contributors

1. Fork this repository
2. Clone and checkout a preview branch:
   ```bash
   git clone https://github.com/YOUR_USERNAME/AegisOSRepo.git
   cd AegisOSRepo
   git checkout preview/freemium  # or preview/gamer, preview/aidev
   ```
3. Read [CONTRIBUTING.md](CONTRIBUTING.md)
4. Make changes and submit a Pull Request

---

## Building ISOs

### Using GitHub Actions (Recommended)

1. Go to **Actions** tab
2. Select **Build Aegis OS ISOs**
3. Click **Run workflow**
4. Choose edition and wait for build
5. Download ISO from artifacts

### Manual Build (Arch Linux)

```bash
# Install archiso
sudo pacman -S archiso

# Build
cd build-system
sudo python build-aegis.py --edition freemium --real-build
```

---

## Project Structure

```
AegisOSRepo/
├── .github/
│   ├── workflows/           # GitHub Actions
│   ├── ISSUE_TEMPLATE/      # Bug/feature templates
│   └── CODEOWNERS           # Code ownership
├── aegis-promotional/       # Marketing website
├── build-system/
│   ├── archiso/             # ISO build files
│   │   ├── packages/        # Package lists per edition
│   │   ├── airootfs/        # Root filesystem overlay
│   │   └── profiledef.sh    # ISO profile
│   ├── installers/          # Windows-style media tool
│   └── build-aegis.py       # Build orchestration
├── docs/
│   ├── editions/            # Edition documentation
│   ├── BRANCH_PROTECTION.md # Security rules
│   └── CREATING_BRANCHES.md # Branch setup guide
├── CONTRIBUTING.md          # Contribution guidelines
└── README.md                # This file
```

---

## Contributing

We welcome contributions to the preview editions! 

**Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting.**

### Quick Start

1. Fork the repo
2. Create feature branch from preview branch
3. Make changes
4. Submit PR targeting the preview branch (**not main**)

### What You Can Contribute

- Package additions
- Bug fixes
- Documentation improvements
- Custom tools and scripts
- Performance optimizations
- Translations

---

## Branch Protection

- **`main`** - Protected, requires 2 approvals
- **`preview/*`** - Protected, requires 1 approval
- No force pushes allowed
- All PRs require review

See [docs/BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md) for setup instructions.

---

## Technology Stack

- **Base OS:** Arch Linux (rolling release)
- **Desktop:** XFCE4 with Windows 10 theme
- **Gaming:** Wine, Proton, Steam, Lutris
- **AI/ML:** CUDA, PyTorch, TensorFlow
- **Build System:** archiso, mkarchiso
- **Website:** Flask, Python
- **Payments:** Stripe integration

---

## Links

- [Website](https://aegis-os.com) (coming soon)
- [Issue Tracker](https://github.com/DeQuackDealer/AegisOSRepo/issues)
- [Discussions](https://github.com/DeQuackDealer/AegisOSRepo/discussions)
- [Contributing Guide](CONTRIBUTING.md)

---

## License

- **Preview editions** (preview/* branches): Open Source
- **Commercial editions**: Proprietary

See LICENSE file for details.

---

## Acknowledgments

- Arch Linux community
- archiso developers
- Wine and Proton projects
- SteamOS for inspiration
- All our contributors!

---

**Built with passion for the Linux community**
