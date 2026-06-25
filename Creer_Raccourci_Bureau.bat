@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Creation du raccourci bureau - Gardes ALOUIA

echo Creation du raccourci sur le bureau...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$d=[Environment]::GetFolderPath('Desktop'); $proj=(Get-Location).Path; $lnk=Join-Path $d 'Gardes Clinique ALOUIA.lnk'; $py=(Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source; if(-not $py){$py=(Get-Command pyw.exe -ErrorAction SilentlyContinue).Source}; if(-not $py){$py=(Get-Command python.exe -ErrorAction SilentlyContinue).Source}; if(-not $py){Write-Host 'ERREUR : Python est introuvable. Installez Python depuis python.org en cochant Add Python to PATH, puis relancez ce fichier.'; exit}; $w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut($lnk); $s.TargetPath=$py; $s.Arguments='-m app.main'; $s.WorkingDirectory=$proj; $s.IconLocation=$py; $s.Description='Gestion des gardes - Clinique ALOUIA'; $s.Save(); Write-Host ('OK - Raccourci cree : ' + $lnk)"

echo.
echo Si le message ci-dessus indique OK, le raccourci
echo "Gardes Clinique ALOUIA" se trouve maintenant sur votre bureau.
echo.
pause
