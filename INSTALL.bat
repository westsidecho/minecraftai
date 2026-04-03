@echo off
title Installing Minecraft AI Friends - Max & Luna
echo ==========================================
echo   Minecraft AI Friends - Full Installer
echo   Max and Luna will be your friends!
echo ==========================================
echo.

:: ========================================
:: 1. Node.js
:: ========================================
echo [1/4] Checking Node.js...
where node >nul 2>nul
if %errorlevel% equ 0 (
    echo   Node.js already installed:
    node --version
    goto :check_python
)

echo   Node.js not found. Downloading...
set NODE_URL=https://nodejs.org/dist/v22.15.0/node-v22.15.0-x64.msi
set NODE_INSTALLER=%TEMP%\nodejs_installer.msi
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%NODE_URL%' -OutFile '%NODE_INSTALLER%' }"
if not exist "%NODE_INSTALLER%" (
    echo   Download failed. Please check internet and try again.
    pause
    exit /b 1
)
echo   Installing Node.js...
msiexec /i "%NODE_INSTALLER%" /qn /norestart
timeout /t 5 /nobreak >nul
set "PATH=%ProgramFiles%\nodejs;%PATH%"
del "%NODE_INSTALLER%" 2>nul
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo   Node.js needs a restart. Please restart PC and run INSTALL.bat again.
    pause
    exit /b 1
)
echo   Node.js installed!

:: ========================================
:: 2. Python
:: ========================================
:check_python
echo.
echo [2/4] Checking Python...
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo   Python already installed:
    python --version
    goto :install_npm
)

echo   Python not found. Downloading...
set PYTHON_URL=https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe
set PYTHON_INSTALLER=%TEMP%\python_installer.exe
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' }"
if not exist "%PYTHON_INSTALLER%" (
    echo   Download failed. Please check internet and try again.
    pause
    exit /b 1
)
echo   Installing Python...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
timeout /t 5 /nobreak >nul
set "PATH=%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;%PATH%"
del "%PYTHON_INSTALLER%" 2>nul
echo   Python installed!

:: ========================================
:: 3. NPM packages (for bots)
:: ========================================
:install_npm
echo.
echo [3/4] Installing AI Friends (npm)...
cd /d "%~dp0"
call npm install
if %errorlevel% neq 0 (
    echo   npm install had errors. Trying again...
    call npm install --ignore-scripts
)

:: ========================================
:: 4. Python packages (for voice chat)
:: ========================================
echo.
echo [4/4] Installing Voice Chat (pip)...
pip install pyaudio keyboard requests "python-socketio[client]" 2>nul || python -m pip install pyaudio keyboard requests "python-socketio[client]" 2>nul

:: ========================================
:: 5. FFmpeg
:: ========================================
echo.
echo Checking FFmpeg (needed for bot voice)...
where ffplay >nul 2>nul
if %errorlevel% equ 0 (
    echo   FFmpeg already installed!
) else (
    echo   Installing FFmpeg...
    winget install Gyan.FFmpeg --accept-source-agreements --accept-package-agreements >nul 2>nul
    if %errorlevel% equ 0 (
        echo   FFmpeg installed!
    ) else (
        echo   Could not auto-install FFmpeg.
        echo   Please install manually: winget install Gyan.FFmpeg
        echo   Or download from https://www.gyan.dev/ffmpeg/builds/
    )
)

:: ========================================
:: Done!
:: ========================================
echo.
echo ==========================================
echo   Installation complete!
echo ==========================================
echo.
echo   How to play:
echo     1. Open Minecraft, load a world
echo     2. Esc - Open to LAN - Start LAN World
echo     3. Double-click START.bat
echo.
echo   Have fun with Max and Luna!
echo.
pause
