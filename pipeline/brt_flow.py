"""
Pipeline Prefect v1.4.1 - BRT Data Pipeline
Orquestra captura, agregação, upload para GCS e transformação DBT
Arquitetura Medallion: Bronze -> Silver -> Gold
"""

import sys
from pathlib import Path

# Adiciona diretório de scripts ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from prefect import Flow, task, Parameter
from prefect.schedules import IntervalSchedule
from prefect.engine.signals import SKIP
from datetime import timedelta, datetime
from loguru import logger
import time
import subprocess
import os

from brt_api_capture import BRTAPICapture
from brt_data_aggregator import BRTDataAggregator
from gcs_manager import GCSManager


# ==================== TASKS ====================

@task(name="Capturar dados BRT API", max_retries=3, retry_delay=timedelta(seconds=30))
def capture_brt_data():
    """
    Task: Captura dados da API BRT
    Retorna: DataFrame com dados capturados
    """
    logger.info("📡 Iniciando captura de dados da API BRT...")
    
    capture = BRTAPICapture()
    df = capture.capture_and_process()
    
    if df.empty:
        logger.warning("Nenhum dado capturado")
        raise SKIP("Sem dados disponíveis na API")
    
    logger.success(f"Dados capturados: {len(df)} registros")
    return df


@task(name="Adicionar ao buffer de agregação", nout=2)
def add_to_buffer(df, aggregator):
    """
    Task: Adiciona dados ao buffer de agregação
    Retorna: Tuple (is_complete, aggregator)
    """
    logger.info("Adicionando dados ao buffer...")
    
    is_complete = aggregator.add_data(df)
    
    status = aggregator.get_buffer_status()
    logger.info(
        f"Buffer status: {status['captures_count']}/{status['target_captures']} capturas"
    )
    
    return is_complete, aggregator


@task(name="Gerar arquivo CSV")
def generate_csv(is_complete, aggregator):
    """
    Task: Gera arquivo CSV quando buffer está completo
    Retorna: Caminho do arquivo CSV ou None
    """
    if not is_complete:
        logger.info("Buffer ainda não está completo, pulando geração de CSV")
        raise SKIP("Buffer incompleto")
    
    logger.info("Gerando arquivo CSV consolidado...")
    
    csv_path = aggregator.aggregate_and_save()
    
    if csv_path:
        logger.success(f"CSV gerado: {csv_path}")
    else:
        logger.error("❌ Erro ao gerar CSV")
    
    return csv_path


@task(name="Upload para Google Cloud Storage", max_retries=2, retry_delay=timedelta(seconds=60))
def upload_to_gcs(csv_path):
    """
    Task: Faz upload do CSV para o GCS
    Retorna: URI do arquivo no GCS
    """
    if csv_path is None:
        logger.warning("⚠️ Sem arquivo para upload")
        raise SKIP("Sem arquivo CSV")
    
    logger.info(f"☁️ Enviando arquivo para GCS: {csv_path}")
    
    gcs_manager = GCSManager()
    gcs_uri = gcs_manager.upload_file(csv_path, gcs_folder='brt-data')
    
    if gcs_uri:
        logger.success(f"Upload concluído: {gcs_uri}")
    else:
        logger.error("Erro ao fazer upload para GCS")
        raise Exception("Falha no upload para GCS")
    
    return gcs_uri


@task(name="Executar DBT - Criar tabela externa")
def run_dbt_external_table():
    """
    Task: Cria/atualiza tabela externa no BigQuery
    
    NOTA: A partir do dbt-bigquery 1.5+, tabelas externas são criadas
    usando o comando 'dbt run --select source:*' ou via script SQL direto.
    """
    logger.info("Criando tabela externa no BigQuery...")
    
    dbt_dir = Path(__file__).parent.parent / 'dbt_brt'
    
    try:
        # Opção 1: Usar script SQL direto (mais confiável)
        logger.info("Criando tabela externa via BigQuery API...")
        
        from google.cloud import bigquery
        import os
        
        # Inicializa cliente BigQuery
        client = bigquery.Client(
            project=os.getenv('GCP_PROJECT_ID')
        )
        
        # Lê o script SQL
        sql_file = dbt_dir / 'models' / 'bronze' / 'create_external_table.sql'
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        # Substitui variáveis
        sql = sql.replace('${GCP_PROJECT_ID}', os.getenv('GCP_PROJECT_ID'))
        sql = sql.replace('${GCS_BUCKET_NAME}', os.getenv('GCS_BUCKET_NAME'))
        
        # Executa comandos SQL (separados por ;)
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    client.query(statement).result()
                    logger.debug(f"Executado: {statement[:50]}...")
                except Exception as e:
                    # Ignora erros de "já existe" ou comentários
                    if 'Already Exists' not in str(e) and 'comment' not in str(e).lower():
                        logger.warning(f"Aviso: {e}")
        
        logger.success("Tabela externa criada/atualizada com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao criar tabela externa: {e}")
        logger.info("Você pode criar manualmente usando o script:")
        logger.info("   dbt_brt/models/bronze/create_external_table.sql")
        raise


