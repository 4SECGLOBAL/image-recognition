@echo off
setlocal enabledelayedexpansion

REM Diretório onde as imagens serão salvas
set "images_dir=DataScrapper\images"

REM Argumentos obrigatórios
set "termo_busca=%~1"
set "limite=%~2"
set "min_larg=%~3"
set "min_alt=%~4"
set "max_larg=%~5"
set "max_alt=%~6"

REM Valores padrão
if "%min_larg%"=="" set "min_larg=100"
if "%min_alt%"=="" set "min_alt=100"
if "%max_larg%"=="" set "max_larg=1920"
if "%max_alt%"=="" set "max_alt=1080"

REM Caminho para o Python do ambiente virtual
set "PYTHON_EXEC=env_limpeza\Scripts\python.exe"

REM Verifica se o argumento --limpeza_visual foi passado
set "limpeza_visual_flag="
for %%a in (%*) do (
    if "%%a"=="--limpeza_visual" (
        set "limpeza_visual_flag=--limpeza_visual"
    )
)

echo.
echo 🚀 Iniciando processo completo de coleta e limpeza de imagens...
echo 🔍 Termo de busca: "%termo_busca%"
echo 📸 Limite de imagens: %limite%
echo 📏 Filtros de tamanho → mín: %min_larg%x%min_alt%, máx: %max_larg%x%max_alt%
if defined limpeza_visual_flag echo 🖼️  Modo de limpeza visual ativado!

echo.
echo 📥 => COLETA DE IMAGENS
pushd DataScrapper
call execute.bat %termo_busca% %limite% -join
popd

echo.
echo 🧹 => LIMPEZA DO DATASET
call %PYTHON_EXEC% Limpeza\limpeza_dataset.py %images_dir% ^
    --min_width %min_larg% ^
    --min_height %min_alt% ^
    --max_width %max_larg% ^
    --max_height %max_alt% ^
    %limpeza_visual_flag%

if errorlevel 1 (
    echo ❌ Erro ao executar o script de limpeza.
    exit /b 1
) else (
    echo 🧾 Imagens finais salvas em: %images_dir%
)

echo.
echo 🏁 Processo completo finalizado.
endlocal
