@echo off

set mypath=%~dp0

call %mypath%\.venv\Scripts\activate.bat
cd %mypath%
python %mypath%\file.py
pause