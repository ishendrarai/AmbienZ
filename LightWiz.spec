# LightWiz.spec
# PyInstaller build spec for Light Wiz
# Usage: pyinstaller LightWiz.spec

import os, sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('assets', 'assets'),
    ],
    hiddenimports=(
        collect_submodules('sklearn') +
        collect_submodules('PySide6') +
        ['pystray', 'PIL', 'mss', 'cv2', 'numpy']
    ),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    name='LightWiz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No console window
    icon='assets/icon.ico', # Optional: provide an .ico file
)
