# 🏗️ Arquitetura do Pipeline BRT

## Visão Geral da Arquitetura Medallion

A arquitetura Medallion é um padrão de design para organizar dados em camadas, cada uma com um nível crescente de qualidade e agregação.

## Camadas de Dados

### 🥉 Camada Bronze (Raw Data)

**Objetivo:** Armazenar dados brutos exatamente como recebidos da fonte

**Características:**
- ✅ Dados imutáveis
- ✅ Histórico completo
- ✅ Schema original preservado
- ✅ Formato: CSV no GCS
- ✅ Implementação: Tabela Externa BigQuery

**Fluxo:**
```
API BRT → Captura Minuto a Minuto → Buffer (10 min) → CSV → GCS → BigQuery External Table
```

**Schema Bronze:**
```sql
CREATE EXTERNAL TABLE brt_dataset.brt_gps_raw (
    capture_timestamp TIMESTAMP,
    vehicle_id STRING,
    line STRING,
    latitude FLOAT64,
    longitude FLOAT64,
    speed FLOAT64,
    timestamp_gps TIMESTAMP,
    raw_data STRING
)
OPTIONS (
    format = 'CSV',
    uris = ['gs://brt-data-civitas/brt-data/*.csv'],
    skip_leading_rows = 1
);
```

### 🥈 Camada Silver (Cleaned Data)

**Objetivo:** Dados limpos, validados e enriquecidos

**Transformações:**
1. **Validação de Qualidade**
   - Coordenadas GPS dentro dos limites do RJ
   - Remoção de valores nulos obrigatórios
   - Validação de tipos de dados

2. **Limpeza**
   - Remoção de duplicatas
   - Normalização de formatos
   - Padronização de strings

3. **Enriquecimento**
   - Campos derivados (data, hora, dia da semana)
   - Categorização (velocidade, período do dia)
   - Hash único para rastreamento

**Fluxo:**
```
Bronze → Validação → Deduplicação → Enriquecimento → Silver View
```

**Campos Adicionais:**
- `capture_date`: Data da captura
- `capture_hour`: Hora da captura
- `day_of_week`: Dia da semana (1-7)
- `is_valid_location`: Flag de validação geográfica
- `speed_category`: Categorização da velocidade
- `period_of_day`: Período do dia
- `row_hash`: Hash único MD5

### 🥇 Camada Gold (Business Metrics)

**Objetivo:** Dados agregados e otimizados para consumo analítico

**Características:**
- ✅ Métricas pré-calculadas
- ✅ Agregações de negócio
- ✅ Particionamento otimizado
- ✅ Cluster para performance
- ✅ Pronto para dashboards

**Agregações:**
1. **Dimensões:**
   - Data (particionamento)
   - Linha BRT
   - Período do dia

2. **Métricas Operacionais:**
   - Total de veículos ativos
   - Total de observações
   - Velocidade média/min/max
   - Desvio padrão de velocidade

3. **Distribuições:**
   - Veículos parados
   - Veículos em velocidade lenta
   - Veículos em velocidade normal
   - Veículos em velocidade rápida

4. **KPIs Calculados:**
   - % de veículos por categoria de velocidade
   - Média de observações por veículo
   - Centro geográfico de operação

**Otimizações:**
```sql
-- Particionamento por data
PARTITION BY date_partition

-- Cluster para queries frequentes
CLUSTER BY line, period_of_day
```

## Fluxo de Dados End-to-End

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE BRT - FLUXO COMPLETO                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1️⃣ CAPTURA (Prefect Task)                                     │
│     ├─ API BRT: jeap.rio.rj.gov.br/je-api/api/v2/gps          │
│     ├─ Frequência: A cada 1 minuto                             │
│     ├─ Retry: 3 tentativas com delay de 30s                    │
│     └─ Output: DataFrame pandas                                │
│                                                                 │
│  2️⃣ AGREGAÇÃO (Prefect Task)                                   │
│     ├─ Buffer em memória: 10 capturas                          │
│     ├─ Trigger: Quando buffer completo                         │
│     └─ Output: CSV local                                       │
│                                                                 │
│  3️⃣ ARMAZENAMENTO (Prefect Task)                               │
│     ├─ Upload: CSV → GCS                                       │
│     ├─ Bucket: gs://brt-data-civitas/brt-data/                │
│     ├─ Retry: 2 tentativas                                     │
│     └─ Output: URI do arquivo                                  │
│                                                                 │
│  4️⃣ BRONZE LAYER (DBT Operation)                               │
│     ├─ Comando: dbt run-operation stage_external_sources       │
│     ├─ Ação: Cria/atualiza tabela externa                      │
│     └─ Output: brt_dataset.brt_gps_raw                         │
│                                                                 │
│  5️⃣ SILVER LAYER (DBT Run)                                     │
│     ├─ Comando: dbt run --models silver.*                      │
│     ├─ Modelo: stg_brt_gps_cleaned                             │
│     ├─ Materialização: View                                    │
│     └─ Output: brt_dataset_silver.stg_brt_gps_cleaned          │
│                                                                 │
│  6️⃣ GOLD LAYER (DBT Run)                                       │
│     ├─ Comando: dbt run --models gold.*                        │
│     ├─ Modelo: fct_brt_line_metrics                            │
│     ├─ Materialização: Table (particionada + cluster)          │
│     └─ Output: brt_dataset_gold.fct_brt_line_metrics           │
│                                                                 │
│  7️⃣ QUALIDADE (DBT Test)                                       │
│     ├─ Comando: dbt test                                       │
│     ├─ Testes: Schema + relacionamentos + valores              │
│     └─ Output: Relatório de qualidade                          │
│                                                                 │
│  8️⃣ DOCUMENTAÇÃO (DBT Docs)                                    │
│     ├─ Comando: dbt docs generate                              │
│     ├─ Ação: Gera site de documentação                         │
│     └─ Persiste: Descrições no BigQuery (+persist_docs)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes Técnicos

