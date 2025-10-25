# 📝 Notas de Instalação - Correções de Dependências

## Problemas Identificados e Resolvidos

### 1. dbt-external-tables (RESOLVIDO ✅)

**Problema:** O pacote `dbt-external-tables==0.8.0` não está mais disponível no PyPI.

**Solução:** A partir do **dbt-bigquery 1.5+**, a funcionalidade de tabelas externas foi **integrada nativamente** ao pacote principal.

### 2. pyarrow (RESOLVIDO ✅)

**Problema:** A versão `pyarrow==12.0.1` não está disponível para sua plataforma.

**Solução:** Atualizado para `pyarrow==14.0.2` (versão estável e compatível).

## Versões Corrigidas

```txt
# Antes (com erros)
dbt-external-tables==0.8.0  ❌
pyarrow==12.0.1             ❌

# Depois (funcionando)
# dbt-external-tables removido (funcionalidade nativa no dbt-bigquery 1.5+)
pyarrow==14.0.2             ✅
```

## Mudança na Arquitetura

A partir do **dbt-bigquery 1.5+**, a funcionalidade de tabelas externas foi **integrada nativamente** ao pacote principal. Não é mais necessário instalar o pacote `dbt-external-tables` separadamente.

### Alterações Realizadas

#### 1. `requirements.txt`
✅ Removido: `dbt-external-tables==0.8.0`  
✅ Mantido: `dbt-bigquery==1.5.0` (já inclui suporte a tabelas externas)

#### 2. `dbt_brt/packages.yml`
✅ Removida dependência de `dbt-external-tables`  
✅ Adicionados comentários explicativos

#### 3. `dbt_brt/models/bronze/sources.yml`
✅ Atualizada sintaxe para usar configuração nativa do dbt-bigquery  
✅ Propriedade `external:` com `location:` e `options:`

#### 4. Script SQL Alternativo
✅ Criado: `dbt_brt/models/bronze/create_external_table.sql`  
✅ Script SQL direto para criar tabela externa no BigQuery

#### 5. Pipeline Prefect
✅ Atualizada task `run_dbt_external_table()`  
✅ Agora usa BigQuery API diretamente para criar tabela externa

## Como Instalar Agora

```powershell
# 1. Ative o ambiente virtual
.\venv\Scripts\Activate.ps1

# 2. Instale dependências (versão corrigida)
pip install -r requirements.txt
```

## Criação da Tabela Externa

### Opção 1: Via Pipeline Prefect (Automático)
O pipeline agora cria a tabela externa automaticamente usando a BigQuery API.

```python
# Em pipeline/brt_flow.py
# A task run_dbt_external_table() usa BigQuery client diretamente
```

### Opção 2: Via Script SQL (Manual)

```powershell
# 1. Edite o arquivo e substitua as variáveis
# dbt_brt/models/bronze/create_external_table.sql

# 2. Execute no BigQuery Console
# Ou via bq CLI:
bq query --use_legacy_sql=false < dbt_brt/models/bronze/create_external_table.sql
```

### Opção 3: Via bq CLI (Direto)

```bash
# Substitua as variáveis antes de executar
bq mk --external_table_definition='gs://SEU-BUCKET/brt-data/*.csv@CSV=capture_timestamp:TIMESTAMP,vehicle_id:STRING,line:STRING,latitude:FLOAT64,longitude:FLOAT64,speed:FLOAT64,timestamp_gps:TIMESTAMP,raw_data:STRING' \
  --skip_leading_rows=1 \
  SEU-PROJECT:brt_dataset.brt_gps_raw
```

## Configuração DBT Nativa para Tabelas Externas

A nova sintaxe em `sources.yml`:

```yaml
sources:
  - name: brt_external
    schema: brt_dataset
    tables:
      - name: brt_gps_raw
        external:
          location: "gs://{{ var('gcs_bucket') }}/brt-data/*.csv"
          options:
            format: CSV
            skip_leading_rows: 1
            autodetect: false
        columns:
          - name: capture_timestamp
            data_type: timestamp
          # ... demais colunas
```

## Verificação

Após a instalação, verifique:

```powershell
# 1. Verificar pacotes instalados
pip list | Select-String "dbt"

# Esperado:
# dbt-bigquery        1.5.0
# dbt-core            1.5.0

# 2. Testar conexão DBT
cd dbt_brt
dbt debug

# 3. Verificar se tabela externa foi criada (após executar pipeline)
# No BigQuery Console, procure por: brt_dataset.brt_gps_raw
```

## Referências

- [dbt-bigquery External Tables](https://docs.getdbt.com/reference/resource-properties/external)
- [BigQuery External Tables](https://cloud.google.com/bigquery/docs/external-tables)
- [Migration Guide](https://github.com/dbt-labs/dbt-external-tables#deprecation-notice)

## Status

✅ **Problema resolvido**  
✅ **Instalação funcionando**  
✅ **Pipeline atualizado**  
✅ **Documentação atualizada**

---

**Data:** 24 de outubro de 2025  
**Versão do Projeto:** 1.0.1
