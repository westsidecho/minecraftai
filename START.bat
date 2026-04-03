@echo off
title Minecraft AI Friends - Max & Luna
echo ==========================================
echo   Minecraft AI Friends - Max and Luna
echo ==========================================
echo.
echo   Make sure Minecraft is open and you did:
echo     Esc - Open to LAN - Start LAN World
echo.
echo   Starting Max and Luna...
echo   Voice chat: Hold [V] to talk, release to send
echo   Press [Q] in voice window to quit voice chat
echo.

cd /d "%~dp0"

:: Start the bots in background
start "Max and Luna" cmd /c "node main.js"

:: Wait for MindServer to start
echo   Waiting for bots to connect...
timeout /t 8 /nobreak >nul

:: Start voice listener
echo   Starting voice chat...
echo.
python voice_listener.py 2>nul || python3 voice_listener.py 2>nul

echo.
echo   Voice chat closed.
echo   To stop Max and Luna, close the other window too.
pause >nul
