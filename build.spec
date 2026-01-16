# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Google Photos Organiser.

This configuration creates a single-file Windows executable that bundles
all dependencies (Pillow, tqdm) and can run without Python installed.

To build:
    pyinstaller build.spec

The executable will be created in dist/photo-organiser.exe
"""

import sys
from pathlib import Path

# Application configuration
app_name = 'photo-organiser'
entry_point = 'src/photo_organiser/main.py'

# Analysis: Scan for dependencies and scripts
a = Analysis(
    [entry_point],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Ensure all photo_organiser modules are included
        'photo_organiser',
        'photo_organiser.main',
        'photo_organiser.extractor',
        'photo_organiser.metadata',
        'photo_organiser.organizer',
        'photo_organiser.config',
        # Pillow dependencies (image format support)
        'PIL._imaging',
        'PIL.Image',
        'PIL.ImageFile',
        'PIL.JpegImagePlugin',
        'PIL.PngImagePlugin',
        'PIL.GifImagePlugin',
        # tqdm for progress bars
        'tqdm',
        'tqdm.std',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test and development dependencies
        'pytest',
        'unittest',
        'test',
        # Exclude unused standard library modules to reduce size
        'tkinter',
        'pydoc',
        'doctest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ: Create Python archive
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# EXE: Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression to reduce executable size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console mode (not windowed)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Optional: Add icon file
    # icon='icon.ico',  # Uncomment and provide icon file if desired
)
