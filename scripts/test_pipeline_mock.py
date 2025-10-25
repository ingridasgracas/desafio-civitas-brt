"""
Script de teste do pipeline com dados mockados
Simula captura da API BRT com dados fictícios
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import pandas as pd
from datetime import datetime
from loguru import logger
from brt_data_aggregator import BRTDataAggregator
from gcs_manager import GCSManager

def create_mock_data():
    """Cria dados fictícios simulando resposta da API BRT"""
    
    logger.info("🎭 Gerando dados mockados da API BRT...")
    
    # Simula dados de 20 veículos
    mock_data = []
    
    lines = ['01', '10', '50', '60']
    
    for i in range(20):
        mock_data.append({
            'ordem': f'BRT{1000 + i}',
            'line': lines[i % len(lines)],
            'latitude': -22.9 + (i * 0.001),  # Rio de Janeiro
            'longitude': -43.2 - (i * 0.001),
            'speed': 30 + (i * 2),
            'timestamp': datetime.now().isoformat(),
            'direction': 'Norte'
        })
    
    df = pd.DataFrame(mock_data)
    logger.success(f"✅ Dados mockados criados: {len(df)} registros")
    
    return df


def test_full_pipeline():
    """Testa pipeline completo com dados mockados"""
    
    logger.info("="*60)
    logger.info("🧪 TESTE DO PIPELINE COM DADOS MOCKADOS")
    logger.info("="*60)
    
    # 1. Criar dados mockados
    df = create_mock_data()
    logger.info(f"\n📊 Dados capturados:\n{df.head()}\n")
    
    # 2. Testar agregador
    logger.info("📦 Testando agregador de buffer...")
    aggregator = BRTDataAggregator(aggregation_minutes=10)
    
    # Simular 6 capturas (10 minutos)
    for i in range(6):
        logger.info(f"  Captura {i+1}/6...")
        is_complete = aggregator.add_data(df)
        
        status = aggregator.get_buffer_status()
        logger.info(f"  Buffer: {status['captures_count']}/{status['target_captures']}")
        
        if is_complete:
            logger.success("  ✅ Buffer completo!")
            break
    
    # 3. Gerar CSV
    logger.info("\n💾 Gerando arquivo CSV...")
    csv_path = aggregator.aggregate_and_save()
    
    if csv_path:
        logger.success(f"✅ CSV gerado: {csv_path}")
        
        # Mostrar primeiras linhas
        df_saved = pd.read_csv(csv_path)
        logger.info(f"\n📄 Conteúdo do CSV ({len(df_saved)} registros):")
        logger.info(f"\n{df_saved.head(10)}\n")
    else:
        logger.error("❌ Erro ao gerar CSV")
        return False
    
    # 4. Upload para GCS
    logger.info("☁️ Fazendo upload para Google Cloud Storage...")
    try:
        gcs_manager = GCSManager()
        gcs_uri = gcs_manager.upload_file(csv_path, gcs_folder='brt-data-test')
        
        if gcs_uri:
            logger.success(f"✅ Upload concluído: {gcs_uri}")
        else:
            logger.error("❌ Erro no upload")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao fazer upload: {e}")
        return False
    
    # 5. Verificar no GCS
    logger.info("\n🔍 Verificando arquivo no GCS...")
    try:
        files = gcs_manager.list_files(prefix='brt-data-test/')
        logger.info(f"Arquivos no bucket:")
        for file in files:
            logger.info(f"  - {file}")
        logger.success("✅ Arquivo encontrado no GCS!")
    except Exception as e:
        logger.error(f"❌ Erro ao listar arquivos: {e}")
    
    # Resultado final
    logger.info("\n" + "="*60)
    logger.success("🎉 TESTE DO PIPELINE CONCLUÍDO COM SUCESSO!")
    logger.info("="*60)
    logger.info("\n✅ Próximos passos:")
    logger.info("  1. Acesse o GCS: https://console.cloud.google.com/storage/browser/brt-data-civitas?project=brt-pipeline-civitas")
    logger.info("  2. Verifique a pasta 'brt-data-test/'")
    logger.info("  3. Execute DBT manualmente: cd dbt_brt && dbt run\n")
    
    return True


if __name__ == "__main__":
    test_full_pipeline()
