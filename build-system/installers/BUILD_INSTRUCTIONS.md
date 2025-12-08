# Aegis OS Installer Build Instructions

Complete guide for building Windows .exe installers using PyInstaller.

## Quick Start - Running the Installer Directly

### Using the Batch Launcher (Recommended for End Users)

The easiest way to run the installer on Windows is to use the included batch launcher:

```cmd
AegisInstaller.bat
```

This will automatically:
1. Check if Python 3.11+ is installed
2. Download and install Python if needed (prompts user for permission)
3. Install required dependencies (cryptography)
4. Let you choose between Freemium or Licensed installer
5. Launch the installer GUI

**No admin rights required** for user-level Python installation.

### Using PowerShell (More Reliable)

For better error handling and progress display:

```powershell
.\AegisInstaller.ps1
```

PowerShell options:
```powershell
# Run Freemium installer directly (skip selection prompt)
.\AegisInstaller.ps1 -Freemium

# Run Licensed installer directly
.\AegisInstaller.ps1 -Licensed

# Skip Python check (if you know Python is installed)
.\AegisInstaller.ps1 -SkipPythonCheck

# Silent mode (auto-accept prompts)
.\AegisInstaller.ps1 -Silent -Freemium
```

### Setup Dependencies Only

To install dependencies without running the installer:

```cmd
setup-dependencies.bat
```

This installs:
- `cryptography` (for license verification)
- `pyinstaller` (for building executables)

## How the ISO System Works

### Offline-Only Installation

The Aegis installers are designed to work 100% offline:

1. **No Internet Downloads**: ISOs are never downloaded during installation
2. **Local Source Only**: ISOs must be present on local storage or USB drives
3. **Automatic Detection**: Installer scans common locations for ISO files

### ISO Search Locations

The installer searches for ISO files in this order:

1. **Same folder as installer** - `./aegis-freemium.iso`
2. **Subfolder** - `./iso/aegis-freemium.iso`
3. **User directories**:
   - `~/Downloads/`
   - `~/Desktop/`
   - `~/.aegis/iso/`
