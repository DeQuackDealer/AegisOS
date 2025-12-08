# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for Aegis OS Freemium Installer
Creates a standalone Windows executable (.exe)

Build command: pyinstaller pyinstaller-freemium.spec
Output: dist/AegisInstallerFreemium.exe

This spec file includes:
- All necessary Python dependencies bundled
- Hidden imports for SSL/cryptography backends
- Windows version info embedded (from version_info.txt)
- DPI awareness manifest
- Single-file (onefile) mode
- manifest.json for checksums
- Custom icon
"""

import os
import sys

block_cipher = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(SPECPATH))
RESOURCES_DIR = os.path.join(SCRIPT_DIR, 'resources')
KEYS_DIR = os.path.join(SCRIPT_DIR, 'keys')

icon_path = os.path.join(RESOURCES_DIR, 'aegis-icon.ico')
if not os.path.exists(icon_path):
    icon_path = None

version_file = os.path.join(SCRIPT_DIR, 'version_info.txt')
if not os.path.exists(version_file):
    version_file = None

data_files = []

manifest_path = os.path.join(SCRIPT_DIR, 'manifest.json')
if os.path.exists(manifest_path):
    data_files.append((manifest_path, '.'))

ssl_hiddenimports = [
    'ssl',
    '_ssl',
    '_hashlib',
    'hashlib',
]

crypto_hiddenimports = [
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat',
    'cryptography.hazmat.backends',
    'cryptography.hazmat.backends.openssl',
    'cryptography.hazmat.backends.openssl.backend',
    'cryptography.hazmat.bindings',
    'cryptography.hazmat.bindings.openssl',
    'cryptography.hazmat.bindings.openssl.binding',
    'cryptography.hazmat.bindings._openssl',
    'cryptography.hazmat.bindings._rust',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.hashes',
    'cryptography.hazmat.primitives.kdf',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    'cryptography.hazmat.primitives.ciphers',
    'cryptography.hazmat.primitives.ciphers.algorithms',
    'cryptography.hazmat.primitives.ciphers.modes',
    'cryptography.hazmat.primitives.serialization',
    'cryptography.hazmat.primitives.serialization.pkcs7',
    'cryptography.hazmat.primitives.serialization.pkcs12',
    'cryptography.hazmat.primitives.asymmetric',
    'cryptography.hazmat.primitives.asymmetric.rsa',
    'cryptography.hazmat.primitives.asymmetric.dsa',
    'cryptography.hazmat.primitives.asymmetric.ec',
    'cryptography.hazmat.primitives.asymmetric.padding',
    'cryptography.hazmat.primitives.asymmetric.utils',
    'cryptography.hazmat.primitives.asymmetric.types',
    'cryptography.exceptions',
    'cryptography.x509',
    'cryptography.x509.oid',
    'cryptography.x509.extensions',
]

cffi_hiddenimports = [
    'cffi',
    '_cffi_backend',
]

app_hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinter.font',
    'threading',
    'webbrowser',
    'pathlib',
    'time',
    'json',
    'shutil',
    'ctypes',
    'ctypes.wintypes',
    'string',
    'os',
    'sys',
    'platform',
    'subprocess',
    'urllib',
    'urllib.request',
    'urllib.error',
    'urllib.parse',
    'tempfile',
    'base64',
    're',
    'datetime',
    'collections',
    'functools',
    'typing',
    'enum',
    'struct',
    'binascii',
]

all_hiddenimports = (
    ssl_hiddenimports +
    crypto_hiddenimports +
    cffi_hiddenimports +
    app_hiddenimports
)

a = Analysis(
    ['aegis-installer-freemium.py'],
    pathex=[SCRIPT_DIR],
    binaries=[],
    datas=data_files,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'tensorflow',
        'torch',
        'sklearn',
        'notebook',
        'IPython',
        'pytest',
        'sphinx',
        'docutils',
        'babel',
        'jinja2',
        'flask',
        'django',
        'setuptools',
        'pip',
        'wheel',
        'pkg_resources',
        'pydoc',
        'doctest',
        'optparse',
        'asyncio',
        'concurrent',
        'multiprocessing',
        'xmlrpc',
        'test',
        'distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AegisInstallerFreemium',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'python*.dll',
        'api-ms-win-*.dll',
        'ucrtbase.dll',
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,
    icon=icon_path,
    version=version_file,
    manifest='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="2.0.0.0"
    processorArchitecture="*"
    name="AegisOS.InstallerFreemium"
    type="win32"
  />
  <description>Aegis OS Freemium Installer</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 11 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
      <!-- Windows 10 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
      <!-- Windows 8.1 -->
      <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/>
      <!-- Windows 8 -->
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/>
      <!-- Windows 7 -->
      <supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"/>
    </application>
  </compatibility>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/pm</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
      <longPathAware xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">true</longPathAware>
    </windowsSettings>
  </application>
</assembly>''',
)