### Orquestração: Prefect v1.4.1

**Por que Prefect?**
- ✅ Interface web intuitiva
- ✅ Retry automático com backoff
- ✅ Monitoramento em tempo real
- ✅ Scheduling flexível
- ✅ Logs centralizados

**Estrutura do Flow:**
```python
Flow("BRT Data Pipeline")
  ├─ Task: capture_brt_data()
  ├─ Task: add_to_buffer()
  ├─ Task: generate_csv()
  ├─ Task: upload_to_gcs()
  ├─ Task: run_dbt_external_table()
  ├─ Task: run_dbt_transformations()
  └─ Task: run_dbt_tests()
```

### Transformação: DBT

**Por que DBT?**
- ✅ SQL como linguagem de transformação
- ✅ Testes de qualidade built-in
- ✅ Documentação automática
- ✅ Lineage de dados
- ✅ Versionamento de modelos

**Estrutura de Modelos:**
```
dbt_brt/models/
├── bronze/
│   └── sources.yml          # Definição de tabelas externas
├── silver/
│   ├── stg_brt_gps_cleaned.sql
│   └── schema.yml
└── gold/
    ├── fct_brt_line_metrics.sql
    └── schema.yml
```

### Armazenamento: GCP

**Google Cloud Storage:**
- Camada de staging para CSVs
- Bucket: `gs://brt-data-civitas/brt-data/`
- Formato: CSV com header
- Retenção: Configurável

**BigQuery:**
- Tabelas externas (Bronze)
- Views materializadas (Silver)
- Tabelas particionadas (Gold)
- Dataset: `brt_dataset`

## Decisões de Design

### 1. Por que Tabela Externa para Bronze?

**Vantagens:**
- ✅ Separação de armazenamento e computação
- ✅ Custo reduzido (storage em GCS é mais barato)
- ✅ Flexibilidade para processar dados brutos
- ✅ Histórico completo sem duplicação

**Trade-offs:**
- ⚠️ Performance de query inferior a tabelas nativas
- ⚠️ Requer GCS além do BigQuery

### 2. Por que View para Silver?

**Vantagens:**
- ✅ Sempre reflete dados mais recentes
- ✅ Sem custo de armazenamento adicional
- ✅ Queries otimizadas pelo BigQuery

**Trade-offs:**
- ⚠️ Recomputação a cada query

### 3. Por que Tabela Particionada para Gold?

**Vantagens:**
- ✅ Performance otimizada para queries por data
- ✅ Custo reduzido (scan apenas partições necessárias)
- ✅ Ideal para dashboards com filtros temporais

**Configuração:**
```sql
PARTITION BY date_partition
CLUSTER BY line, period_of_day
```

## Qualidade de Dados

### Níveis de Testes

1. **Testes de Schema (Bronze → Silver)**
   - Campos obrigatórios não nulos
   - Tipos de dados corretos
   - Valores dentro de ranges esperados

2. **Testes de Relacionamento (Silver)**
   - Unicidade de combinações
   - Referências válidas

3. **Testes de Negócio (Gold)**
   - Métricas dentro de limites esperados
   - Consistência de agregações

### Exemplo de Teste DBT

```yaml
# schema.yml
models:
  - name: stg_brt_gps_cleaned
    columns:
      - name: latitude
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: -23.0
              max_value: -22.7
```

## Monitoramento e Observabilidade

### Métricas de Pipeline

1. **Captura:**
   - Taxa de sucesso de requisições API
   - Tempo médio de resposta
   - Total de registros capturados

2. **Agregação:**
   - Tamanho dos arquivos CSV
   - Tempo de agregação
   - Registros por arquivo

3. **Transformação:**
   - Duração de cada modelo DBT
   - Linhas processadas
   - Testes falhados

4. **Qualidade:**
   - % de registros válidos
   - Taxa de duplicatas removidas
   - Cobertura de testes

### Alertas Recomendados

- ⚠️ API indisponível por > 5 minutos
- ⚠️ Buffer não completado em 15 minutos
- ⚠️ Upload GCS falhou
- ⚠️ Testes DBT falharam
- ⚠️ Latência > 2 horas entre captura e disponibilização Gold

## Escalabilidade

### Capacidade Atual

- **Frequência:** 1 captura/minuto
- **Agregação:** 10 minutos
- **Volume diário:** ~144 CSVs/dia
- **Registros/dia:** ~200-500 veículos × 144 capturas = ~28.800-72.000 registros

### Pontos de Escala

1. **Aumentar frequência:**
   - Modificar `CAPTURE_INTERVAL_SECONDS`
   - Ajustar schedule do Prefect

2. **Processar múltiplas linhas:**
   - Paralelizar capturas por linha
   - Usar Prefect mapping

3. **Otimizar custos BigQuery:**
   - Aumentar granularidade de particionamento
   - Adicionar mais clustering

## Custos Estimados (GCP Free Tier)

- **Cloud Storage:** ~1GB/mês → Grátis
- **BigQuery Storage:** ~2GB/mês → Grátis
- **BigQuery Queries:** ~10GB processados/mês → Grátis
- **Total:** $0/mês dentro do free tier

---

**Desenvolvido seguindo as melhores práticas de Data Engineering** 🚀
