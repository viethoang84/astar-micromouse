@echo off
echo Dang build A* algorithm...
g++ -std=c++11 -O2 -Wall -o astar.exe astar.cpp
if errorlevel 1 goto failed
echo Build thanh cong: astar.exe
echo Gio chay giao dien: python ..\ui.py
pause
exit /b 0

:failed
echo Build THAT BAI! Hay cai g++ truoc (MinGW hoac MSYS2).
pause
exit /b 1
