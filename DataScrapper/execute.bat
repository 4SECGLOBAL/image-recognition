@echo off
setlocal enabledelayedexpansion

rem Verifica se há todos os argumentos necessários passados
if "%~1"=="" (
    echo Usage: %0 filename limit [-join]
    endlocal
    exit /b 1
)

if "%~2"=="" (
    echo Usage: %0 filename limit [-join]
    endlocal
    exit /b 1
)

rem Obtém os dados de filename, limit e a flag de juntar a partir dos argumentos
set "filename=%~1"
set "limit=%~2"
set "junta=%~3"

rem Itera por cada linha no arquivo txt e realiza o scrap com cada termo de busca
for /f "delims=" %%i in (.\listas_termos\%filename%) do (
    set search_term=%%i
    echo Baixando imagens para o termo: !search_term! com limite de %limit% imagens
    .\venv\Scripts\python.exe .\google-images-download\bing_scraper.py --search "!search_term!" --limit %limit% --download --chromedriver .\chromedriver.exe  --output_directory .\images\%filename%
)

rem Diretório selecionado
set "current_dir=.\images\%filename%"
echo %current_dir%

rem Verifica se o terceiro argumento é '-join'
if /i "%junta%"=="-join" (

    rem Itera por todas as pastas dentro do diretório selecionado
    for /d %%d in ("%current_dir%\*") do (
        echo Processando pasta: %%d

        rem Move todos os arquivos de todas as pastas para o diretório superior
        move "%%d\*" "%current_dir%"

        rem Deleta as pastas
        rd /s /q "%%d"
    )
) else (
    echo Invalid argument: %junta%
    echo Usage: %0 filename limit [-join]
)

endlocal
pause
