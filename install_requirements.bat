@echo off
setlocal

:: Function-like section for creating venv and installing requirements
call :create_venv_and_install env_model AutoAnotador\requirements.txt
if errorlevel 1 exit /b 1

call :create_venv_and_install env_scrapper DataScrapper\google-images-download\requirements.txt
if errorlevel 1 exit /b 1

call :create_venv_and_install env_scrapper limpezavenv Limpeza\requirements.txt
if errorlevel 1 exit /b 1

:: Install ChromeDriver
call :install_chromedriver

echo.
echo 🎉 All environments set up successfully.
exit /b 0

:create_venv_and_install
set "VENV_NAME=%~1"
set "REQ_PATH=%~2"

echo ------------------------------------------------------
echo Creating virtual environment: %VENV_NAME%
echo ------------------------------------------------------

python -m virtualenv %VENV_NAME%
if errorlevel 1 (
    echo ❌ Failed to create virtual environment: %VENV_NAME%
    exit /b 1
)

echo ✅ Virtual environment "%VENV_NAME%" created successfully.

echo ------------------------------------------------------
echo Installing requirements from %REQ_PATH%
echo ------------------------------------------------------

call %VENV_NAME%\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment: %VENV_NAME%
    exit /b 1
)

pip install --upgrade pip
pip install -r %REQ_PATH%
if errorlevel 1 (
    echo ❌ Failed to install requirements for %VENV_NAME% from %REQ_PATH%
    call deactivate
    exit /b 1
)

echo ✅ Requirements installed successfully for %VENV_NAME%.
call deactivate

echo ------------------------------------------------------
echo %VENV_NAME% setup completed.
echo ------------------------------------------------------
echo.
exit /b 0

:install_chromedriver
echo ------------------------------------------------------
echo Installing ChromeDriver
echo ------------------------------------------------------

:: Check if Google Chrome is installed
where /q chrome
if errorlevel 1 (
    echo ❌ Google Chrome is not installed. Please install Google Chrome first.
    exit /b 1
)

:: Get Chrome version
for /f "tokens=3" %%a in ('reg query "HKCU\Software\Google\Chrome\BLBeacon" /v version 2^>nul') do set "CHROME_VERSION=%%a"
if not defined CHROME_VERSION (
    echo ❌ Failed to retrieve Chrome version.
    exit /b 1
)

:: Determine ChromeDriver version
set "CHROMEDRIVER_VERSION=chromedriver_win32\%CHROME_VERSION%"

:: Download ChromeDriver
echo 📥 Downloading ChromeDriver version %CHROME_VERSION%...
mkdir "%~dp0DataScrapper\chromedriver"
cd /d "%~dp0DataScrapper\chromedriver"
curl -LO "https://chromedriver.storage.googleapis.com/%CHROME_VERSION%/chromedriver_win32.zip"
if errorlevel 1 (
    echo ❌ Failed to download ChromeDriver.
    exit /b 1
)

:: Extract ChromeDriver
echo 📦 Extracting ChromeDriver...
tar -xf chromedriver_win32.zip
if errorlevel 1 (
    echo ❌ Failed to extract ChromeDriver.
    exit /b 1
)

:: Move ChromeDriver to a directory in PATH
move /y chromedriver.exe "%~dp0DataScrapper\chromedriver\chromedriver.exe"
if errorlevel 1 (
    echo ❌ Failed to move ChromeDriver to the specified directory.
    exit /b 1
)

:: Add ChromeDriver to PATH
setx PATH "%PATH%;%~dp0DataScrapper\chromedriver"
if errorlevel 1 (
    echo ❌ Failed to add ChromeDriver to PATH.
    exit /b 1
)

:: Output ChromeDriver path
echo ✅ ChromeDriver installed successfully at: "%~dp0DataScrapper\chromedriver\chromedriver.exe"
cd /d "%~dp0"
exit /b 0