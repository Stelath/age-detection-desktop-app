# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

block_cipher = None

# Set pathex to include the current working directory (adjust if needed)
a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    # If you have an assets folder with images or other non-Python data, bundle it here.
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    # Add the runtime hook that sets up the model download path.
    runtime_hooks=['runtime_hook_set_deepface_path.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # Use windowed mode so no console pops up.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='AgeAnalyzer.app',
    icon=None,
    bundle_identifier=None,
)