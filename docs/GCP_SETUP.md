#  Configuração Google Cloud Platform

## Passo 1: Criar Projeto GCP

### Via Console Web

1. Acesse: https://console.cloud.google.com/
2. Clique no seletor de projetos (topo da página)
3. Clique em "Novo Projeto"
4. Preencha:
   - **Nome do Projeto:** `BRT Pipeline CIVITAS`
   - **ID do Projeto:** `brt-pipeline-civitas` (ou outro único)
5. Clique em "Criar"

### Via gcloud CLI

```bash
gcloud projects create brt-pipeline-civitas --name="BRT Pipeline CIVITAS"
gcloud config set project brt-pipeline-civitas
```

## Passo 2: Ativar APIs Necessárias

### Via Console Web

1. Acesse: https://console.cloud.google.com/apis/library
2. Pesquise e ative:
   - **BigQuery API**
   - **Cloud Storage API**

### Via gcloud CLI

```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
```

## Passo 3: Criar Service Account

### Via Console Web

1. Acesse: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Clique em "Criar Conta de Serviço"
3. Preencha:
   - **Nome:** `BRT Pipeline Service Account`
   - **ID:** `brt-pipeline-sa`
   - **Descrição:** `Service Account para pipeline BRT`
4. Clique em "Criar e continuar"
5. Adicione roles:
   - `BigQuery Admin`
   - `Storage Admin`
6. Clique em "Continuar" e depois em "Concluir"

### Via gcloud CLI

```bash
# Cria Service Account
gcloud iam service-accounts create brt-pipeline-sa \
    --display-name="BRT Pipeline Service Account" \
    --description="Service Account para pipeline BRT"

# Adiciona roles
gcloud projects add-iam-policy-binding brt-pipeline-civitas \
    --member="serviceAccount:brt-pipeline-sa@brt-pipeline-civitas.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding brt-pipeline-civitas \
    --member="serviceAccount:brt-pipeline-sa@brt-pipeline-civitas.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

## Passo 4: Criar e Baixar Chave JSON

### Via Console Web

1. Na página de Service Accounts, clique na conta criada
2. Vá para a aba "Chaves"
3. Clique em "Adicionar Chave" → "Criar nova chave"
4. Selecione tipo: **JSON**
5. Clique em "Criar"
6. O arquivo será baixado automaticamente
7. Mova o arquivo para: `config/gcp-credentials.json`

### Via gcloud CLI

```bash
gcloud iam service-accounts keys create config/gcp-credentials.json \
    --iam-account=brt-pipeline-sa@brt-pipeline-civitas.iam.gserviceaccount.com
```

## Passo 5: Criar Bucket GCS

### Via Console Web

1. Acesse: https://console.cloud.google.com/storage
2. Clique em "Criar Bucket"
3. Preencha:
   - **Nome:** `brt-data-civitas` (deve ser globalmente único)
   - **Localização:** `Multi-region` → `US`
   - **Classe de armazenamento:** `Standard`
   - **Controle de acesso:** `Uniforme`
4. Clique em "Criar"

### Via gcloud CLI

```bash
gcloud storage buckets create gs://brt-data-civitas \
    --location=US \
    --uniform-bucket-level-access
```

### Via gsutil

```bash
gsutil mb -l US -b on gs://brt-data-civitas
```

## Passo 6: Criar Dataset BigQuery

### Via Console Web

1. Acesse: https://console.cloud.google.com/bigquery
2. No explorador, clique no seu projeto
3. Clique nos três pontos → "Criar conjunto de dados"
4. Preencha:
   - **ID do conjunto de dados:** `brt_dataset`
   - **Localização:** `US (multiple regions in United States)`
   - **Expiração padrão de tabela:** `Nunca`
5. Clique em "Criar conjunto de dados"

### Via bq CLI

```bash
bq mk --location=US --dataset brt_dataset
```

## Passo 7: Configurar Variáveis de Ambiente

Edite o arquivo `.env`:

```bash
# Google Cloud Platform
GCP_PROJECT_ID=brt-pipeline-civitas
GCS_BUCKET_NAME=brt-data-civitas
GCP_CREDENTIALS_PATH=./config/gcp-credentials.json

