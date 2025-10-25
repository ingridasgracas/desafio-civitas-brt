"""
Script Helper - Criar Recursos GCP
Automatiza a criação do bucket e dataset
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import storage, bigquery

# Cores
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def create_bucket(project_id, bucket_name, location='southamerica-east1'):
    """Cria bucket no Cloud Storage"""
    try:
        storage_client = storage.Client(project=project_id)
        
        # Verificar se já existe
        try:
            bucket = storage_client.get_bucket(bucket_name)
            print_info(f"Bucket '{bucket_name}' já existe")
            return True
        except:
            pass
        
        # Criar bucket
        print_info(f"Criando bucket '{bucket_name}' em {location}...")
        bucket = storage_client.create_bucket(
            bucket_name,
            location=location
        )
        print_success(f"Bucket '{bucket_name}' criado com sucesso!")
        return True
        
    except Exception as e:
        print_error(f"Erro ao criar bucket: {e}")
        return False

def create_dataset(project_id, dataset_id, location='southamerica-east1'):
    """Cria dataset no BigQuery"""
    try:
        bq_client = bigquery.Client(project=project_id)
        
        # Verificar se já existe
        try:
            dataset_ref = bq_client.dataset(dataset_id)
            bq_client.get_dataset(dataset_ref)
            print_info(f"Dataset '{dataset_id}' já existe")
            return True
        except:
            pass
        
        # Criar dataset
        print_info(f"Criando dataset '{dataset_id}' em {location}...")
        dataset_ref = bq_client.dataset(dataset_id)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        dataset = bq_client.create_dataset(dataset)
        print_success(f"Dataset '{dataset_id}' criado com sucesso!")
        return True
        
    except Exception as e:
        print_error(f"Erro ao criar dataset: {e}")
        return False

def main():
    print("\n" + "="*60)
    print(f"{BLUE}🚀 CRIAÇÃO DE RECURSOS GCP{RESET}")
    print("="*60 + "\n")
    
    # Carregar configurações
    load_dotenv()
    
    project_id = os.getenv('GCP_PROJECT_ID')
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    credentials_path = os.getenv('GCP_CREDENTIALS_PATH')
    dataset_id = os.getenv('BQ_DATASET')
    
    # Configurar credenciais
    if not Path(credentials_path).exists():
        print_error(f"Arquivo de credenciais não encontrado: {credentials_path}")
        print_info("Crie a Service Account primeiro (veja SETUP_GUIDE.md)")
        return
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    
    print_info(f"Projeto: {project_id}")
    print_info(f"Localização: southamerica-east1 (São Paulo)\n")
    
    # Criar recursos
    bucket_ok = create_bucket(project_id, bucket_name)
    dataset_ok = create_dataset(project_id, dataset_id)
    
    print("\n" + "="*60)
    if bucket_ok and dataset_ok:
        print_success("TODOS OS RECURSOS CRIADOS COM SUCESSO!")
    else:
        print_error("Alguns recursos não foram criados")
    print("="*60 + "\n")
    
    if bucket_ok and dataset_ok:
        print_info("Próximos passos:")
        print("  1. Execute: python test_gcp_config.py")
        print("  2. Execute: docker-compose up -d")
        print("  3. Execute: python pipeline/brt_flow.py\n")

if __name__ == "__main__":
    main()
