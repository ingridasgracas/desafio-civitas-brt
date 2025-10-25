"""
Script para captura de dados da API BRT Rio de Janeiro
Captura informações GPS dos veículos minuto a minuto
Arquitetura Medallion - Camada Bronze (dados brutos)
"""

import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()


class BRTAPICapture:
    """Classe para captura de dados da API do BRT"""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Inicializa o capturador de dados BRT
        
        Args:
            api_url: URL da API BRT (padrão: variável de ambiente BRT_API_URL)
        """
        self.api_url = api_url or os.getenv(
            'BRT_API_URL', 
            'https://jeap.rio.rj.gov.br/je-api/api/v2/gps'
        )
        logger.info(f"BRT API Capture inicializado com URL: {self.api_url}")
    
    def fetch_data(self) -> Optional[Dict]:
        """
        Realiza requisição à API BRT e retorna os dados
        
        Returns:
            Dict com dados da API ou None em caso de erro
        """
        try:
            logger.info(f"Capturando dados da API BRT em {datetime.now()}")
            
            response = requests.get(
                self.api_url,
                timeout=30,
                headers={'User-Agent': 'CIVITAS-BRT-Pipeline/1.0'}
            )
            response.raise_for_status()
            
            data = response.json()
            logger.success(f"Dados capturados com sucesso: {len(data)} veículos")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao capturar dados da API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None
    
    def process_raw_data(self, raw_data: Dict) -> pd.DataFrame:
        """
        Processa dados brutos da API e retorna DataFrame
        
        Args:
            raw_data: Dados brutos da API
            
        Returns:
            DataFrame com dados processados
        """
        try:
            # Adiciona timestamp de captura
            capture_timestamp = datetime.now().isoformat()
            
            # Verifica se raw_data é uma lista ou dict
            if isinstance(raw_data, list):
                vehicles = raw_data
            elif isinstance(raw_data, dict) and 'veiculos' in raw_data:
                vehicles = raw_data['veiculos']
            else:
                vehicles = [raw_data]
            
            # Processa cada veículo
            processed_records = []
            for vehicle in vehicles:
                record = {
                    'capture_timestamp': capture_timestamp,
                    'vehicle_id': vehicle.get('codigo') or vehicle.get('ordem'),  # Novo formato usa 'codigo'
                    'line': vehicle.get('linha'),
                    'latitude': vehicle.get('latitude'),
                    'longitude': vehicle.get('longitude'),
                    'speed': vehicle.get('velocidade'),
                    'timestamp_gps': vehicle.get('dataHora'),
                    'placa': vehicle.get('placa', ''),
                    'sentido': vehicle.get('sentido', ''),
                    'trajeto': vehicle.get('trajeto', ''),
                    'raw_data': str(vehicle)  # Mantém dados brutos para auditoria
                }
                processed_records.append(record)
            
            df = pd.DataFrame(processed_records)
            logger.info(f"Dados processados: {len(df)} registros")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao processar dados: {e}")
            return pd.DataFrame()
    
    def capture_and_process(self) -> pd.DataFrame:
        """
        Captura e processa dados em uma única operação
        
        Returns:
            DataFrame com dados processados
        """
        raw_data = self.fetch_data()
        
        if raw_data is None:
            logger.warning("Retornando DataFrame vazio devido a erro na captura")
            return pd.DataFrame()
        
        return self.process_raw_data(raw_data)


def main():
    """Função principal para teste do módulo"""
    capture = BRTAPICapture()
    df = capture.capture_and_process()
    
    if not df.empty:
        print("\n=== Amostra dos dados capturados ===")
        print(df.head())
        print(f"\nTotal de registros: {len(df)}")
        print(f"\nColunas: {df.columns.tolist()}")
    else:
        print("Nenhum dado foi capturado")


if __name__ == "__main__":
    main()
