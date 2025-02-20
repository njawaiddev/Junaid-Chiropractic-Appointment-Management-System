# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['google_auth_oauthlib.flow', 'google.auth.transport.requests', 'google.oauth2.credentials', 'google_auth_oauthlib', 'google.auth', 'google.oauth2', 'google_auth_httplib2', 'googleapiclient', 'PIL._tkinter_finder', 'babel.numbers']
hiddenimports += collect_submodules('google_auth_oauthlib')
hiddenimports += collect_submodules('google_auth_httplib2')
hiddenimports += collect_submodules('googleapiclient')
hiddenimports += collect_submodules('google.auth')
hiddenimports += collect_submodules('google.oauth2')


a = Analysis(
    ['/Users/naveedjawaid/Documents/M APP/src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/naveedjawaid/Documents/M APP/src', 'src'), ('/Users/naveedjawaid/Documents/M APP/assets', 'assets'), ('/Users/naveedjawaid/Documents/M APP/credentials.json', '.')],
    hiddenimports=hiddenimports,
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
    target_arch=None,
    codesign_identity=None,
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
    bundle_identifier=None,
)
