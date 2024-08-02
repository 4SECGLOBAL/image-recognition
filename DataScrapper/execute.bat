@echo off
setlocal enabledelayedexpansion

rem Check if enough arguments are provided
if "%~1"=="" (
    echo Usage: %0 filename limit
    endlocal
    exit /b 1
)

if "%~2"=="" (
    echo Usage: %0 filename limit
    endlocal
    exit /b 1
)

rem Get the filename and limit from the command-line arguments
set "filename=%~1"
set "limit=%~2"

rem Loop through each line in the specified file
for /f "delims=" %%i in (%filename%) do (
    set search_term=%%i
    echo Running command for: !search_term! with limit %limit%
    .\venv\Scripts\python.exe .\google-images-download\bing_scraper.py --search "!search_term!" --limit %limit% --download --chromedriver .\chromedriver.exe
)

endlocal
pause
