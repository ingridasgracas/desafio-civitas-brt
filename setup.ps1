# 🚀 Script de Inicialização Rápida - PowerShell
# Executa setup completo do pipeline BRT

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Pipeline BRT CIVITAS - Setup Rápido  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verifica Python
Write-Host "[1/7] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python não encontrado!" -ForegroundColor Red
    exit 1
}

# 2. Cria ambiente virtual
Write-Host "[2/7] Criando ambiente virtual..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "  ✓ Ambiente virtual criado" -ForegroundColor Green
} else {
    Write-Host "  ✓ Ambiente virtual já existe" -ForegroundColor Green
}

# 3. Ativa ambiente virtual
Write-Host "[3/7] Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "  ✓ Ambiente ativado" -ForegroundColor Green

# 4. Instala dependências
Write-Host "[4/7] Instalando dependências..." -ForegroundColor Yellow
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-Host "  ✓ Dependências instaladas" -ForegroundColor Green

# 5. Cria arquivo .env
Write-Host "[5/7] Configurando .env..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  ✓ Arquivo .env criado" -ForegroundColor Green
    Write-Host "  ⚠ Configure as variáveis em .env antes de executar!" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Arquivo .env já existe" -ForegroundColor Green
}

# 6. Cria diretórios
Write-Host "[6/7] Criando diretórios..." -ForegroundColor Yellow
$dirs = @("data\bronze", "data\silver", "data\gold", "logs", "config")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "  ✓ Diretórios criados" -ForegroundColor Green

# 7. Instala pacotes DBT
Write-Host "[7/7] Instalando pacotes DBT..." -ForegroundColor Yellow
Set-Location dbt_brt
dbt deps --quiet
Set-Location ..
Write-Host "  ✓ Pacotes DBT instalados" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ Setup Completo!                    " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure .env com suas credenciais GCP"
Write-Host "2. Inicie Prefect: docker-compose up -d"
Write-Host "3. Execute pipeline: python pipeline\brt_flow.py"
Write-Host ""
