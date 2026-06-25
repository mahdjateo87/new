@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Gestion des Gardes - Clinique ALOUIA

rem Lanceur double-clic : demarre l'application sans laisser de fenetre cmd ouverte.
rem Essaie pythonw (sans console), puis pyw / python / py en repli.

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw -m app.main
    exit /b
)

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw -m app.main
    exit /b
)

where python >nul 2>nul
if %errorlevel%==0 (
    start "" python -m app.main
    exit /b
)

where py >nul 2>nul
if %errorlevel%==0 (
    start "" py -m app.main
    exit /b
)

echo.
echo Python est introuvable sur ce PC.
echo Installez Python depuis https://www.python.org/downloads/
echo en cochant la case "Add Python to PATH", puis relancez ce fichier.
echo.
pause
