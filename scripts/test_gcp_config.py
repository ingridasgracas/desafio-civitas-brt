"""
Script para testar configuração do GCP
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from google.cloud import storage, bigquery

# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configurações
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')
DATASET_NAME = os.getenv('BQ_DATASET')
CREDENTIALS_PATH = Path(__file__).parent.parent / 'config' / 'gcp-credentials.json'

# Configurar credenciais
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(CREDENTIALS_PATH)


def test_storage():
    """Testa acesso ao Cloud Storage"""
    logger.info("🪣 Testando Cloud Storage...")
    
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.get_bucket(BUCKET_NAME)
        
        logger.success(f"✅ Bucket acessível: gs://{bucket.name}")
        logger.info(f"   Localização: {bucket.location}")
        logger.info(f"   Storage Class: {bucket.storage_class}")
        
        # Testar upload
        blob = bucket.blob('test/connection_test.txt')
        blob.upload_from_string('Teste de conexão - Pipeline BRT CIVITAS')
        logger.success(f"✅ Upload de teste bem-sucedido!")
        
        # Testar download
        content = blob.download_as_text()
        logger.success(f"✅ Download de teste bem-sucedido!")
        
        # Limpar arquivo de teste
        blob.delete()
        logger.info("   Arquivo de teste removido")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar Storage: {e}")
        return False


def test_bigquery():
    """Testa acesso ao BigQuery"""
    logger.info("\n📊 Testando BigQuery...")
    
    try:
        bq_client = bigquery.Client(project=PROJECT_ID)
        dataset = bq_client.get_dataset(DATASET_NAME)
        
        logger.success(f"✅ Dataset acessível: {dataset.dataset_id}")
        logger.info(f"   Localização: {dataset.location}")
        logger.info(f"   Descrição: {dataset.description}")
        
        # Testar query
        query = """
            SELECT 
                'Teste de conexão' as mensagem,
                CURRENT_TIMESTAMP() as timestamp
        """
        
        query_job = bq_client.query(query)
        results = query_job.result()
        
        for row in results:
            logger.success(f"✅ Query executada: {row.mensagem} às {row.timestamp}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar BigQuery: {e}")
        return False


def main():
    """Função principal"""
    logger.info("="*60)
    logger.info("🧪 TESTE DE CONFIGURAÇÃO GCP")
    logger.info("="*60)
    logger.info(f"\nProjeto: {PROJECT_ID}")
    logger.info(f"Bucket: {BUCKET_NAME}")
    logger.info(f"Dataset: {DATASET_NAME}\n")
    
    # Verificar credenciais
    if not CREDENTIALS_PATH.exists():
        logger.error(f"❌ Credenciais não encontradas: {CREDENTIALS_PATH}")
        return
    
    logger.success(f"✅ Credenciais: {CREDENTIALS_PATH}\n")
    
    # Executar testes
    storage_ok = test_storage()
    bigquery_ok = test_bigquery()
    
    # Resultado
    logger.info("\n" + "="*60)
    if storage_ok and bigquery_ok:
        logger.success("🎉 TODOS OS TESTES PASSARAM!")
        logger.info("="*60)
        logger.info("\n✅ Configuração GCP está correta!")
        logger.info("\n📋 Próximo passo:")
        logger.info("   Inicie o Prefect Server: docker-compose up -d\n")
    else:
        logger.error("❌ ALGUNS TESTES FALHARAM")
        logger.info("="*60)
        logger.info("\nVerifique as permissões da Service Account.\n")


if __name__ == "__main__":
    main()
