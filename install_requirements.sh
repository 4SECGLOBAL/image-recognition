#!/bin/bash

set -e

# Função para verificar a versão do Google Chrome instalada
get_chrome_version() {
    if command -v google-chrome &> /dev/null; then
        google-chrome --version | grep -oP '\d+\.\d+\.\d+.\d+'
    elif command -v chromium &> /dev/null; then
        chromium --version | grep -oP '\d+\.\d+\.\d+.\d+'
    else
        echo "❌ Google Chrome ou Chromium não encontrado."
        exit 1
    fi
}

# Função para baixar e instalar o ChromeDriver correspondente
install_chromedriver() {
    local chrome_version=$1
    local chromedriver_version="chrome-for-testing-public/$chrome_version/linux64"
    local driver_zip="chromedriver-linux64.zip"
    local driver_url="https://storage.googleapis.com/$chromedriver_version/$driver_zip"

    echo "📥 Baixando ChromeDriver versão $chrome_version..."
    wget -q --show-progress "$driver_url" -O "$driver_zip"

    if [ ! -f "$driver_zip" ]; then
        echo "❌ Erro: Falha ao baixar o ChromeDriver."
        exit 1
    fi

    echo "📦 Extraindo ChromeDriver..."
    unzip -q "$driver_zip"
    chmod +x chromedriver-linux64/chromedriver
    sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
    rm -rf "$driver_zip" chromedriver-linux64

    echo "✅ ChromeDriver instalado com sucesso."
}

# Verifica se o Google Chrome está instalado
echo "🔍 Verificando instalação do Google Chrome..."
chrome_version=$(get_chrome_version)
echo "✅ Google Chrome versão $chrome_version detectado."

# Instala o ChromeDriver correspondente
install_chromedriver "$chrome_version"

# Função para criar o ambiente virtual e instalar dependências
create_venv_and_install() {
    local venv_name=$1
    local req_path=$2

    echo "------------------------------------------------------"
    echo "🛠️  Criando ambiente virtual: $venv_name"
    echo "------------------------------------------------------"

    python3 -m venv "$venv_name"
    if [ $? -ne 0 ]; then
        echo "❌ Falha ao criar o ambiente virtual: $venv_name"
        exit 1
    fi

    echo "✅ Ambiente '$venv_name' criado com sucesso."

    echo "📦 Instalando dependências de $req_path"
    source "$venv_name/bin/activate"
    pip install --upgrade pip
    pip install -r "$req_path"
    if [ $? -ne 0 ]; then
        echo "❌ Falha ao instalar dependências para $venv_name"
        deactivate
        exit 1
    fi

    echo "✅ Dependências instaladas com sucesso para $venv_name."
    deactivate
    echo "------------------------------------------------------"
    echo "$venv_name finalizado."
    echo "------------------------------------------------------"
    echo ""
}

# Setup dos ambientes
create_venv_and_install "env_model" "AutoAnotador/requirements.txt"
create_venv_and_install "env_scrapper" "DataScrapper/google-images-download/requirements.txt"
create_venv_and_install "env_limpeza" "Limpeza/requirements.txt"

echo "🎉 Todos os ambientes foram configurados com sucesso."
