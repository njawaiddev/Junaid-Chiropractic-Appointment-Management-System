# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('Info.plist', '.'), ('src', 'src'), ('assets', 'assets')],
    hiddenimports=['PIL', 'PIL._tkinter_finder', 'tkcalendar', 'babel.numbers', 'customtkinter', 'Foundation', 'objc', 'AppKit', 'PyObjCTools', 'darkdetect', 'google_auth_oauthlib', 'google.auth.transport.requests'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['src/utils/macos_runtime.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChiropracticManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity='-',
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChiropracticManager',
)
app = BUNDLE(
    coll,
    name='ChiropracticManager.app',
    icon=None,
    bundle_identifier='com.naveedjawaid.chiropracticmanager',
)
