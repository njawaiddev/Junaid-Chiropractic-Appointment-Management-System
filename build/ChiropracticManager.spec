# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('/Users/naveedjawaid/Documents/M APP/src', 'src'), ('/Users/naveedjawaid/Documents/M APP/assets', 'assets'), ('/Users/naveedjawaid/Documents/M APP/venv/Lib/site-packages/google_auth_oauthlib', 'google_auth_oauthlib'), ('/Users/naveedjawaid/Documents/M APP/venv/Lib/site-packages/oauthlib', 'oauthlib'), ('/Users/naveedjawaid/Documents/M APP/credentials.json', '.')]
binaries = []
hiddenimports = ['google_auth_oauthlib.flow', 'google.auth.transport.requests', 'google.oauth2.credentials', 'google_auth_oauthlib', 'google.auth', 'google.oauth2', 'google_auth_httplib2', 'googleapiclient', 'PIL._tkinter_finder', 'babel.numbers', 'google.auth.transport.requests', 'google.oauth2.credentials', 'google_auth_oauthlib.flow', 'requests_oauthlib', 'oauthlib', 'oauthlib.oauth2', 'google_auth_oauthlib.session', 'google_auth_oauthlib.helpers', 'google_auth_oauthlib.interactive']
tmp_ret = collect_all('google_auth_oauthlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('google_auth_httplib2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('googleapiclient')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('google.auth')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('google.oauth2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('oauthlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('requests_oauthlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['/Users/naveedjawaid/Documents/M APP/src/main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
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
