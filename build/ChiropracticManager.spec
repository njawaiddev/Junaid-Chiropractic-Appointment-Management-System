# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/naveedjawaid/Documents/M APP/src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/naveedjawaid/Documents/M APP/assets', 'assets'), ('/Users/naveedjawaid/Documents/M APP/src', 'src')],
    hiddenimports=['PIL', 'PIL._tkinter_finder', 'tkcalendar', 'babel.numbers', 'customtkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ChiropracticManager',
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
    icon=['/Users/naveedjawaid/Documents/M APP/assets/icon.ico'],
)
app = BUNDLE(
    exe,
    name='ChiropracticManager.app',
    icon='/Users/naveedjawaid/Documents/M APP/assets/icon.ico',
    bundle_identifier=None,
)
