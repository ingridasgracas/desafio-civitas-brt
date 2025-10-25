"""
Script para criar tabela externa (external table) no BigQuery
apontando para arquivos CSV no Google Cloud Storage
"""

from google.cloud import bigquery
from dotenv import load_dotenv
import os
from loguru import logger

def create_external_table():
    """Cria external table no BigQuery"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    project_id = os.getenv('GCP_PROJECT_ID')
    dataset_id = 'brt_dataset'
    table_id = 'brt_gps_raw'
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    
    logger.info(f"📊 Criando external table: {project_id}.{dataset_id}.{table_id}")
    
    # Inicializar cliente BigQuery
    client = bigquery.Client.from_service_account_json(
        os.getenv('GCP_CREDENTIALS_PATH')
    )
    
    # Configuração da external table
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    # Definir schema
    schema = [
        bigquery.SchemaField("capture_timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("vehicle_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("line", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("latitude", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("longitude", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("speed", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("timestamp_gps", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("placa", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("sentido", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("trajeto", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("raw_data", "STRING", mode="NULLABLE"),
    ]
    
    # Configurar external data source
    external_config = bigquery.ExternalConfig("CSV")
    external_config.source_uris = [f"gs://{bucket_name}/brt-data/*.csv"]
    external_config.schema = schema
    external_config.options.skip_leading_rows = 1  # Skip header
    external_config.options.allow_quoted_newlines = True
    external_config.options.allow_jagged_rows = False
    
    # Criar tabela
    table = bigquery.Table(table_ref, schema=schema)
    table.external_data_configuration = external_config
    
    try:
        table = client.create_table(table, exists_ok=True)
        logger.success(f"✅ External table criada: {table_ref}")
        logger.info(f"   - Source: gs://{bucket_name}/brt-data/*.csv")
        logger.info(f"   - Schema: {len(schema)} colunas")
        
        # Testar query
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT vehicle_id) as unique_vehicles,
            COUNT(DISTINCT line) as unique_lines
        FROM `{table_ref}`
        """
        
        logger.info("🔍 Testando query na external table...")
        result = client.query(query).result()
        
        for row in result:
            logger.info(f"   - Total de registros: {row.total_records}")
            logger.info(f"   - Veículos únicos: {row.unique_vehicles}")
            logger.info(f"   - Linhas únicas: {row.unique_lines}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar external table: {e}")
        return False

if __name__ == "__main__":
    success = create_external_table()
    
    if success:
        logger.success("\n🎉 External table criada com sucesso!")
        logger.info("\n📝 Próximos passos:")
        logger.info("   1. Execute: cd dbt_brt")
        logger.info("   2. Execute: dbt run")
        logger.info("   3. Execute: dbt test")
    else:
        logger.error("\n❌ Falha ao criar external table")
