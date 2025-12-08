# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Aegis OS ISO Builder - Licensed Edition
Builds a single-file executable with cryptography support for RSA license validation.
"""

import os
import sys
from pathlib import Path

block_cipher = None

spec_dir = os.path.dirname(os.path.abspath(SPEC))

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

CRYPTOGRAPHY_HIDDEN_IMPORTS = [
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat',
    'cryptography.hazmat.backends',
    'cryptography.hazmat.backends.openssl',
    'cryptography.hazmat.backends.openssl.backend',
    'cryptography.hazmat.backends.openssl.aead',
    'cryptography.hazmat.backends.openssl.ciphers',
    'cryptography.hazmat.backends.openssl.cmac',
    'cryptography.hazmat.backends.openssl.decode_asn1',
    'cryptography.hazmat.backends.openssl.dh',
    'cryptography.hazmat.backends.openssl.dsa',
    'cryptography.hazmat.backends.openssl.ec',
    'cryptography.hazmat.backends.openssl.ed448',
    'cryptography.hazmat.backends.openssl.ed25519',
    'cryptography.hazmat.backends.openssl.encode_asn1',
    'cryptography.hazmat.backends.openssl.hashes',
    'cryptography.hazmat.backends.openssl.hmac',
    'cryptography.hazmat.backends.openssl.poly1305',
    'cryptography.hazmat.backends.openssl.rsa',
    'cryptography.hazmat.backends.openssl.utils',
    'cryptography.hazmat.backends.openssl.x25519',
    'cryptography.hazmat.backends.openssl.x448',
    'cryptography.hazmat.backends.openssl.x509',
    'cryptography.hazmat.bindings',
    'cryptography.hazmat.bindings._rust',
    'cryptography.hazmat.bindings._rust.openssl',
    'cryptography.hazmat.bindings.openssl',
    'cryptography.hazmat.bindings.openssl._conditional',
    'cryptography.hazmat.bindings.openssl.binding',
    'cryptography.hazmat.decrepit',
    'cryptography.hazmat.decrepit.ciphers',
    'cryptography.hazmat.decrepit.ciphers.algorithms',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives._asymmetric',
    'cryptography.hazmat.primitives._cipheralgorithm',
    'cryptography.hazmat.primitives._serialization',
    'cryptography.hazmat.primitives.asymmetric',
    'cryptography.hazmat.primitives.asymmetric.dh',
    'cryptography.hazmat.primitives.asymmetric.dsa',
    'cryptography.hazmat.primitives.asymmetric.ec',
    'cryptography.hazmat.primitives.asymmetric.ed448',
    'cryptography.hazmat.primitives.asymmetric.ed25519',
    'cryptography.hazmat.primitives.asymmetric.padding',
    'cryptography.hazmat.primitives.asymmetric.rsa',
    'cryptography.hazmat.primitives.asymmetric.types',
    'cryptography.hazmat.primitives.asymmetric.utils',
    'cryptography.hazmat.primitives.asymmetric.x25519',
    'cryptography.hazmat.primitives.asymmetric.x448',
    'cryptography.hazmat.primitives.ciphers',
    'cryptography.hazmat.primitives.ciphers.aead',
    'cryptography.hazmat.primitives.ciphers.algorithms',
    'cryptography.hazmat.primitives.ciphers.base',
    'cryptography.hazmat.primitives.ciphers.modes',
    'cryptography.hazmat.primitives.cmac',
    'cryptography.hazmat.primitives.constant_time',
    'cryptography.hazmat.primitives.hashes',
    'cryptography.hazmat.primitives.hmac',
    'cryptography.hazmat.primitives.kdf',
    'cryptography.hazmat.primitives.kdf.concatkdf',
    'cryptography.hazmat.primitives.kdf.hkdf',
    'cryptography.hazmat.primitives.kdf.kbkdf',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    'cryptography.hazmat.primitives.kdf.scrypt',
    'cryptography.hazmat.primitives.kdf.x963kdf',
    'cryptography.hazmat.primitives.keywrap',
    'cryptography.hazmat.primitives.padding',
    'cryptography.hazmat.primitives.poly1305',
    'cryptography.hazmat.primitives.serialization',
    'cryptography.hazmat.primitives.serialization.base',
    'cryptography.hazmat.primitives.serialization.pkcs12',
    'cryptography.hazmat.primitives.serialization.pkcs7',
    'cryptography.hazmat.primitives.serialization.ssh',
    'cryptography.hazmat.primitives.twofactor',
    'cryptography.hazmat.primitives.twofactor.hotp',
    'cryptography.hazmat.primitives.twofactor.totp',
    'cryptography.utils',
    'cryptography.x509',
    'cryptography.x509.base',
    'cryptography.x509.certificate_transparency',
    'cryptography.x509.extensions',
    'cryptography.x509.general_name',
    'cryptography.x509.name',
    'cryptography.x509.oid',
    'cryptography.x509.verification',
    'cffi',
    '_cffi_backend',
]

a = Analysis(
    ['aegis_builder_licensed.py'],
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
        'base64',
    ] + CRYPTOGRAPHY_HIDDEN_IMPORTS,
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
    name='AegisBuilderLicensed',
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
