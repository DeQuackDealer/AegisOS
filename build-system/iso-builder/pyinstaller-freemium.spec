# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Aegis OS ISO Builder - Freemium Edition
Builds a single-file executable with all resources embedded.
"""

import os
import sys
from pathlib import Path

block_cipher = None

# Get the directory containing this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect all resources from the resources folder
resources_dir = os.path.join(spec_dir, 'resources')
datas = []

if os.path.exists(resources_dir):
    for root, dirs, files in os.walk(resources_dir):
        for file in files:
            src_path = os.path.join(root, file)
            rel_dir = os.path.relpath(root, resources_dir)
            if rel_dir == '.':
                dst_dir = 'resources'
            else:
                dst_dir = os.path.join('resources', rel_dir)
            datas.append((src_path, dst_dir))

a = Analysis(
    ['aegis_builder_freemium.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        'json',
        'hashlib',
        'tempfile',
        'shutil',
        'subprocess',
        'struct',
        'lzma',
        'tarfile',
        'dataclasses',
        'typing',
        'pathlib',
        'datetime',
        'threading',
        'webbrowser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'cryptography',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AegisBuilderFreemium',
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
    version='version_info.txt',
    icon=os.path.join(resources_dir, 'icons', 'aegis-builder.ico') if os.path.exists(os.path.join(resources_dir, 'icons', 'aegis-builder.ico')) else None,
    manifest='aegis-builder.manifest',
    uac_admin=False,
)
