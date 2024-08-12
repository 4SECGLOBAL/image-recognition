@echo off
setlocal enabledelayedexpansion

rem Get the current directory
set "current_dir=%cd%"

rem Loop through all folders in the current directory
for /d %%d in (*) do (
    echo Processing folder: %%d

    rem Move all files from the folder to the parent directory
    move "%%d\*" "%current_dir%"

    rem Delete the folder after moving its contents
    rd /s /q "%%d"
)

echo All files moved and folders deleted.
pause
