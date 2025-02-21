@echo off
echo Building Chiropractic Manager v2.0.0...

rem Clean previous builds
echo Cleaning previous builds...
rmdir /s /q build dist

rem Create executable with PyInstaller
echo Creating executable with PyInstaller...
pyinstaller ChiropracticManager.spec

rem Create installer with Inno Setup
echo Creating installer with Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

echo Build complete! Installer is in the dist folder. 