# 🚀 Guia de Execução - Pipeline BRT CIVITAS

## ✅ Configuração Concluída

Parabéns! Seu ambiente está totalmente configurado:

- ✅ Python 3.12 + dependências instaladas
- ✅ Projeto GCP criado (`brt-pipeline-civitas`)
- ✅ Service Account com permissões (Editor)
- ✅ Credenciais JSON configuradas
- ✅ Bucket GCS criado (`brt-data-civitas`)
- ✅ Dataset BigQuery criado (`brt_dataset`)
- ✅ Pipeline Prefect testado

---

## 📋 Como Executar o Pipeline

### **Opção 1: Execução Manual (Teste único)**

Execute uma vez para testar:

```powershell
cd C:\Users\ingri\OneDrive\Documentos\projetos\code\desafio-civitas-brt
python -c "from pipeline.brt_flow import create_brt_pipeline_flow; flow = create_brt_pipeline_flow(); flow.run()"
```

### **Opção 2: Execução Agendada (Produção)**

Executa a cada 1 minuto automaticamente:

```powershell
cd C:\Users\ingri\OneDrive\Documentos\projetos\code\desafio-civitas-brt
python pipeline\brt_flow.py
```

**Pressione `Ctrl+C` para parar**

### **Opção 3: Executar apenas DBT (transformações)**

Se já tiver dados no GCS:

```powershell
cd C:\Users\ingri\OneDrive\Documentos\projetos\code\desafio-civitas-brt
cd dbt_brt
dbt run
dbt test
```

---

## 🔍 Verificar Resultados

### **1. Cloud Storage (Arquivos CSV)**

Acesse: https://console.cloud.google.com/storage/browser/brt-data-civitas?project=brt-pipeline-civitas

Você verá arquivos como:
```
brt-data/
  └── brt_gps_YYYY-MM-DD_HH-MM-SS.csv
```

### **2. BigQuery (Tabelas)**

Acesse: https://console.cloud.google.com/bigquery?project=brt-pipeline-civitas

**Tabelas criadas:**

| Camada | Tabela | Descrição |
|--------|--------|-----------|
| 🥉 Bronze | `bronze_brt_gps` | Tabela externa (raw data do GCS) |
| 🥈 Silver | `stg_brt_gps_cleaned` | Dados limpos e validados |
| 🥇 Gold | `fct_brt_line_metrics` | Métricas agregadas por linha |

### **3. Queries de Exemplo**

```sql
-- Ver dados brutos
SELECT * FROM `brt-pipeline-civitas.brt_dataset.bronze_brt_gps` LIMIT 100;

-- Ver dados limpos
SELECT * FROM `brt-pipeline-civitas.brt_dataset.stg_brt_gps_cleaned` LIMIT 100;

-- Métricas por linha
SELECT 
    line,
    date_partition,
    total_vehicles,
    avg_speed_kmh,
    dist_normal,
    dist_slow,
    dist_stopped
FROM `brt-pipeline-civitas.brt_dataset.fct_brt_line_metrics`
ORDER BY date_partition DESC, line;
```

---

## 🛠️ Troubleshooting

### **Erro: API BRT não acessível**

```
ERROR | brt_api_capture:fetch_data:57 - Erro ao capturar dados da API
```

✅ **Solução:** A API pode estar instável. O pipeline tem retry automático e continuará tentando.

### **Erro: Credenciais GCP**

```
ERROR | Credentials not found
```

✅ **Solução:**
```powershell
# Verificar se o arquivo existe
ls config\gcp-credentials.json

# Reconfigurar se necessário
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\ingri\OneDrive\Documentos\projetos\code\desafio-civitas-brt\config\gcp-credentials.json"
```

### **Erro: Bucket ou Dataset não existe**

✅ **Solução:**
```powershell
python scripts\create_gcp_resources.py
```

---

## 📊 Monitoramento

### **Logs do Pipeline**

Os logs são salvos em:
```
logs/
  ├── brt_api_YYYY-MM-DD.log
  ├── gcs_upload_YYYY-MM-DD.log
  └── dbt_run_YYYY-MM-DD.log
```

### **Status do Buffer**

O pipeline agrega dados a cada **10 minutos** (6 capturas de 1 em 1 minuto).

Você verá nos logs:
```
Buffer status: 3/6 capturas  ⏳ Aguardando mais dados
Buffer status: 6/6 capturas  ✅ Completo! Gerando CSV
```

---

## 🎯 Próximos Passos Recomendados

1. **Testar com dados reais:**
   - Aguarde a API BRT ficar disponível
   - Deixe rodar por alguns ciclos para acumular dados

2. **Visualização:**
   - Conecte o Looker Studio ao BigQuery
   - Crie dashboards com as métricas da tabela `fct_brt_line_metrics`

3. **Otimizações:**
   - Ajuste `aggregation_minutes` no `.env` conforme necessário
   - Configure alertas no GCP Monitoring

4. **Produção:**
   - Deploy em Cloud Run ou Compute Engine
   - Configure Cloud Scheduler para execução automática

---

## 📞 Suporte

**Documentação do Projeto:**
- `README.md` - Visão geral
- `ARCHITECTURE.md` - Arquitetura detalhada
- `docs/GCP_SETUP.md` - Setup do GCP
- `docs/EXTERNAL_TABLES_GUIDE.md` - Guia de tabelas externas

**Links Úteis:**
- Prefect 1.4.1: https://docs-v1.prefect.io/
- DBT: https://docs.getdbt.com/
- BigQuery: https://cloud.google.com/bigquery/docs

---

## 🎉 Projeto Pronto!

Você completou o setup do **Pipeline BRT CIVITAS**!

✅ Todos os recursos estão criados  
✅ Pipeline está funcional  
✅ Testes passaram  

**Boa sorte no desafio! 🚀**
