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

    REM Executa o script Python
    %PYTHON_EXEC% .\google-images-download\bing_scraper.py --search "!search_term!" --limit %limit% --download --chromedriver ".\DataScrapper\chromedriver\chromedriver.exe" -i "%filename%"

    REM Constrói nome de diretório
    set "search_dir=%images_dir%!search_term: =_!"

    if exist "!search_dir!" (
        for /f %%F in ('dir /a-d /b "!search_dir!" ^| find /c /v ""') do (
            set /a images_downloaded=%%F
            set /a total_images_downloaded+=images_downloaded
            echo Termo: "!search_term!" - Imagens baixadas: !images_downloaded!/%limit%
        )
    ) else (
        echo Erro: O diretório "!search_dir!" não foi encontrado.
    )
)

echo.
echo => Total de imagens baixadas com sucesso: %total_images_downloaded%

REM Verifica se o terceiro argumento é -join
if /i "%junta%"=="-join" (
    echo.
    echo => Unindo todas as imagens em um único diretório

    for /f "usebackq delims=" %%L in ("%filename%") do (
        set "line=%%L"
        set "current_dir=%images_dir%!line: =_!"

        if exist "!current_dir!" (
            echo Movendo arquivos de "!current_dir!" para "%images_dir%"
            move /Y "!current_dir!\*" "%images_dir%" >nul
            rmdir /S /Q "!current_dir!"
        ) else (
            echo Erro: O diretório "!current_dir!" não existe.
        )
    )
)

endlocal