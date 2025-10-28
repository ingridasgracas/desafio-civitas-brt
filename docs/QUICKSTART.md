#  Guia de Início Rápido - Pipeline BRT

Este guia fornece instruções passo a passo para colocar o pipeline em funcionamento o mais rápido possível.

## ⏱ Tempo Estimado: 30 minutos

##  Checklist Pré-execução

- [ ] Python 3.8+ instalado
- [ ] Docker Desktop instalado e rodando
- [ ] Conta Google Cloud Platform criada
- [ ] Git instalado

##  Passos Rápidos

### 1. Clone e Configure (5 min)

```powershell
# Clone o repositório
git clone https://github.com/seu-usuario/desafio-civitas-brt.git
cd desafio-civitas-brt

# Crie ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instale dependências
pip install -r requirements.txt
```

### 2. Configure GCP (10 min)

#### 2.1. Crie Projeto GCP

1. Acesse: https://console.cloud.google.com/
2. Clique em "Novo Projeto"
3. Nome: `brt-pipeline-civitas`
4. Anote o Project ID

#### 2.2. Ative APIs

```powershell
# Via gcloud CLI (se instalado)
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com

# OU via console:
# https://console.cloud.google.com/apis/library
```

#### 2.3. Crie Service Account

1. Acesse: https://console.cloud.google.com/iam-admin/serviceaccounts
2. "Criar Conta de Serviço"
3. Nome: `brt-pipeline-sa`
4. Adicione roles:
   - BigQuery Admin
   - Storage Admin
5. Crie chave JSON
6. Baixe e salve em `config/gcp-credentials.json`

#### 2.4. Crie Recursos GCP

```powershell
# Bucket GCS
gcloud storage buckets create gs://brt-data-civitas --location=US

# Dataset BigQuery
bq mk --location=US brt_dataset
```

### 3. Configure Variáveis de Ambiente (2 min)

```powershell
# Copie o template
Copy-Item .env.example .env

# Edite .env e preencha:
# GCP_PROJECT_ID=seu-project-id
# GCS_BUCKET_NAME=brt-data-civitas
# GCP_CREDENTIALS_PATH=./config/gcp-credentials.json
```

### 4. Inicie Prefect Server (3 min)

```powershell
# Suba os containers
docker-compose up -d

# Aguarde 30 segundos
Start-Sleep -Seconds 30

# Verifique se está rodando
docker-compose ps
```

Acesse: http://localhost:4200

### 5. Instale Dependências DBT (2 min)

```powershell
cd dbt_brt
dbt deps
cd ..
```

### 6. Teste Individual de Componentes (5 min)

#### Teste 1: Captura da API

```powershell
python scripts/brt_api_capture.py
```

**Esperado:** 
```
 Dados capturados: X registros
  vehicle_id | line | latitude | longitude | speed
```

#### Teste 2: Upload GCS (teste)

```powershell
python scripts/gcs_manager.py
```

**Esperado:**
```
 Upload bem-sucedido: gs://brt-data-civitas/test/...
```

#### Teste 3: DBT Connection

```powershell
cd dbt_brt
dbt debug
```

**Esperado:**
```
 Connection test: OK
```

### 7. Execute Pipeline Completo (3 min)

```powershell
# Execute o flow
python pipeline/brt_flow.py
```

**O que acontece:**
1.  Captura dados da API BRT
2.  Adiciona ao buffer (precisa rodar 10x para gerar CSV)
3.  Gera CSV (após 10 capturas)
4.  Upload para GCS
5.  Cria tabela externa BigQuery
6.  Executa transformações Silver e Gold
7.  Executa testes de qualidade

##  Verificação de Sucesso

### Verifique no Prefect UI

Acesse: http://localhost:4200

- [ ] Flow aparece na lista
- [ ] Última execução foi sucesso
- [ ] Todas as tasks completaram

### Verifique no GCS

```powershell
gcloud storage ls gs://brt-data-civitas/brt-data/
```

- [ ] Arquivos CSV presentes

### Verifique no BigQuery

Acesse: https://console.cloud.google.com/bigquery

Execute:
```sql
-- Verifica tabela Bronze
SELECT COUNT(*) FROM `brt_dataset.brt_gps_raw` LIMIT 10;

-- Verifica view Silver
SELECT COUNT(*) FROM `brt_dataset_silver.stg_brt_gps_cleaned` LIMIT 10;

-- Verifica tabela Gold
SELECT * FROM `brt_dataset_gold.fct_brt_line_metrics` ORDER BY date_partition DESC LIMIT 10;
```

##  Próximos Passos

### Executar Pipeline Continuamente

```powershell
# Registre o flow no Prefect Server
python pipeline/brt_flow.py register

# O flow executará automaticamente a cada minuto
```

### Acessar Documentação DBT

```powershell
cd dbt_brt
dbt docs generate
dbt docs serve
```

Acesse: http://localhost:8080

### Criar Dashboard

Use BigQuery + Looker Studio:
1. Acesse: https://lookerstudio.google.com/
2. Crie nova fonte de dados → BigQuery
3. Selecione: `brt_dataset_gold.fct_brt_line_metrics`
4. Crie visualizações:
   - Veículos ativos por linha
   - Velocidade média por período
   - Mapa de calor de operações

##  Problemas Comuns

### Erro: "Permission denied" no GCP

**Solução:**
```powershell
# Verifique se as credenciais estão corretas
$env:GOOGLE_APPLICATION_CREDENTIALS = ".\config\gcp-credentials.json"
```

### Erro: "Prefect Server não conecta"

**Solução:**
```powershell
# Reinicie os containers
docker-compose restart

# Verifique logs
docker-compose logs prefect-server
```

### Erro: "API BRT timeout"

**Solução:**
- API pode estar temporariamente indisponível
- Aguarde alguns minutos e tente novamente
- Pipeline tem retry automático (3 tentativas)

### Erro: "DBT não encontra tabela"

**Solução:**
```powershell
# Execute manualmente a criação da tabela externa
cd dbt_brt
dbt run-operation stage_external_sources
```

##  Dashboard de Monitoramento

Após executar, você terá:

### Prefect UI (http://localhost:4200)
- Status do pipeline em tempo real
- Histórico de execuções
- Logs detalhados

### DBT Docs (http://localhost:8080)
- Documentação de modelos
- Lineage de dados
- Schema das tabelas

### BigQuery Console
- Dados em tempo real
- Queries SQL
- Análises ad-hoc

##  Dicas

1. **Execute múltiplas vezes:**
   - Pipeline precisa rodar 10x para gerar primeiro CSV
   - Use loop para testar:
   ```powershell
   for ($i=1; $i -le 10; $i++) {
       python pipeline/brt_flow.py
       Start-Sleep -Seconds 60
   }
   ```

2. **Monitore custos GCP:**
   - Acesse: https://console.cloud.google.com/billing
   - Configure alertas de budget

3. **Backup de dados:**
   - CSVs são salvos localmente em `data/`
   - GCS mantém histórico completo

##  Recursos Adicionais

- [Documentação Completa](../README.md)
- [Arquitetura Detalhada](./ARQUITETURA.md)
- [Prefect Docs](https://docs-v1.prefect.io/)
- [DBT Docs](https://docs.getdbt.com/)
- [BigQuery Docs](https://cloud.google.com/bigquery/docs)

---

**Pronto! Seu pipeline está funcionando! **

Se encontrar problemas, consulte a seção de Troubleshooting no README principal ou abra uma issue no GitHub.
