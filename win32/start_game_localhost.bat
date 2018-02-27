@echo off
cd ..
:restart
rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PPYTHON_PATH=<PPYTHON_PATH

echo ===============================
echo Starting Toontown Infinite...
echo ppython: %PPYTHON_PATH%
echo ===============================

%PPYTHON_PATH% -m toontown.toonbase.ClientStart
pause
goto restart
