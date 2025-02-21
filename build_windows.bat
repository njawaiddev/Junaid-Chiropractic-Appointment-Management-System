@echo off
echo Cleaning previous builds...
rmdir /s /q build dist installer
mkdir installer

echo Building executable...
pyinstaller ChiropracticManager.spec --noconfirm --clean

echo Creating installer...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

echo Build complete! Installer is in the installer folder.
pause 