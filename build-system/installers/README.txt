================================================================
  AEGIS OS INSTALLER BUILD PACKAGE
================================================================

This folder contains everything needed to build the Aegis OS
Windows installers (.exe files).


QUICK START (Windows)
================================================================

1. Make sure Python 3.8+ is installed
   Download from: https://www.python.org/downloads/
   IMPORTANT: Check "Add Python to PATH" during installation!

2. Double-click: BUILD.bat

3. Wait for the build to complete (2-5 minutes)

4. Find your .exe files in the "dist" folder


WHAT'S IN THIS FOLDER
================================================================

BUILD.bat
    Double-click this to build the installers!
    (This is the only file you need to run)

build-all-installers.py
    The main build script (called by BUILD.bat)

aegis-installer-freemium.py
    Source code for the Freemium installer
    - Detects ISOs from USB drives and local folders
    - Downloads from Aegis servers if not found locally
    - No license required

aegis-installer-licensed.py
    Source code for the Licensed installer
    - Same features as Freemium installer
    - RSA-2048 digital signature verification
    - Validates license.json files before installation

aegis-installer-freemium.spec
aegis-installer-licensed.spec
    PyInstaller configuration files
    (Advanced users only - optional)

manifest.json
    List of all Aegis OS editions with SHA-256 checksums
    Used by installers for offline ISO verification

license.json.example
    Example license file format for customers

keys/
    RSA key management tools:
    - generate-keys.py: Create new RSA-2048 key pairs
    - sign-license.py: Sign license files for customers
    - aegis-public.pem: Public key (embedded in installers)

resources/
    Icon and Windows manifest files


OUTPUT FILES
================================================================

After building, you'll find these in the "dist" folder:

    AegisInstallerFreemium.exe  (~15 MB)
    AegisInstallerLicensed.exe  (~18 MB)

These are standalone executables that work on any Windows PC.
No Python or other software required to run them!


FOR CUSTOMERS
================================================================

Freemium Edition:
    1. Download AegisInstallerFreemium.exe
    2. Double-click to run
    3. Insert USB with ISO or let it download
    4. Follow the wizard

Licensed Editions (Basic, Gamer, AI Developer, etc.):
    1. Purchase a license from aegis-os.com
    2. Download your license.json file
    3. Download AegisInstallerLicensed.exe
    4. Place license.json in your home folder or USB drive
    5. Double-click installer and follow the wizard


TROUBLESHOOTING
================================================================

"Python is not installed or not in PATH"
    Install Python from python.org and check
    "Add Python to PATH" during installation.

"PyInstaller not found"
    The build script will install it automatically.
    If it fails, run: pip install pyinstaller

Build fails with errors:
    Make sure you have internet connection for first build.
    PyInstaller needs to download some files.

.exe files are flagged by antivirus:
    This is a false positive. PyInstaller-created executables
    are sometimes flagged. You can add an exception or
    sign the executables with a code signing certificate.


SUPPORT
================================================================

Website: https://aegis-os.com
Email:   support@aegis-os.com


================================================================
  (c) 2025 Aegis OS - All Rights Reserved
================================================================
