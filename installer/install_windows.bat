@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ============================================
echo  Installation - Gestion des Gardes ALOUIA
echo ============================================
echo.

set "INSTALL_DIR=%ProgramFiles%\CliniqueAlouiaGardes"
set "DESKTOP=%USERPROFILE%\Desktop"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

:: Demander le dossier d'installation
set /p "INSTALL_DIR= Dossier d'installation [%INSTALL_DIR%]: "
if "%INSTALL_DIR%"=="" set "INSTALL_DIR=%ProgramFiles%\CliniqueAlouiaGardes"

echo.
echo Installation dans : %INSTALL_DIR%
echo.

:: Créer le dossier
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copier les fichiers
xcopy /E /I /Y "%~dp0app" "%INSTALL_DIR%\app" >nul
copy /Y "%~dp0LancerGardes.bat" "%INSTALL_DIR%\" >nul
copy /Y "%~dp0LancerGardes.pyw" "%INSTALL_DIR%\" >nul 2>nul
if exist "%~dp0dist\CliniqueAlouiaGardes.exe" (
    copy /Y "%~dp0dist\CliniqueAlouiaGardes.exe" "%INSTALL_DIR%\" >nul
)

:: Raccourci bureau
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $s = $ws.CreateShortcut('%DESKTOP%\Gardes Clinique ALOUIA.lnk'); ^
   if (Test-Path '%INSTALL_DIR%\CliniqueAlouiaGardes.exe') { $s.TargetPath = '%INSTALL_DIR%\CliniqueAlouiaGardes.exe' } ^
   else { $s.TargetPath = '%INSTALL_DIR%\LancerGardes.bat' }; ^
   $s.WorkingDirectory = '%INSTALL_DIR%'; ^
   $s.Description = 'Gestion des gardes - Clinique ALOUIA'; ^
   $s.Save()"

:: Raccourci menu démarrer
if not exist "%START_MENU%\Clinique ALOUIA" mkdir "%START_MENU%\Clinique ALOUIA"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $s = $ws.CreateShortcut('%START_MENU%\Clinique ALOUIA\Gardes Clinique ALOUIA.lnk'); ^
   if (Test-Path '%INSTALL_DIR%\CliniqueAlouiaGardes.exe') { $s.TargetPath = '%INSTALL_DIR%\CliniqueAlouiaGardes.exe' } ^
   else { $s.TargetPath = '%INSTALL_DIR%\LancerGardes.bat' }; ^
   $s.WorkingDirectory = '%INSTALL_DIR%'; ^
   $s.Save()"

echo.
echo ============================================
echo  Installation terminée !
echo ============================================
echo.
echo Raccourci créé sur le bureau : "Gardes Clinique ALOUIA"
echo.
echo L'application peut aussi être copiée sur une clé USB.
echo Copiez tout le dossier : %INSTALL_DIR%
echo.
pause
