# 🔧 Guia Rápido: Criação de Tabelas Externas no BigQuery

## Contexto

**Mudança importante:** O pacote `dbt-external-tables` foi descontinuado. A partir do `dbt-bigquery 1.5+`, as tabelas externas são criadas usando funcionalidades nativas.

## ✅ Solução Implementada

### Método 1: Via Pipeline Prefect (Recomendado)

O pipeline cria automaticamente a tabela externa usando a BigQuery API.

```python
# Já implementado em pipeline/brt_flow.py
# Executa automaticamente quando você roda:
python pipeline/brt_flow.py
```

### Método 2: Script SQL Manual

**Passo 1:** Edite o arquivo `dbt_brt/models/bronze/create_external_table.sql`

Substitua:
- `${GCP_PROJECT_ID}` → Seu ID do projeto GCP
- `${GCS_BUCKET_NAME}` → Nome do seu bucket

**Passo 2:** Execute no BigQuery Console

1. Acesse: https://console.cloud.google.com/bigquery
2. Abra o editor SQL
3. Cole e execute o script

**OU via bq CLI:**

```bash
# Substitua as variáveis primeiro!
cat dbt_brt/models/bronze/create_external_table.sql | \
  sed "s/\${GCP_PROJECT_ID}/seu-projeto/g" | \
  sed "s/\${GCS_BUCKET_NAME}/seu-bucket/g" | \
  bq query --use_legacy_sql=false
```

### Método 3: Comando bq mk (Linha de Comando)

```bash
# Template (substitua as variáveis)
bq mk \
  --external_table_definition=gs://SEU-BUCKET/brt-data/*.csv@CSV=capture_timestamp:TIMESTAMP,vehicle_id:STRING,line:STRING,latitude:FLOAT64,longitude:FLOAT64,speed:FLOAT64,timestamp_gps:TIMESTAMP,raw_data:STRING \
  --skip_leading_rows=1 \
  --description="Tabela externa BRT GPS - Camada Bronze" \
  SEU-PROJECT:brt_dataset.brt_gps_raw
```

**Exemplo real:**
```bash
bq mk \
  --external_table_definition=gs://brt-data-civitas/brt-data/*.csv@CSV=capture_timestamp:TIMESTAMP,vehicle_id:STRING,line:STRING,latitude:FLOAT64,longitude:FLOAT64,speed:FLOAT64,timestamp_gps:TIMESTAMP,raw_data:STRING \
  --skip_leading_rows=1 \
  --description="Tabela externa BRT GPS - Camada Bronze" \
  brt-pipeline-civitas:brt_dataset.brt_gps_raw
```

## 🧪 Verificação

### 1. Verificar se tabela existe

```sql
-- Execute no BigQuery Console
SELECT 
  table_name, 
  table_type,
  ddl
FROM `SEU-PROJECT.brt_dataset.INFORMATION_SCHEMA.TABLES`
WHERE table_name = 'brt_gps_raw';
```

### 2. Testar query na tabela

```sql
SELECT 
  COUNT(*) as total_rows,
  MIN(capture_timestamp) as first_capture,
  MAX(capture_timestamp) as last_capture
FROM `SEU-PROJECT.brt_dataset.brt_gps_raw`;
```

### 3. Ver amostra dos dados

```sql
SELECT *
FROM `SEU-PROJECT.brt_dataset.brt_gps_raw`
ORDER BY capture_timestamp DESC
LIMIT 10;
```

## 📝 Sintaxe DBT Atualizada

Arquivo: `dbt_brt/models/bronze/sources.yml`

```yaml
version: 2

sources:
  - name: brt_external
    schema: brt_dataset
    tables:
      - name: brt_gps_raw
        description: "Tabela externa com dados GPS dos veículos BRT"
        
        # Configuração nativa do dbt-bigquery para tabelas externas
        external:
          location: "gs://{{ var('gcs_bucket') }}/brt-data/*.csv"
          options:
            format: CSV
            skip_leading_rows: 1
            autodetect: false
        
        columns:
          - name: capture_timestamp
            data_type: timestamp
            description: "Timestamp de captura"
          # ... demais colunas
```

## ❓ Troubleshooting

### Erro: "Table not found"

**Causa:** Tabela externa ainda não foi criada  
**Solução:** Execute um dos métodos acima para criar

### Erro: "Permission denied"

**Causa:** Service Account sem permissões  
**Solução:** Adicione role `BigQuery Admin` no IAM

### Erro: "No files match pattern"

**Causa:** Bucket vazio ou padrão de arquivo incorreto  
**Solução:** 
1. Verifique se existem CSVs em `gs://seu-bucket/brt-data/`
2. Execute o pipeline para gerar dados primeiro

### Erro: "Schema mismatch"

**Causa:** Colunas do CSV não correspondem ao schema  
**Solução:** Verifique se o CSV tem exatamente 8 colunas:
```
capture_timestamp,vehicle_id,line,latitude,longitude,speed,timestamp_gps,raw_data
```

## 📚 Referências

- [BigQuery External Tables](https://cloud.google.com/bigquery/docs/external-tables)
- [dbt-bigquery External Config](https://docs.getdbt.com/reference/resource-properties/external)
- [BigQuery bq CLI](https://cloud.google.com/bigquery/docs/bq-command-line-tool)

## ✅ Checklist

- [ ] Bucket GCS criado e com CSVs
- [ ] Dataset BigQuery criado (`brt_dataset`)
- [ ] Credenciais configuradas em `.env`
- [ ] Tabela externa criada (via um dos 3 métodos)
- [ ] Query de verificação executada com sucesso
- [ ] Pipeline Prefect funcionando

---

**Atualizado:** 24 de outubro de 2025  
**Versão do Pipeline:** 1.0.1
