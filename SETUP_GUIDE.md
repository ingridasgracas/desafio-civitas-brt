# 🚀 Guia de Setup - Desafio CIVITAS BRT Pipeline

**Projeto:** brt-pipeline-civitas  
**ID:** 881527434313  
**Status:** ✅ Dependências instaladas

---

## 📝 Checklist de Configuração

### ✅ 1. Projeto GCP Criado
- [x] Projeto: `brt-pipeline-civitas`
- [x] ID: `881527434313`
- [x] Arquivo `.env` configurado

### 🔧 2. Ativar APIs do Google Cloud

Acesse o [Console do GCP](https://console.cloud.google.com/apis/library?project=brt-pipeline-civitas) e ative:

- [ ] **Cloud Storage API** - Para armazenar CSVs
- [ ] **BigQuery API** - Para warehouse de dados
- [ ] **Cloud IAM API** - Para gerenciar permissões

**OU via gcloud CLI:**
```bash
gcloud config set project brt-pipeline-civitas
gcloud services enable storage-api.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable iam.googleapis.com
```

### 🔑 3. Criar Service Account e Credenciais

1. Acesse: https://console.cloud.google.com/iam-admin/serviceaccounts?project=brt-pipeline-civitas

2. Clique em **"+ CREATE SERVICE ACCOUNT"**

3. Preencha:
   - **Service account name:** `brt-pipeline-sa`
   - **Service account ID:** `brt-pipeline-sa`
   - **Description:** `Service Account para pipeline BRT`

4. Clique em **"CREATE AND CONTINUE"**

5. Adicione as seguintes roles:
   - `BigQuery Admin` (para criar datasets e tabelas)
   - `Storage Admin` (para criar e gerenciar buckets)
   - `Storage Object Admin` (para upload de arquivos)

6. Clique em **"CONTINUE"** e depois **"DONE"**

7. Agora clique na service account criada

8. Vá em **"KEYS"** → **"ADD KEY"** → **"Create new key"**

9. Escolha **JSON** e clique em **"CREATE"**

10. O arquivo JSON será baixado. **Renomeie para `gcp-credentials.json`**

11. Mova o arquivo para: `c:\Users\ingri\OneDrive\Documentos\projetos\code\desafio-civitas-brt\config\gcp-credentials.json`

### 📦 4. Criar Cloud Storage Bucket

**Opção A - Via Console:**
1. Acesse: https://console.cloud.google.com/storage/browser?project=brt-pipeline-civitas
2. Clique em **"CREATE BUCKET"**
3. Nome: `brt-data-civitas`
4. Location type: `Region`
5. Location: `us-east1` (ou southamerica-east1 para São Paulo)
6. Storage class: `Standard`
7. Access control: `Uniform`
8. Clique em **"CREATE"**

**Opção B - Via gcloud:**
```bash
gsutil mb -p brt-pipeline-civitas -c STANDARD -l southamerica-east1 gs://brt-data-civitas/
```

### 🗄️ 5. Criar Dataset no BigQuery

**Opção A - Via Console:**
1. Acesse: https://console.cloud.google.com/bigquery?project=brt-pipeline-civitas
2. No painel esquerdo, clique no ID do projeto
3. Clique nos três pontos → **"Create dataset"**
4. Dataset ID: `brt_dataset`
5. Location: `US` (ou `southamerica-east1`)
6. Clique em **"CREATE DATASET"**

**Opção B - Via bq CLI:**
```bash
bq mk --dataset --location=southamerica-east1 brt-pipeline-civitas:brt_dataset
```

### ✅ 6. Verificar Configuração

Execute o script de teste:
```bash
python test_gcp_config.py
```

Se tudo estiver OK, você verá:
```
✅ Credenciais GCP OK
✅ Projeto configurado: brt-pipeline-civitas
✅ Acesso ao Cloud Storage OK
✅ Acesso ao BigQuery OK
```

---

## 🚀 Próximos Passos Após Setup

### 1. Iniciar Prefect Server
```bash
docker-compose up -d
```

### 2. Acessar Dashboard do Prefect
```
http://localhost:4200
```

### 3. Executar Pipeline Manualmente
```bash
python pipeline/brt_flow.py
```

### 4. Verificar Dados no BigQuery
```sql
-- Ver dados brutos (Bronze)
SELECT * FROM `brt-pipeline-civitas.brt_dataset.bronze_brt_gps_raw` LIMIT 10;

-- Ver dados limpos (Silver)
SELECT * FROM `brt-pipeline-civitas.brt_dataset.silver_brt_gps_cleaned` LIMIT 10;

-- Ver métricas agregadas (Gold)
SELECT * FROM `brt-pipeline-civitas.brt_dataset.gold_brt_line_metrics` 
ORDER BY date_partition DESC LIMIT 10;
```

---

## 📚 Documentação Adicional

- [QUICKSTART.md](./QUICKSTART.md) - Início rápido
- [ARQUITETURA.md](./docs/ARQUITETURA.md) - Arquitetura do sistema
- [GCP_SETUP.md](./docs/GCP_SETUP.md) - Setup detalhado GCP
- [PREFECT_VISUAL_GUIDE.md](./docs/PREFECT_VISUAL_GUIDE.md) - Guia visual Prefect

---

## ⚠️ Troubleshooting

### Erro: "Default credentials not found"
→ Certifique-se de que `./config/gcp-credentials.json` existe e está configurado no `.env`

### Erro: "Permission denied"
→ Verifique se a Service Account tem as roles necessárias

### Erro: "Bucket not found"
→ Crie o bucket `brt-data-civitas` no Cloud Storage

### Erro: "Dataset not found"
→ Crie o dataset `brt_dataset` no BigQuery

---

## 💡 Dicas

1. Use a região `southamerica-east1` (São Paulo) para menor latência no Brasil
2. Monitore os custos no [Billing Dashboard](https://console.cloud.google.com/billing)
3. Configure alertas de orçamento para evitar surpresas
4. O tier gratuito do BigQuery oferece 10GB de armazenamento e 1TB de queries/mês
5. O tier gratuito do Cloud Storage oferece 5GB de armazenamento

---

**Status:** 🔄 Aguardando configuração de credenciais GCP
