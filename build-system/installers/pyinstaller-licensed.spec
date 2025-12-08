# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for Aegis OS Licensed Installer
Creates a standalone Windows executable with RSA license validation

Build command: pyinstaller pyinstaller-licensed.spec
Output: dist/AegisInstallerLicensed.exe

Requirements:
- Python 3.11+
- PyInstaller
- cryptography (for RSA license validation)
"""

import os
from datetime import datetime

block_cipher = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(SPECPATH))
RESOURCES_DIR = os.path.join(SCRIPT_DIR, 'resources')

icon_path = os.path.join(RESOURCES_DIR, 'aegis-icon.ico')
if not os.path.exists(icon_path):
    icon_path = None

data_files = []

public_key_path = os.path.join(RESOURCES_DIR, 'aegis-public-key.pem')
if os.path.exists(public_key_path):
    data_files.append((public_key_path, 'resources'))

a = Analysis(
    ['aegis-installer-licensed.py'],
    pathex=[SCRIPT_DIR],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'hashlib',
        'threading',
        'webbrowser',
        'pathlib',
        'time',
        'json',
        'base64',
        'shutil',
        'ctypes',
        'string',
        'datetime',
        'cryptography',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.hashes',
        'cryptography.hazmat.primitives.serialization',
        'cryptography.hazmat.primitives.asymmetric',
        'cryptography.hazmat.primitives.asymmetric.padding',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.default_backend',
        'cryptography.exceptions',
    ],
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
        'email',
        'http.server',
        'logging',
        'unittest',
        'pydoc',
        'doctest',
        'optparse',
        'pickle',
        'sqlite3',
        'xml.etree',
        'xml.dom',
        'xml.sax',
        'asyncio',
        'concurrent',
        'multiprocessing',
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
    name='AegisInstallerLicensed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,
    icon=icon_path,
    version_info={
        'FileVersion': (2, 0, 0, 0),
        'ProductVersion': (2, 0, 0, 0),
        'FileDescription': 'Aegis OS Licensed Installer',
        'InternalName': 'AegisInstallerLicensed',
        'OriginalFilename': 'AegisInstallerLicensed.exe',
        'ProductName': 'Aegis OS',
        'CompanyName': 'Aegis OS',
        'LegalCopyright': f'Copyright (c) {datetime.now().year} Aegis OS',
    } if False else None,
    manifest='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="2.0.0.0"
    processorArchitecture="*"
    name="AegisOS.InstallerLicensed"
    type="win32"
  />
  <description>Aegis OS Licensed Installer with RSA License Validation</description>
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
