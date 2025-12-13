# Contributing to Aegis OS

Thank you for your interest in contributing to Aegis OS! This document provides guidelines for contributing to the open-source preview editions.

## Branch Structure

| Branch | Purpose | Status |
|--------|---------|--------|
| `main` | Production-ready code, protected | **Protected** |
| `preview/freemium` | Base edition with Wine/Proton | Open for contributions |
| `preview/gamer` | Gaming-focused edition | Open for contributions |
| `preview/aidev` | AI/ML development edition | Open for contributions |

## Getting Started

1. **Fork the repository** to your GitHub account
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/AegisOSRepo.git
   cd AegisOSRepo
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/DeQuackDealer/AegisOSRepo.git
   ```
4. **Checkout the preview branch** you want to contribute to:
   ```bash
   git checkout preview/freemium  # or preview/gamer, preview/aidev
   ```

## Contribution Workflow

### For Bug Fixes and Small Changes

1. Create a feature branch from the appropriate preview branch:
   ```bash
   git checkout preview/freemium
   git pull upstream preview/freemium
   git checkout -b fix/your-fix-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "fix: brief description of fix"
   ```

3. Push to your fork:
   ```bash
   git push origin fix/your-fix-name
   ```

4. Open a Pull Request targeting the **preview branch** (NOT main)

### For New Features

1. Open an Issue first describing the feature
2. Wait for approval from maintainers
3. Follow the same workflow as bug fixes

## Commit Message Format

Use conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add MangoHUD configuration tool
fix: resolve Wine prefix creation error
docs: update installation instructions
```

## Code Standards

### Shell Scripts
- Use `#!/bin/bash` shebang
- Quote all variables: `"$VAR"` not `$VAR`
- Use `shellcheck` to validate scripts
- Add comments for complex logic

### Python Scripts
- Follow PEP 8 style guide
- Use type hints where possible
- Include docstrings for functions
- Maximum line length: 100 characters

### Package Lists
- One package per line
- Add comments explaining non-obvious packages
- Keep alphabetically sorted within sections

## What NOT to Do

1. **Never push directly to `main`** - Always use Pull Requests
2. **Never push directly to protected branches** - Use feature branches
3. **Don't modify core build scripts** without approval
4. **Don't add proprietary software** - Keep it open source
5. **Don't remove existing functionality** without discussion
6. **Don't commit sensitive data** (API keys, passwords, etc.)

## Pull Request Guidelines

### Before Submitting

- [ ] Test your changes locally if possible
- [ ] Update documentation if needed
- [ ] Ensure no merge conflicts
- [ ] Follow commit message format
- [ ] Target the correct preview branch

### PR Title Format

```
[EDITION] Brief description
```

Examples:
- `[FREEMIUM] Add Firefox ESR as default browser`
- `[GAMER] Configure MangoHUD defaults`
- `[AIDEV] Add Jupyter notebook integration`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing Done
Describe how you tested the changes

## Related Issues
Fixes #123
```

## Edition-Specific Guidelines

### Freemium Edition (`preview/freemium`)
- Focus on core functionality and stability
- Wine/Proton basics for Windows app compatibility
- Keep lightweight - minimal bloat
- Target audience: New Linux users from Windows

### Gamer Edition (`preview/gamer`)
- Gaming performance optimizations
- Steam, Lutris, Heroic Games Launcher support
- MangoHUD, GameMode, gamepad support
- Proton-GE and Wine-GE configurations
- Target audience: PC gamers

### AI Developer Edition (`preview/aidev`)
- CUDA/ROCm GPU compute support
- Python ML/AI libraries
- Jupyter, VS Code integration
- Docker/container support
- Target audience: ML engineers and data scientists

## Getting Help

- **Questions**: Open a Discussion on GitHub
- **Bugs**: Open an Issue with the bug template
- **Features**: Open an Issue with the feature template

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers learn
- Focus on the code, not the person

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Aegis OS!
