@echo off
cd ..

rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PPYTHON_PATH=<PPYTHON_PATH

echo ====================================
echo Starting Toontown Infinite Server...
echo ====================================

%PPYTHON_PATH% -m toontown.dedicated.DedicatedStart
pause
