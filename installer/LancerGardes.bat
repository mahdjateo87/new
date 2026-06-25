@echo off
cd /d "%~dp0"
if exist "CliniqueAlouiaGardes.exe" (
    start "" "CliniqueAlouiaGardes.exe"
) else if exist "app\main.py" (
    pythonw app\main.py
) else (
    pythonw main.py
)
