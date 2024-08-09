@echo off
setlocal enabledelayedexpansion

rem Verifica se há todos os argumentos necessários passados
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

rem Obtem os dados de filename e limit a partir dos argumentos
set "filename=%~1"
set "limit=%~2"

rem Itera por cada linha no arquivo txt e realiza o scrap com cada termo de busca
for /f "delims=" %%i in (%filename%) do (
    set search_term=%%i
    echo Baixando imagens para o termo: !search_term! com limite de %limit% imagens
    .\venv\Scripts\python.exe .\google-images-download\bing_scraper.py --search "!search_term!" --limit %limit% --download --chromedriver .\chromedriver.exe
)

endlocal
pause
