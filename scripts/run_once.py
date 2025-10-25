"""
Script para executar o pipeline BRT uma única vez (sem agendamento)
Útil para testes e demonstração
"""

import sys
from pathlib import Path

# Adiciona diretório de scripts ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from prefect import Flow
from datetime import timedelta
from loguru import logger

from brt_api_capture import BRTAPICapture
from brt_data_aggregator import BRTDataAggregator
from gcs_manager import GCSManager

def run_single_capture():
    """Executa uma captura única e salva no GCS"""
    
    logger.info("="*60)
    logger.info("🚀 EXECUÇÃO ÚNICA - Pipeline BRT")
    logger.info("="*60)
    
    # 1. Capturar dados
    logger.info("\n📡 STEP 1: Capturando dados da API...")
    capture = BRTAPICapture()
    df = capture.capture_and_process()
    
    if df.empty:
        logger.error("❌ Nenhum dado capturado!")
        return False
    
    logger.success(f"✅ {len(df)} registros capturados")
    
    # 2. Gerar CSV
    logger.info("\n💾 STEP 2: Gerando arquivo CSV...")
    aggregator = BRTDataAggregator(aggregation_minutes=1)  # Agregação instantânea
    aggregator.add_data(df)
    csv_path = aggregator.aggregate_and_save()
    
    if not csv_path:
        logger.error("❌ Erro ao gerar CSV!")
        return False
    
    logger.success(f"✅ CSV gerado: {csv_path}")
    
    # 3. Upload para GCS
    logger.info("\n☁️  STEP 3: Fazendo upload para GCS...")
    gcs = GCSManager()
    gcs_uri = gcs.upload_file(csv_path, gcs_folder='brt-data')
    
    if not gcs_uri:
        logger.error("❌ Erro no upload!")
        return False
    
    logger.success(f"✅ Upload concluído: {gcs_uri}")
    
    # Resumo
    logger.info("\n" + "="*60)
    logger.success("🎉 PIPELINE EXECUTADO COM SUCESSO!")
    logger.info("="*60)
    logger.info(f"\n📊 Resumo:")
    logger.info(f"   Registros capturados: {len(df)}")
    logger.info(f"   Arquivo local: {csv_path}")
    logger.info(f"   GCS URI: {gcs_uri}")
    logger.info(f"\n🔍 Próximo passo:")
    logger.info(f"   Execute DBT para transformar os dados:")
    logger.info(f"   cd dbt_brt")
    logger.info(f"   dbt run")
    logger.info(f"   dbt test\n")
    
    return True


if __name__ == "__main__":
    success = run_single_capture()
    sys.exit(0 if success else 1)
