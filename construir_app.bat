@echo off
setlocal
title Minas Numericas - construir app
cd /d "%~dp0"

echo ================================================
echo   Minas Numericas: crear la app (.exe)
echo ================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro Python. Instala Python 3.9+ desde python.org
    echo         y marca "Add Python to PATH" al instalar.
    goto fin
)

echo [1/4] Instalando pygame-ce y PyInstaller...
python -m pip install --upgrade pygame-ce pyinstaller
if errorlevel 1 goto error

echo.
echo [2/4] Construyendo MinasNumericas.exe (tarda 1-2 minutos)...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name MinasNumericas --icon icono.ico --add-data "icono.png;." main.py
if errorlevel 1 goto error

echo.
echo [3/4] Copiando el entregable...
if not exist "Entregable" mkdir "Entregable"
copy /Y "dist\MinasNumericas.exe" "Entregable\MinasNumericas.exe" >nul

echo.
echo [4/4] Instalando en esta computadora y creando accesos directos...
set "DESTINO=%LOCALAPPDATA%\Programs\MinasNumericas"
if not exist "%DESTINO%" mkdir "%DESTINO%"
copy /Y "dist\MinasNumericas.exe" "%DESTINO%\MinasNumericas.exe" >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$w = New-Object -ComObject WScript.Shell;" ^
  "$exe = Join-Path $env:LOCALAPPDATA 'Programs\MinasNumericas\MinasNumericas.exe';" ^
  "$destinos = @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'));" ^
  "foreach ($d in $destinos) { $s = $w.CreateShortcut((Join-Path $d 'Minas Numericas.lnk')); $s.TargetPath = $exe; $s.WorkingDirectory = (Split-Path $exe); $s.IconLocation = $exe + ',0'; $s.Description = 'Juego de 32 metodos numericos'; $s.Save() }"
if errorlevel 1 goto error

echo.
echo ================================================
echo   LISTO
echo   - Acceso directo "Minas Numericas" en tu escritorio y en el menu Inicio.
echo   - Para compartir: manda el archivo Entregable\MinasNumericas.exe
echo   - Partidas guardadas de cada persona: %%APPDATA%%\MinasNumericas
echo ================================================
goto fin

:error
echo.
echo [ERROR] Algo fallo. Revisa los mensajes de arriba.

:fin
echo.
pause
