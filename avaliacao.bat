@echo off
setlocal enabledelayedexpansion

REM Ativar o ambiente virtual
call env_model\Scripts\activate.bat

REM Obter argumentos
set "data_yaml=%~1"
set "model_path=%~2"
set "test_path=%~3"
set "confidence=%~4"
set "device=%~5"
set "save_json=%~6"

echo.
echo 🚀 Iniciando processo completo de avaliação...
echo 📄 YAML do dataset: %data_yaml%
echo 📸 Modelo: %model_path%
echo 📏 Imagens de validação: %test_path%
if not "%confidence%"=="" echo 🔍 Confiança: %confidence%
if not "%device%"=="" echo 💻 Dispositivo: %device%
if not "%save_json%"=="" echo 💾 JSON: %save_json%
echo.

echo ✍️ => AUTO-ANOTAÇÃO
REM Descomente a linha abaixo se desejar realizar a auto-anotação
REM python AutoAnotador\annotator.py %test_path%\images\ --det_model %model_path% --draw

if errorlevel 1 (
    echo ❌ Erro ao executar o script de auto-anotação.
    goto :EOF
) else (
    echo ✅ Auto-anotação concluída e salva em: %test_path%\images_auto_annotate_labels
)

echo.
echo 🔍 => VALIDAÇÃO YOLO NO CONJUNTO DE TESTE
set "yolo_cmd=yolo detect val data=%data_yaml% model=%model_path% split=test plots=True project=Avaliador\validacao"

if not "%confidence%"=="" set "yolo_cmd=!yolo_cmd! conf=%confidence%"
if not "%device%"=="" set "yolo_cmd=!yolo_cmd! device=%device%"
if not "%save_json%"=="" set "yolo_cmd=!yolo_cmd! save_json=%save_json%"

call !yolo_cmd!

if errorlevel 1 (
    echo ❌ Erro ao executar a validação YOLO.
    goto :EOF
) else (
    echo ✅ Validação concluída com sucesso e salva em: Avaliador\validacao
)

echo.
echo 🔍 => VALIDAÇÃO DE ASSERTIVIDADE NO CONJUNTO DE TESTE
python Avaliador\image_assertivity.py %test_path%\labels\ %test_path%\images_auto_annotate_labels --yaml_path %data_yaml% --check_fp True --save True

if errorlevel 1 (
    echo ❌ Erro ao executar a validação de assertividade.
    goto :EOF
) else (
    echo ✅ Validação de assertividade concluída com sucesso
)

echo.
echo 🏁 Avaliação completa finalizada.
endlocal