4. **USB drives** (Windows: `D:\`, `E:\`, etc.; Linux: `/media/`, `/mnt/`)
   - Root of USB drive
   - `aegis/` subfolder
   - `AegisOS/` subfolder

### ISO Naming Convention

The installer recognizes these filename patterns:
- `aegis-freemium.iso`
- `AegisOS-Freemium.iso`
- `aegis-os-freemium.iso`
- Any `.iso` file containing "aegis" or "freemium"

### Manifest File (Optional)

Include a `manifest.json` alongside ISOs for checksum verification:

```json
{
  "version": "2.0.0",
  "editions": {
    "freemium": {
      "filename": "aegis-freemium.iso",
      "sha256": "abc123...",
      "size_gb": 3.2
    },
    "basic": {
      "filename": "aegis-basic.iso",
      "sha256": "def456...",
      "size_gb": 3.5
    }
  }
}
```

## Prerequisites

### Required Software

1. **Python 3.11+**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: `python --version`

2. **PyInstaller**
   ```cmd
   pip install pyinstaller
   ```
   - Verify: `pyinstaller --version`

3. **Cryptography Library** (for licensed installer)
   ```cmd
   pip install cryptography
   ```

### Optional Software

4. **UPX** (for smaller executables)
   - Download from: https://upx.github.io/
   - Extract and add to PATH

5. **Windows SDK** (for code signing)
   - Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/

## Building the Installers

### Quick Build (Recommended)

Run the automated build script:

```cmd
cd build-system\installers
python build-windows.py
```

This will:
- Detect Python and PyInstaller
- Build both freemium and licensed installers
- Create output in `dist/` folder

### Manual Build

#### Freemium Installer

```cmd
cd build-system\installers
pyinstaller pyinstaller-freemium.spec
```

Output: `dist/AegisInstallerFreemium.exe`

#### Licensed Installer

```cmd
cd build-system\installers
pyinstaller pyinstaller-licensed.spec
```

Output: `dist/AegisInstallerLicensed.exe`

## Including Resources

### Icon File

Place your icon file at:
```
build-system/installers/resources/aegis-icon.ico
```

Requirements:
- Format: ICO (Windows Icon)
- Recommended sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
- Color depth: 32-bit with alpha transparency

### Windows Manifest

The manifest is embedded in the spec files and provides:
- UAC elevation settings
- Windows version compatibility
- DPI awareness

To modify, edit the `manifest` parameter in the spec files.

## Code Signing (Optional)

Code signing removes Windows SmartScreen warnings and verifies authenticity.

### Using SignTool (Windows SDK)

1. Obtain a code signing certificate (.pfx file)

2. Sign the executable:
   ```cmd
   signtool sign /f certificate.pfx /p PASSWORD /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist\AegisInstallerFreemium.exe
   ```

### Using build-windows.py

```cmd
python build-windows.py --sign --cert path\to\certificate.pfx --password YOUR_PASSWORD
```

## Testing the Built Executable

### Basic Testing

1. **Run the installer**
   - Double-click the .exe file
   - Verify the GUI appears correctly

2. **Test ISO detection**
   - Place a test ISO in the same folder
   - Verify it's detected automatically

3. **Test installation**
   - Select an installation folder
   - Verify files are copied correctly

### Testing on Clean System

For best results, test on a clean Windows VM:
- Windows 10/11 without Python installed
- Verify the exe runs standalone
- Check for missing DLL errors

## Troubleshooting

### Common Issues

#### "Python not found" Error

**Solution**: Add Python to PATH
```cmd
set PATH=%PATH%;C:\Python311;C:\Python311\Scripts
```

Or reinstall Python with "Add to PATH" checked.

#### "PyInstaller not found" Error

**Solution**: Install PyInstaller
```cmd
pip install pyinstaller
```

If pip isn't found:
```cmd
python -m pip install pyinstaller
```

#### "Failed to execute script" Error

**Possible causes**:
1. Missing dependencies - Check the spec file's `hiddenimports`
2. Icon file not found - Verify `resources/aegis-icon.ico` exists
3. Antivirus blocking - Add exception for the dist folder

**Debug mode**:
```cmd
pyinstaller --debug all pyinstaller-freemium.spec
```

#### Large Executable Size

**Solutions**:
1. Install UPX for compression
2. Check `excludes` in spec file
3. Use `--onefile` instead of `--onedir`

#### Windows Defender / SmartScreen Warning

**Solutions**:
1. Sign the executable with a code signing certificate
2. Right-click → Properties → Unblock
3. Users can click "More info" → "Run anyway"

#### Missing cryptography Module

**Solution**:
```cmd
pip install cryptography
```

For the licensed installer, this is required for RSA license validation.

#### tkinter Import Error

**Solution**: tkinter should be included with Python. If not:
- Reinstall Python with "tcl/tk and IDLE" option checked
- Or install manually: `pip install tk`

### Build Log

Check the build output for warnings:
```cmd
pyinstaller --log-level DEBUG pyinstaller-freemium.spec 2> build.log
```

## Output Files

After successful build:

```
build-system/installers/
├── dist/
│   ├── AegisInstallerFreemium.exe    # Freemium installer (~15-25 MB)
│   └── AegisInstallerLicensed.exe    # Licensed installer (~15-25 MB)
├── build/                             # Temporary build files (can delete)
└── *.spec                             # Spec files
```

## Build Customization

### Changing Version Information

Edit the spec file's `version` parameter or use a version file:

```python
# In spec file
exe = EXE(
    ...
    version='version_info.txt',
    ...
)
```

### Adding Data Files

To include additional files:

```python
# In spec file
datas=[
    ('resources/aegis-icon.ico', 'resources'),
    ('config.json', '.'),
]
```

### Changing Output Name

Modify the `name` parameter in the EXE block:

```python
exe = EXE(
    ...
    name='AegisOS-Installer-v2.0',
    ...
)
```

## Continuous Integration

For automated builds, see the GitHub Actions workflow at:
`.github/workflows/build-installers.yml`

## Packaging for Distribution

### Creating a Distribution Package

For distributing the installer to end users, create a package with all necessary files:

#### Option 1: Python Script Distribution (Smaller Download)

Include these files in a ZIP:
```
AegisOS-Installer/
├── AegisInstaller.bat           # Main launcher for users
├── AegisInstaller.ps1           # PowerShell alternative
├── setup-dependencies.bat       # Dependency installer
├── aegis-installer-freemium.py  # Freemium installer script
├── aegis-installer-licensed.py  # Licensed installer script
├── iso/                         # Optional: Include ISO files
│   └── aegis-freemium.iso
└── README.txt                   # Brief instructions
```

Users run `AegisInstaller.bat` and Python is installed automatically if needed.

**Pros**: Smaller download (~50 KB without ISO), auto-updates Python
**Cons**: Requires internet for first run if Python not installed

#### Option 2: Standalone Executable (No Dependencies)

Build with PyInstaller for a true standalone experience:

```cmd
cd build-system\installers
python build-windows.py
```

Creates a single .exe that includes Python and all dependencies.

Distribution package:
```
AegisOS-Installer/
├── AegisInstallerFreemium.exe   # Standalone executable (~20 MB)
├── iso/                         # Include ISO files
│   └── aegis-freemium.iso
└── README.txt
```

**Pros**: Works offline, no Python required, single click
**Cons**: Larger download, needs rebuild for updates

#### Option 3: USB Distribution Package

For offline distribution via USB drive:

```
USB_DRIVE/
├── AegisInstaller.bat           # Auto-runs Python installer
├── AegisInstaller.ps1
├── aegis-installer-freemium.py
├── aegis-installer-licensed.py
├── iso/
│   ├── aegis-freemium.iso
│   ├── aegis-basic.iso
│   └── manifest.json            # Checksums
├── python/
│   └── python-3.12.0-amd64.exe  # Bundled Python installer
└── autorun.inf                  # Optional: Auto-launch on insert
```

### Creating USB Distribution

1. Format USB drive (FAT32 or NTFS for large ISO files)
2. Copy all installer files
3. Download Python installer and place in `python/` folder
4. Create `autorun.inf` (optional):

```ini
[autorun]
label=Aegis OS Installer
icon=aegis-icon.ico
open=AegisInstaller.bat
action=Install Aegis OS
```

### License File Distribution

For licensed editions, include the license file:

```
AegisOS-Licensed/
├── AegisInstaller.bat
├── aegis-installer-licensed.py
├── license.json                 # Customer's license file
├── iso/
│   └── aegis-basic.iso
└── README.txt
```

The installer automatically detects `license.json` in the same folder.

## Support

For build issues:
- Check the troubleshooting section above
- Open an issue on the repository
- Contact: support@aegis-os.com
