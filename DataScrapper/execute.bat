@echo off
setlocal enabledelayedexpansion

REM Verifica se os argumentos necessários foram passados
if "%~1"=="" (
    echo Usage: %~nx0 filename limit [-join]
    exit /b 1
)
if "%~2"=="" (
    echo Usage: %~nx0 filename limit [-join]
    exit /b 1
)

REM Diretórios
set "termos_dir=.\listas_termos\"
set "images_dir=.\images\"

REM Argumentos
set "filename=%termos_dir%%~1.txt"
set "limit=%~2"
set "junta=%~3"

REM Caminho do interpretador Python
set "PYTHON_EXEC=..\env_scrapper\Scripts\python.exe"

REM Inicializa o contador
set /a total_images_downloaded=0

REM Itera por cada linha do arquivo .txt
for /f "usebackq delims=" %%A in ("%filename%") do (
    set "search_term=%%A"
    echo => Baixando imagens para o termo: !search_term! com limite de %limit% imagens

    for /f %%F in ('dir /a-d /b "%images_dir%" 2^>nul ^| find /c /v ""') do set /a images_before=%%F
    set "prefix=!search_term: =_!"

    echo Motor: Bing
    %PYTHON_EXEC% .\google-images-download\bing_scraper.py --search "!search_term!" --limit %limit% --download --chromedriver ".\DataScrapper\chromedriver\chromedriver.exe" --flat_directory --prefix "bing_!prefix!"
    set "bing_status=!errorlevel!"

    echo Motor: Google
    %PYTHON_EXEC% .\google-images-download\google_scraper.py --search "!search_term!" --limit %limit% --download --chromedriver ".\DataScrapper\chromedriver\chromedriver.exe" --flat_directory --prefix "google_!prefix!"
    set "google_status=!errorlevel!"

    if "!bing_status!"=="0" (
        set "has_success=1"
    ) else if "!google_status!"=="0" (
        set "has_success=1"
    ) else (
        set "has_success=0"
    )

    if "!has_success!"=="1" (
        for /f %%F in ('dir /a-d /b "%images_dir%" 2^>nul ^| find /c /v ""') do set /a images_after=%%F
        set /a images_downloaded=images_after-images_before
        set /a total_images_downloaded+=images_downloaded
        echo Termo: "!search_term!" - Imagens baixadas: !images_downloaded!/%limit%
    ) else (
        echo Erro ao baixar imagens para o termo "!search_term!" em todos os motores.
    )
)

echo.
echo => Total de imagens baixadas com sucesso: %total_images_downloaded%

REM Verifica se o terceiro argumento é -join
if /i "%junta%"=="-join" (
    echo.
    echo => As imagens ja foram salvas diretamente em "%images_dir%"
)

endlocal
