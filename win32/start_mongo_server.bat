@echo off

title Toontown DB

:main
mongod.exe --port 7030
goto main