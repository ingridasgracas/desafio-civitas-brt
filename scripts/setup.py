"""
Script de Setup - Configuração inicial do projeto
Verifica dependências, cria recursos GCP e configura ambiente
"""

import os
import sys
import subprocess
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


def check_python_version():
    """Verifica versão do Python"""
    logger.info("Verificando versão do Python...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("Python 3.8+ é necessário")
        return False
    
    logger.success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
    return True


def check_docker():
    """Verifica se Docker está instalado e rodando"""
    logger.info("Verificando Docker...")
    
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        logger.success(f"Docker instalado: {result.stdout.strip()} ✓")
        
        # Verifica se está rodando
        subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            check=True
        )
        logger.success("Docker daemon está rodando ✓")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Docker não está instalado ou não está rodando")
        return False


def check_gcloud():
    """Verifica se gcloud CLI está instalado"""
    logger.info("Verificando gcloud CLI...")
    
    try:
        result = subprocess.run(
            ['gcloud', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        logger.success("gcloud CLI instalado ✓")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("gcloud CLI não encontrado (opcional)")
        return False


def check_env_file():
    """Verifica se .env existe"""
    logger.info("Verificando arquivo .env...")
    
    env_path = Path('.env')
    
    if not env_path.exists():
        logger.warning(".env não encontrado, criando a partir do template...")
        
        example_path = Path('.env.example')
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            logger.success(".env criado. Por favor, configure as variáveis!")
            return False
        else:
            logger.error(".env.example não encontrado")
            return False
    
    logger.success(".env encontrado ✓")
    return True


def check_gcp_credentials():
    """Verifica credenciais GCP"""
    logger.info("Verificando credenciais GCP...")
    
    cred_path = os.getenv('GCP_CREDENTIALS_PATH', './config/gcp-credentials.json')
    
    if not Path(cred_path).exists():
        logger.error(f"Arquivo de credenciais não encontrado: {cred_path}")
        logger.info("Por favor, baixe as credenciais do GCP e salve em config/gcp-credentials.json")
        return False
    
    logger.success("Credenciais GCP encontradas ✓")
    return True


def check_dependencies():
    """Verifica se dependências Python estão instaladas"""
    logger.info("Verificando dependências Python...")
    
    required_packages = [
        'prefect',
        'google-cloud-storage',
        'google-cloud-bigquery',
        'dbt-core',
        'dbt-bigquery',
        'pandas',
        'requests'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.warning(f"Pacotes faltando: {', '.join(missing)}")
        logger.info("Execute: pip install -r requirements.txt")
        return False
    
    logger.success("Todas as dependências instaladas ✓")
    return True


def create_directories():
    """Cria diretórios necessários"""
    logger.info("Criando diretórios...")
    
    dirs = [
        'data/bronze',
        'data/silver',
        'data/gold',
        'logs',
        'config'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    logger.success("Diretórios criados ✓")


def test_api_connection():
    """Testa conexão com API BRT"""
    logger.info("Testando conexão com API BRT...")
    
    try:
        import requests
        api_url = os.getenv('BRT_API_URL', 'https://jeap.rio.rj.gov.br/je-api/api/v2/gps')
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        logger.success("API BRT acessível ✓")
        return True
    except Exception as e:
        logger.warning(f"API BRT não acessível: {e}")
        logger.info("Isso pode ser temporário, continue mesmo assim")
        return False


def main():
    """Função principal de setup"""
    
    print("\n" + "="*60)
    print("🚀 SETUP - Pipeline BRT CIVITAS")
    print("="*60 + "\n")
    
    checks = [
        ("Python 3.8+", check_python_version),
        ("Docker", check_docker),
        ("Arquivo .env", check_env_file),
        ("Credenciais GCP", check_gcp_credentials),
        ("Dependências Python", check_dependencies),
    ]
    
    results = []
    
    for name, check_func in checks:
        result = check_func()
        results.append(result)
        print()
    
    # Checks opcionais
    check_gcloud()
    print()
    
    test_api_connection()
    print()
    
    create_directories()
    print()
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DO SETUP")
    print("="*60 + "\n")
    
    for (name, _), result in zip(checks, results):
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print()
    
    if all(results):
        print("✅ Setup completo! Você está pronto para executar o pipeline.")
        print("\nPróximos passos:")
        print("1. Configure as variáveis no arquivo .env")
        print("2. Inicie o Prefect: docker-compose up -d")
        print("3. Execute o pipeline: python pipeline/brt_flow.py")
    else:
        print("⚠️ Alguns itens precisam de atenção.")
        print("Por favor, resolva os problemas acima antes de continuar.")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
