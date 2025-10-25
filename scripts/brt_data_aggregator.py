"""
Agregador de dados BRT
Coleta dados minuto a minuto e gera arquivo CSV com 10 minutos de dados
Arquitetura Medallion - Transição Bronze -> Silver
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()


class BRTDataAggregator:
    """Classe para agregação de dados BRT capturados minuto a minuto"""
    
    def __init__(
        self, 
        aggregation_minutes: int = 10,
        data_dir: Optional[str] = None
    ):
        """
        Inicializa o agregador de dados
        
        Args:
            aggregation_minutes: Quantidade de minutos para agregação
            data_dir: Diretório para armazenar dados
        """
        self.aggregation_minutes = int(
            os.getenv('AGGREGATION_MINUTES', aggregation_minutes)
        )
        self.data_dir = Path(data_dir or './data')
        self.bronze_dir = self.data_dir / 'bronze'
        self.silver_dir = self.data_dir / 'silver'
        
        # Cria diretórios se não existirem
        self.bronze_dir.mkdir(parents=True, exist_ok=True)
        self.silver_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"Agregador inicializado: {self.aggregation_minutes} minutos"
        )
        
        self.data_buffer: List[pd.DataFrame] = []
        self.buffer_start_time: Optional[datetime] = None
    
    def add_data(self, df: pd.DataFrame) -> bool:
        """
        Adiciona dados ao buffer
        
        Args:
            df: DataFrame com dados capturados
            
        Returns:
            True se buffer está completo, False caso contrário
        """
        if df.empty:
            logger.warning("DataFrame vazio recebido, ignorando")
            return False
        
        # Primeiro dado - inicializa timestamp
        if self.buffer_start_time is None:
            self.buffer_start_time = datetime.now()
            logger.info(f"Iniciando buffer em {self.buffer_start_time}")
        
        self.data_buffer.append(df.copy())
        logger.info(
            f"Dados adicionados ao buffer: {len(self.data_buffer)} capturas"
        )
        
        # Verifica se completou o período de agregação
        elapsed_time = datetime.now() - self.buffer_start_time
        is_complete = len(self.data_buffer) >= self.aggregation_minutes
        
        if is_complete:
            logger.success(
                f"Buffer completo: {len(self.data_buffer)} capturas em "
                f"{elapsed_time.total_seconds():.1f} segundos"
            )
        
        return is_complete
    
    def aggregate_and_save(self) -> Optional[str]:
        """
        Agrega dados do buffer e salva em CSV
        
        Returns:
            Caminho do arquivo CSV gerado ou None em caso de erro
        """
        if not self.data_buffer:
            logger.warning("Buffer vazio, nada para agregar")
            return None
        
        try:
            # Concatena todos os DataFrames do buffer
            aggregated_df = pd.concat(self.data_buffer, ignore_index=True)
            
            # Gera nome do arquivo com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"brt_data_{timestamp}.csv"
            filepath = self.silver_dir / filename
            
            # Salva CSV
            aggregated_df.to_csv(filepath, index=False)
            
            logger.success(
                f"Arquivo CSV gerado: {filepath} "
                f"({len(aggregated_df)} registros)"
            )
            
            # Também salva cópia na camada bronze (dados brutos)
            bronze_filepath = self.bronze_dir / filename
            aggregated_df.to_csv(bronze_filepath, index=False)
            
            # Limpa buffer
            self.data_buffer = []
            self.buffer_start_time = None
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erro ao agregar e salvar dados: {e}")
            return None
    
    def get_buffer_status(self) -> dict:
        """
        Retorna status atual do buffer
        
        Returns:
            Dict com informações do buffer
        """
        elapsed = None
        if self.buffer_start_time:
            elapsed = (datetime.now() - self.buffer_start_time).total_seconds()
        
        return {
            'captures_count': len(self.data_buffer),
            'target_captures': self.aggregation_minutes,
            'elapsed_seconds': elapsed,
            'is_complete': len(self.data_buffer) >= self.aggregation_minutes
        }


def main():
    """Função principal para teste do módulo"""
    from brt_api_capture import BRTAPICapture
    import time
    
    # Inicializa capturador e agregador
    capture = BRTAPICapture()
    aggregator = BRTDataAggregator(aggregation_minutes=3)  # 3 min para teste
    
    print("=== Teste de Agregação BRT ===")
    print(f"Capturando dados a cada minuto por {aggregator.aggregation_minutes} minutos...\n")
    
    # Simula captura minuto a minuto
    for i in range(aggregator.aggregation_minutes):
        print(f"[{i+1}/{aggregator.aggregation_minutes}] Capturando dados...")
        
        df = capture.capture_and_process()
        is_complete = aggregator.add_data(df)
        
        status = aggregator.get_buffer_status()
        print(f"Status: {status['captures_count']}/{status['target_captures']} capturas")
        
        if is_complete:
            print("\n✓ Buffer completo! Gerando CSV...")
            filepath = aggregator.aggregate_and_save()
            if filepath:
                print(f"✓ Arquivo salvo: {filepath}\n")
            break
        else:
            print(f"Aguardando próxima captura em 60 segundos...\n")
            time.sleep(60)


if __name__ == "__main__":
    main()
