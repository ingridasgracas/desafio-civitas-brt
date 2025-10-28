# Data Folder

Esta pasta contém dados gerados pela pipeline BRT.

## Estrutura

```
data/
├── example_brt_consolidated.csv   # Arquivo de exemplo (100 registros)
├── bronze/                         # Capturas individuais da API (1 min)
├── bronze_consolidated/            # Dados consolidados (10 min)
├── silver/                         # Dados processados/limpos
└── gold/                           # Métricas agregadas
```

## Arquivo de Exemplo

**`example_brt_consolidated.csv`** (48 KB)
- Contém 100 linhas de exemplo de dados consolidados
- Formato: CSV com header
- Período: 27/10/2025 ~18:17
- Linhas BRT: 22, 35, 50, 51, 52

### Colunas:
- `timestamp`: Data/hora da captura
- `vehicle_id`: ID do veículo BRT
- `line`: Linha do BRT
- `latitude`, `longitude`: Coordenadas GPS
- `speed`: Velocidade em km/h
- `gps_timestamp`: Timestamp GPS (milissegundos)
- `placa`: Placa do veículo
- `sentido`: Direção (ida/volta)
- `trajeto`: Trajeto completo da linha
- `raw_data`: Dados JSON brutos da API

## Como Reproduzir os CSVs Completos

### Opção 1: Baixar do Google Cloud Storage
```bash
# Autentique-se com a conta do projeto
gcloud auth login
gcloud config set project brt-pipeline-476423

# Baixe os arquivos consolidados
gsutil cp gs://brt-data-bucket/bronze/*.csv data/bronze_consolidated/
```

### Opção 2: Executar a Pipeline
```powershell
# 1. Ative o ambiente virtual
venv_new\Scripts\activate

# 2. Configure credenciais GCP
$env:GOOGLE_APPLICATION_CREDENTIALS="config\gcp-credentials.json"

# 3. Inicie Prefect Server (Docker)
docker start temp-postgres-1 temp-hasura-1 temp-graphql-1 temp-apollo-1 temp-ui-1 temp-towel-1

# 4. Aguarde containers ficarem healthy (~30s)
docker ps

# 5. Registre o flow
python scripts\register_flow.py

# 6. Inicie o agent
prefect agent local start -l ingrid

# 7. Execute o flow manualmente ou aguarde schedule (1 minuto)
```

A pipeline irá:
1. Capturar dados da API a cada 1 minuto → `data/bronze/`
2. Consolidar a cada 10 minutos → `data/bronze_consolidated/`
3. Upload para GCS → `gs://brt-data-bucket/bronze/`
4. DBT transforma Bronze → Silver → Gold
5. Dados finais no BigQuery:
   - `brt_dataset_bronze.external_brt_gps_data`
   - `brt_dataset_silver.stg_brt_gps_cleaned`
   - `brt_dataset_gold.fct_brt_line_metrics`

## BigQuery

Dados completos disponíveis no BigQuery (14.630+ registros):

```sql
-- Ver dados Bronze
SELECT * FROM `brt-pipeline-476423.brt_dataset_bronze.external_brt_gps_data` LIMIT 100;

-- Ver métricas Gold
SELECT * FROM `brt-pipeline-476423.brt_dataset_gold.fct_brt_line_metrics` 
ORDER BY date_partition DESC, line;
```

## Notas

- **Não commite CSVs grandes no Git** - use GCS/BigQuery
- Arquivo de exemplo (`example_brt_consolidated.csv`) é permitido
- Pastas `bronze/`, `silver/`, `gold/` são ignoradas pelo Git
- Dados reais estão em Cloud Storage e BigQuery