@task(name="Executar DBT - Transformações")
def run_dbt_transformations():
    """
    Task: Executa modelos DBT (Silver e Gold)
    """
    logger.info("Executando transformações DBT...")
    
    dbt_dir = Path(__file__).parent.parent / 'dbt_brt'
    
    try:
        # Executa modelos DBT
        result = subprocess.run(
            ['dbt', 'run', '--profiles-dir', '.'],
            cwd=str(dbt_dir),
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.success("Transformações DBT executadas com sucesso")
        logger.debug(result.stdout)
        
        # Gera documentação
        logger.info("Gerando documentação DBT...")
        subprocess.run(
            ['dbt', 'docs', 'generate', '--profiles-dir', '.'],
            cwd=str(dbt_dir),
            check=True,
            capture_output=True
        )
        
        logger.success("Documentação gerada")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar DBT: {e.stderr}")
        raise


@task(name="Executar testes DBT")
def run_dbt_tests():
    """
    Task: Executa testes de qualidade de dados
    """
    logger.info("Executando testes de qualidade de dados...")
    
    dbt_dir = Path(__file__).parent.parent / 'dbt_brt'
    
    try:
        result = subprocess.run(
            ['dbt', 'test', '--profiles-dir', '.'],
            cwd=str(dbt_dir),
            check=False,  # Não falha se testes falharem
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.success("Todos os testes passaram")
        else:
            logger.warning("Alguns testes falharam:")
            logger.warning(result.stdout)
        
    except Exception as e:
        logger.error(f" Erro ao executar testes: {e}")


# ==================== FLOW ====================

def create_brt_pipeline_flow(
    aggregation_minutes: int = 10,
    run_interval_minutes: int = 1
):
    """
    Cria flow do pipeline BRT
    
    Args:
        aggregation_minutes: Minutos para agregação
        run_interval_minutes: Intervalo entre execuções
    """
    
    # Configuração do schedule (executa a cada N minutos)
    schedule = IntervalSchedule(
        interval=timedelta(minutes=run_interval_minutes)
    )
    
    with Flow(
        name="BRT Data Pipeline - Medallion Architecture",
        schedule=schedule
    ) as flow:
        
        # Parâmetros
        agg_minutes = Parameter(
            "aggregation_minutes", 
            default=aggregation_minutes
        )
        
        # Inicializa agregador (mantém estado entre execuções)
        aggregator = BRTDataAggregator(aggregation_minutes=agg_minutes)
        
        # ========== Camada Bronze ==========
        # 1. Captura dados da API
        df = capture_brt_data()
        
        # 2. Adiciona ao buffer de agregação
        buffer_result = add_to_buffer(df, aggregator)
        is_complete = buffer_result[0]
        aggregator = buffer_result[1]
        
        # 3. Gera CSV quando buffer completo
        csv_path = generate_csv(is_complete, aggregator)
        
        # 4. Upload para GCS
        gcs_uri = upload_to_gcs(csv_path)
        
        # ========== Camada Silver/Gold ==========
        # 5. Cria tabela externa no BigQuery
        external_table = run_dbt_external_table()
        external_table.set_upstream(gcs_uri)
        
        # 6. Executa transformações DBT
        transformations = run_dbt_transformations()
        transformations.set_upstream(external_table)
        
        # 7. Executa testes de qualidade
        tests = run_dbt_tests()
        tests.set_upstream(transformations)
    
    return flow


# ==================== MAIN ====================

def main():
    """Função principal para registro e execução do flow"""
    
    # Cria flow
    flow = create_brt_pipeline_flow(
        aggregation_minutes=10,
        run_interval_minutes=1
    )
    
    # Registra flow no Prefect Server
    # flow.register(project_name="BRT Pipeline")
    
    # OU executa localmente
    logger.info("Iniciando BRT Data Pipeline...")
    flow.run()


if __name__ == "__main__":
    main()
