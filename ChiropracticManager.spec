# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src'), ('assets', 'assets')],
    hiddenimports=['PIL', 'PIL._tkinter_finder', 'tkcalendar', 'babel.numbers', 'customtkinter', 'google.api_core', 'google.auth', 'google.oauth2', 'google_auth_oauthlib', 'google.auth.transport.requests'],
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
    icon=['assets/icon.ico'],
)
app = BUNDLE(
    exe,
    name='ChiropracticManager.app',
    icon='assets/icon.ico',
    bundle_identifier=None,
)
