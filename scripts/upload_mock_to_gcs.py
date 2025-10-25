"""
Script para fazer upload dos dados mockados para GCS
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from google.cloud import storage

# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configurações
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')
CREDENTIALS_PATH = Path(__file__).parent.parent / 'config' / 'gcp-credentials.json'

# Configurar credenciais
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(CREDENTIALS_PATH)


def upload_mock_data_to_gcs():
    """Faz upload dos dados mockados para GCS"""
    
    logger.info("="*60)
    logger.info("☁️ UPLOAD DE DADOS MOCKADOS PARA GCS")
    logger.info("="*60)
    
    # Encontrar arquivo CSV mais recente
    mock_dir = Path(__file__).parent.parent / 'data_output' / 'mock'
    
    if not mock_dir.exists():
        logger.error(f"❌ Diretório não encontrado: {mock_dir}")
        logger.info("Execute primeiro: python scripts/generate_mock_data.py")
        return False
    
    csv_files = list(mock_dir.glob('mock_brt_data_*.csv'))
    
    if not csv_files:
        logger.error(f"❌ Nenhum arquivo CSV encontrado em: {mock_dir}")
        logger.info("Execute primeiro: python scripts/generate_mock_data.py")
        return False
    
    # Pegar o mais recente
    csv_file = max(csv_files, key=lambda p: p.stat().st_mtime)
    
    logger.info(f"\n📁 Arquivo local: {csv_file.name}")
    logger.info(f"   Tamanho: {csv_file.stat().st_size / 1024:.2f} KB")
    
    try:
        # Conectar ao GCS
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        
        # Nome do arquivo no GCS
        gcs_path = f"brt-data/{csv_file.name}"
        blob = bucket.blob(gcs_path)
        
        # Upload
        logger.info(f"\n☁️ Fazendo upload para: gs://{BUCKET_NAME}/{gcs_path}")
        blob.upload_from_filename(str(csv_file))
        
        logger.success(f"\n✅ Upload concluído com sucesso!")
        logger.info(f"\n📊 URI do arquivo: gs://{BUCKET_NAME}/{gcs_path}")
        
        # Verificar
        blob.reload()
        logger.info(f"   Tamanho no GCS: {blob.size / 1024:.2f} KB")
        logger.info(f"   Tipo: {blob.content_type}")
        logger.info(f"   Criado em: {blob.time_created}")
        
        logger.info("\n" + "="*60)
        logger.success("🎉 DADOS MOCKADOS DISPONÍVEIS NO GCS!")
        logger.info("="*60)
        logger.info("\n📋 Próximos passos:")
        logger.info("  1. Execute: cd dbt_brt")
        logger.info("  2. Execute: dbt run")
        logger.info("  3. Execute: dbt test")
        logger.info("\n")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Erro ao fazer upload: {e}")
        return False


if __name__ == "__main__":
    upload_mock_data_to_gcs()