# BigQuery
BQ_DATASET=brt_dataset
```

## Passo 8: Testar Configuração

### Teste Python

```python
# test_gcp.py
from google.cloud import storage, bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './config/gcp-credentials.json'

# Testa Storage
storage_client = storage.Client(project='brt-pipeline-civitas')
bucket = storage_client.bucket('brt-data-civitas')
print(f" Bucket acessível: {bucket.name}")

# Testa BigQuery
bq_client = bigquery.Client(project='brt-pipeline-civitas')
dataset_ref = bq_client.dataset('brt_dataset')
dataset = bq_client.get_dataset(dataset_ref)
print(f" Dataset acessível: {dataset.dataset_id}")

print("\n Configuração GCP OK!")
```

Execute:
```bash
python test_gcp.py
```

### Teste gcloud

```bash
# Lista buckets
gcloud storage ls

# Lista datasets
bq ls

# Verifica Service Account
gcloud iam service-accounts list
```

## Custos Estimados (Free Tier)

### Cloud Storage
- **Free Tier:** 5 GB/mês
- **Uso estimado:** ~500 MB/mês
- **Custo:** $0/mês

### BigQuery
- **Storage Free Tier:** 10 GB
- **Query Free Tier:** 1 TB/mês processado
- **Uso estimado:** ~2 GB storage, ~10 GB queries/mês
- **Custo:** $0/mês

### Total Estimado: $0/mês
*Dentro do Google Cloud Free Tier*

## Monitoramento de Custos

### Configurar Alertas

1. Acesse: https://console.cloud.google.com/billing/budgets
2. Clique em "Criar orçamento"
3. Configure:
   - **Orçamento mensal:** $5 (como segurança)
   - **Alertas:** 50%, 90%, 100%
4. Adicione email para notificações

## Limpeza (Opcional)

Se precisar deletar recursos:

```bash
# Deleta bucket
gcloud storage rm -r gs://brt-data-civitas

# Deleta dataset
bq rm -r -d brt_dataset

# Deleta Service Account
gcloud iam service-accounts delete brt-pipeline-sa@brt-pipeline-civitas.iam.gserviceaccount.com

# Deleta projeto (CUIDADO!)
gcloud projects delete brt-pipeline-civitas
```

## Segurança

### Boas Práticas

1. **Nunca commite credenciais**
   - `.gitignore` já está configurado
   - Verifique: `config/gcp-credentials.json` está ignorado

2. **Rotação de chaves**
   - Troque chaves a cada 90 dias
   - Delete chaves antigas

3. **Princípio do menor privilégio**
   - Use apenas os roles necessários
   - Evite `Owner` ou `Editor`

4. **Auditoria**
   - Ative logs de auditoria
   - Monitore acessos

## Troubleshooting

### Erro: "Permission Denied"

```bash
# Verifique se GOOGLE_APPLICATION_CREDENTIALS está definido
echo $GOOGLE_APPLICATION_CREDENTIALS  # Linux/Mac
$env:GOOGLE_APPLICATION_CREDENTIALS   # Windows PowerShell

# Verifique permissões
gcloud projects get-iam-policy brt-pipeline-civitas
```

### Erro: "Bucket already exists"

Nomes de bucket são globalmente únicos. Tente outro nome:
```bash
# Exemplo: adicione seu username
gcloud storage buckets create gs://brt-data-civitas-seunome
```

### Erro: "API not enabled"

```bash
# Liste APIs ativas
gcloud services list --enabled

# Ative APIs faltantes
gcloud services enable bigquery.googleapis.com storage.googleapis.com
```

---

**Configuração GCP completa! **

Próximo passo: [Voltar ao Guia de Início Rápido](./QUICKSTART.md)
