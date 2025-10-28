"""
Google Cloud Storage Manager
Gerencia upload de arquivos CSV para o GCS
Arquitetura Medallion - Persistência na nuvem
"""

from google.cloud import storage
from pathlib import Path
from typing import Optional
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()


class GCSManager:
    """Classe para gerenciar uploads no Google Cloud Storage"""
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        credentials_path: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """
        Inicializa o gerenciador GCS
        
        Args:
            bucket_name: Nome do bucket GCS
            credentials_path: Caminho para arquivo de credenciais
            project_id: ID do projeto GCP
        """
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME')
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        
        credentials_path = credentials_path or os.getenv('GCP_CREDENTIALS_PATH')
        
        if credentials_path and os.path.exists(credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            logger.info(f"Credenciais GCP carregadas: {credentials_path}")
        
        try:
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            logger.success(
                f"GCS Manager inicializado - Bucket: {self.bucket_name}"
            )
        except Exception as e:
            logger.error(f"Erro ao inicializar GCS Client: {e}")
            self.client = None
            self.bucket = None
    
    def upload_file(
        self,
        local_filepath: str,
        gcs_folder: str = 'brt-data',
        destination_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Faz upload de arquivo para o GCS
        
        Args:
            local_filepath: Caminho do arquivo local
            gcs_folder: Pasta no bucket GCS
            destination_name: Nome do arquivo no GCS (opcional)
            
        Returns:
            URI público do arquivo ou None em caso de erro
        """
        if not self.bucket:
            logger.error("Bucket GCS não inicializado")
            return None
        
        try:
            local_path = Path(local_filepath)
            
            if not local_path.exists():
                logger.error(f"Arquivo não encontrado: {local_filepath}")
                return None
            
            # Define nome de destino
            if destination_name is None:
                destination_name = local_path.name
            
            blob_name = f"{gcs_folder}/{destination_name}"
            blob = self.bucket.blob(blob_name)
            
            logger.info(f"Iniciando upload: {local_filepath} -> gs://{self.bucket_name}/{blob_name}")
            
            # Faz upload
            blob.upload_from_filename(str(local_path))
            
            # URI do arquivo
            gcs_uri = f"gs://{self.bucket_name}/{blob_name}"
            
            logger.success(f"Upload concluído: {gcs_uri}")
            
            return gcs_uri
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload para GCS: {e}")
            return None
    
    def list_files(self, prefix: str = 'brt-data/') -> list:
        """
        Lista arquivos no bucket com determinado prefixo
        
        Args:
            prefix: Prefixo para filtrar arquivos
            
        Returns:
            Lista de nomes de arquivos
        """
        if not self.bucket:
            logger.error("Bucket GCS não inicializado")
            return []
        
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            files = [blob.name for blob in blobs]
            logger.info(f"Encontrados {len(files)} arquivos com prefixo '{prefix}'")
            return files
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {e}")
            return []
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Deleta arquivo do bucket
        
        Args:
            blob_name: Nome do blob (arquivo) no GCS
            
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        if not self.bucket:
            logger.error("Bucket GCS não inicializado")
            return False
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.success(f"Arquivo deletado: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {e}")
            return False
    
    def create_bucket_if_not_exists(self, location: str = 'US') -> bool:
        """
        Cria bucket se não existir
        
        Args:
            location: Localização do bucket
            
        Returns:
            True se bucket existe ou foi criado, False em caso de erro
        """
        try:
            # Verifica se bucket existe
            if self.client.lookup_bucket(self.bucket_name):
                logger.info(f"Bucket já existe: {self.bucket_name}")
                return True
            
            # Cria bucket
            bucket = self.client.create_bucket(
                self.bucket_name,
                location=location
            )
            self.bucket = bucket
            logger.success(f"Bucket criado: {self.bucket_name} em {location}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar bucket: {e}")
            return False


def main():
    """Função principal para teste do módulo"""
    import tempfile
    
    # Cria arquivo de teste
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("vehicle_id,latitude,longitude,timestamp\n")
        f.write("1001,-22.906847,-43.172897,2025-10-24T10:00:00\n")
        test_file = f.name
    
    print("=== Teste GCS Manager ===\n")
    
    # Inicializa manager
    gcs = GCSManager()
    
    if gcs.bucket:
        # Upload
        print(f"Fazendo upload de: {test_file}")
        uri = gcs.upload_file(test_file, gcs_folder='test')
        
        if uri:
            print(f"✓ Upload bem-sucedido: {uri}\n")
            
            # Lista arquivos
            print("Arquivos no bucket:")
            files = gcs.list_files(prefix='test/')
            for file in files:
                print(f"  - {file}")
    else:
        print("GCS não configurado. Configure as credenciais em .env")
    
    # Limpa arquivo de teste
    os.unlink(test_file)


if __name__ == "__main__":
    main()
