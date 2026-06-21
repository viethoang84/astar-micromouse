@echo off
g++ -std=c++11 -O2 -Wall -o astar.exe main.cpp
if %ERRORLEVEL% == 0 (
    echo Build successful: astar.exe
) else (
    echo Build FAILED
)
pause
