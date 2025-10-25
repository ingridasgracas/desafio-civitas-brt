"""
Script de Teste - Configuração GCP
Verifica se as credenciais e recursos estão configurados corretamente
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def main():
    print("\n" + "="*60)
    print(f"{BLUE}🔍 VERIFICAÇÃO DE CONFIGURAÇÃO GCP{RESET}")
    print("="*60 + "\n")

    # 1. Carregar .env
    load_dotenv()
    
    # 2. Verificar variáveis de ambiente
    print_info("Verificando variáveis de ambiente...")
    
    project_id = os.getenv('GCP_PROJECT_ID')
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    credentials_path = os.getenv('GCP_CREDENTIALS_PATH')
    dataset = os.getenv('BQ_DATASET')
    
    if project_id == 'seu-projeto-gcp':
        print_error("GCP_PROJECT_ID ainda não foi configurado no arquivo .env")
        return False
    
    print_success(f"Projeto GCP: {project_id}")
    print_success(f"Bucket GCS: {bucket_name}")
    print_success(f"Dataset BigQuery: {dataset}")
    
    # 3. Verificar se arquivo de credenciais existe
    print_info("\nVerificando arquivo de credenciais...")
    
    creds_file = Path(credentials_path)
    if not creds_file.exists():
        print_error(f"Arquivo de credenciais não encontrado: {credentials_path}")
        print_warning("Siga os passos em SETUP_GUIDE.md para criar a Service Account")
        return False
    
    print_success(f"Arquivo de credenciais encontrado: {credentials_path}")
    
    # 4. Testar conexão com GCP
    print_info("\nTestando conexão com Google Cloud...")
    
    try:
        from google.cloud import storage, bigquery
        import google.auth
        
        # Autenticar
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # Teste Storage
        print_info("Testando Cloud Storage...")
        storage_client = storage.Client(project=project_id)
        
        # Listar buckets (ou tentar acessar o bucket específico)
        try:
            bucket = storage_client.get_bucket(bucket_name)
            print_success(f"Bucket '{bucket_name}' acessível ✓")
        except Exception as e:
            if "404" in str(e):
                print_warning(f"Bucket '{bucket_name}' não existe ainda")
                print_info(f"Crie o bucket usando: gsutil mb gs://{bucket_name}/")
            else:
                print_error(f"Erro ao acessar bucket: {e}")
        
        # Teste BigQuery
        print_info("\nTestando BigQuery...")
        bq_client = bigquery.Client(project=project_id)
        
        # Listar datasets
        try:
            dataset_ref = bq_client.dataset(dataset)
            bq_dataset = bq_client.get_dataset(dataset_ref)
            print_success(f"Dataset '{dataset}' acessível ✓")
        except Exception as e:
            if "404" in str(e):
                print_warning(f"Dataset '{dataset}' não existe ainda")
                print_info(f"Crie o dataset usando: bq mk {project_id}:{dataset}")
            else:
                print_error(f"Erro ao acessar dataset: {e}")
        
        print("\n" + "="*60)
        print(f"{GREEN}✅ CONFIGURAÇÃO BÁSICA OK!{RESET}")
        print("="*60 + "\n")
        
        print_info("Próximos passos:")
        print("  1. Se o bucket não existe, crie-o no Cloud Storage")
        print("  2. Se o dataset não existe, crie-o no BigQuery")
        print("  3. Execute: docker-compose up -d (para Prefect)")
        print("  4. Execute: python pipeline/brt_flow.py")
        print(f"\n{BLUE}📖 Consulte SETUP_GUIDE.md para mais detalhes{RESET}\n")
        
        return True
        
    except ImportError as e:
        print_error(f"Bibliotecas GCP não instaladas: {e}")
        print_info("Execute: pip install -r requirements.txt")
        return False
    
    except Exception as e:
        print_error(f"Erro ao conectar com GCP: {e}")
        print_warning("Verifique se:")
        print("  - As APIs do GCP estão ativadas")
        print("  - A Service Account tem as permissões corretas")
        print("  - O arquivo de credenciais é válido")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
