"""
Script para criar dados de teste (mock) do BRT
Simula resposta da API para testar pipeline end-to-end
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
from loguru import logger

def generate_mock_brt_data(num_records=100, num_lines=5):
    """
    Gera dados mockados similares à API BRT
    
    Args:
        num_records: Número de registros por linha
        num_lines: Número de linhas BRT diferentes
    
    Returns:
        DataFrame com dados mockados
    """
    
    logger.info(f"Gerando {num_records * num_lines} registros mockados...")
    
    # Linhas BRT reais do Rio
    brt_lines = [
        "Transoeste",
        "Transcarioca",
        "Transolímpica",
        "TransBrasil",
        "Transbrasil"
    ][:num_lines]
    
    # Coordenadas aproximadas do Rio (zona oeste principalmente)
    # Barra da Tijuca, Campo Grande, Santa Cruz
    lat_ranges = {
        "Transoeste": (-23.012, -22.995),
        "Transcarioca": (-22.910, -22.885),
        "Transolímpica": (-22.920, -22.900),
        "TransBrasil": (-22.910, -22.880),
        "Transbrasil": (-22.910, -22.880)
    }
    
    lon_ranges = {
        "Transoeste": (-43.490, -43.360),
        "Transcarioca": (-43.370, -43.250),
        "Transolímpica": (-43.440, -43.320),
        "TransBrasil": (-43.300, -43.180),
        "Transbrasil": (-43.300, -43.180)
    }
    
    records = []
    base_time = datetime.now()
    
    for line in brt_lines:
        for i in range(num_records):
            # Timestamp com variação
            timestamp = base_time - timedelta(seconds=i*30)
            
            # Coordenadas dentro da faixa da linha
            latitude = np.random.uniform(*lat_ranges[line])
            longitude = np.random.uniform(*lon_ranges[line])
            
            # Velocidade realista (0-80 km/h, maioria 20-50)
            speed = np.random.choice(
                [0, np.random.uniform(10, 30), np.random.uniform(30, 60), np.random.uniform(60, 80)],
                p=[0.1, 0.4, 0.4, 0.1]  # 10% parado, 40% lento, 40% normal, 10% rápido
            )
            
            # ID do veículo
            vehicle_id = f"BRT-{line[:4].upper()}-{1000 + i}"
            
            record = {
                "dataHora": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "ordem": str(vehicle_id),
                "linha": line,
                "latitude": round(latitude, 6),
                "longitude": round(longitude, 6),
                "velocidade": round(speed, 1),
                # Campos adicionais que a API pode retornar
                "direcao": np.random.choice(["IDA", "VOLTA"]),
                "timestamp_captura": timestamp.isoformat()
            }
            
            records.append(record)
    
    df = pd.DataFrame(records)
    
    logger.success(f"✅ {len(df)} registros mockados gerados!")
    logger.info(f"   Linhas: {df['linha'].nunique()}")
    logger.info(f"   Veículos: {df['ordem'].nunique()}")
    logger.info(f"   Período: {df['dataHora'].min()} até {df['dataHora'].max()}")
    
    return df


def save_mock_data_as_api_response(df, output_dir="data_output/mock"):
    """Salva dados mockados no formato da API"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Formato JSON similar à API
    json_file = output_path / f"mock_api_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    df.to_json(json_file, orient='records', date_format='iso', indent=2)
    logger.success(f"✅ Dados mockados salvos: {json_file}")
    
    return json_file


def save_mock_data_as_csv(df, output_dir="data_output/mock"):
    """Salva dados mockados como CSV"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    csv_file = output_path / f"mock_brt_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    df.to_csv(csv_file, index=False)
    logger.success(f"✅ CSV mockado salvo: {csv_file}")
    
    return csv_file


def main():
    """Função principal"""
    
    logger.info("="*60)
    logger.info("🎭 GERADOR DE DADOS MOCKADOS - API BRT")
    logger.info("="*60)
    
    # Gerar dados
    df = generate_mock_brt_data(num_records=50, num_lines=5)
    
    # Salvar em múltiplos formatos
    json_file = save_mock_data_as_api_response(df)
    csv_file = save_mock_data_as_csv(df)
    
    # Estatísticas
    logger.info("\n" + "="*60)
    logger.info("📊 ESTATÍSTICAS DOS DADOS MOCKADOS")
    logger.info("="*60)
    logger.info(f"\nTotal de registros: {len(df)}")
    logger.info(f"\nPor linha:")
    print(df.groupby('linha').size())
    logger.info(f"\nVelocidade média: {df['velocidade'].mean():.1f} km/h")
    logger.info(f"Velocidade máxima: {df['velocidade'].max():.1f} km/h")
    logger.info(f"\nÁrea de cobertura:")
    logger.info(f"  Latitude: {df['latitude'].min():.4f} até {df['latitude'].max():.4f}")
    logger.info(f"  Longitude: {df['longitude'].min():.4f} até {df['longitude'].max():.4f}")
    
    logger.info("\n" + "="*60)
    logger.success("✅ DADOS MOCKADOS CRIADOS COM SUCESSO!")
    logger.info("="*60)
    logger.info(f"\n📁 Arquivos salvos em: data_output/mock/")
    logger.info(f"   JSON: {json_file.name}")
    logger.info(f"   CSV:  {csv_file.name}")
    logger.info("\n💡 Use estes dados para testar o pipeline!\n")


if __name__ == "__main__":
    main()
