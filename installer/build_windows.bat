@echo off
chcp 65001 >nul
echo Construction de l'application Windows...
echo.

cd /d "%~dp0.."

python -m pip install -r requirements.txt pyinstaller --quiet

pyinstaller --noconfirm --windowed --name CliniqueAlouiaGardes ^
  --add-data "app;app" ^
  app/main.py

if exist "dist\CliniqueAlouiaGardes.exe" (
    echo.
    echo Build reussi : dist\CliniqueAlouiaGardes.exe
    mkdir installer\dist 2>nul
    copy /Y dist\CliniqueAlouiaGardes.exe installer\dist\
    echo Copie dans installer\dist\
) else (
    echo Erreur lors du build.
)

pause
