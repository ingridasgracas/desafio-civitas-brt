# 📊 Relatório Final - Pipeline BRT CIVITAS

**Candidato:** Ingrid Lima  
**Data:** 24 de Outubro de 2025  
**Projeto:** Pipeline ELT - Dados GPS do BRT Rio de Janeiro

---

## 🎯 Objetivo

Desenvolver um pipeline de dados automatizado que:
1. Capture dados GPS dos ônibus BRT em tempo real
2. Armazene no Google Cloud Storage
3. Crie tabelas no BigQuery
4. Transforme dados seguindo arquitetura Medallion (Bronze → Silver → Gold)

---

## 🏗️ Arquitetura Implementada

### **Componentes**

```
┌─────────────────┐
│   API BRT RJ    │
│  (Tempo Real)   │
└────────┬────────┘
         │
         ↓ HTTP Request (1/min)
┌─────────────────┐
│  Python Script  │
│ (brt_api_capture)│
└────────┬────────┘
         │
         ↓ Agregação (10 min)
┌─────────────────┐
│  Buffer Local   │
│ (CSV Generator) │
└────────┬────────┘
         │
         ↓ Upload
┌─────────────────┐
│ Cloud Storage   │
│ (GCS Bucket)    │
└────────┬────────┘
         │
         ↓ External Table
┌─────────────────┐
│   BigQuery      │
│  🥉 Bronze      │ ← Dados brutos (tabela externa)
│  🥈 Silver      │ ← Dados limpos (view DBT)
│  🥇 Gold        │ ← Métricas agregadas (tabela DBT)
└─────────────────┘
```

### **Orquestração**

- **Prefect 1.4.1**: Agendamento e monitoramento
- **Execução**: A cada 1 minuto
- **Agregação**: Gera CSV a cada 10 minutos (6 capturas)

---

## 💻 Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|-----------|
| **Python** | 3.12 | Linguagem principal |
| **Prefect** | 1.4.1 | Orquestração de pipeline |
| **DBT** | 1.5.0 | Transformação de dados (ELT) |
| **Google Cloud Storage** | - | Armazenamento de CSV |
| **BigQuery** | - | Data Warehouse |
| **Pandas** | 2.2.0 | Manipulação de dados |
| **Docker** | 28.4.0 | Containerização (opcional) |

---

## 📁 Estrutura do Projeto

```
desafio-civitas-brt/
├── pipeline/
│   └── brt_flow.py              # Flow principal Prefect
├── scripts/
│   ├── brt_api_capture.py       # Captura API
│   ├── brt_data_aggregator.py   # Agregação 10min
│   ├── gcs_manager.py           # Upload GCS
│   └── generate_mock_data.py    # Dados de teste
├── dbt_brt/
│   ├── models/
│   │   ├── bronze/
│   │   │   └── sources.yml      # Tabela externa GCS
│   │   ├── silver/
│   │   │   └── stg_brt_gps_cleaned.sql
│   │   └── gold/
│   │       └── fct_brt_line_metrics.sql
│   └── tests/
│       └── 27 testes de qualidade
├── config/
│   └── gcp-credentials.json     # Service Account
├── .env                         # Variáveis de ambiente
└── docs/                        # Documentação completa
```

---

## 🎨 Camadas da Arquitetura Medallion

### 🥉 **Camada Bronze** (Raw Data)
- **Tabela:** `bronze_brt_gps`
- **Tipo:** External Table (aponta para CSV no GCS)
- **Dados:** Brutos, sem transformação
- **Schema:**
  ```sql
  - dataHora (STRING)
  - ordem (STRING) 
  - linha (STRING)
  - latitude (FLOAT64)
  - longitude (FLOAT64)
  - velocidade (FLOAT64)
  ```

### 🥈 **Camada Silver** (Cleaned Data)
- **View:** `stg_brt_gps_cleaned`
- **Transformações:**
  - ✅ Conversão de tipos (timestamp, numeric)
  - ✅ Validação de coordenadas GPS (Rio de Janeiro)
  - ✅ Remoção de duplicatas
  - ✅ Campos derivados (data, hora, dia da semana)
  - ✅ Categorização de velocidade (parado/lento/normal/rápido)
  - ✅ Identificação de período do dia

### 🥇 **Camada Gold** (Business Metrics)
- **Tabela:** `fct_brt_line_metrics`
- **Features:**
  - Particionada por data
  - Clusterizada por linha e período
  - Agregações por linha BRT:
    - Velocidade média
    - Total de veículos
    - Distribuição por categoria de velocidade
    - Métricas por período do dia

---

## ✅ Testes de Qualidade (27 testes)

### **Testes Bronze:**
- Campos obrigatórios não nulos
- Unicidade de registros
- Valores aceitos para linha BRT

### **Testes Silver:**
- Coordenadas dentro do Rio de Janeiro
- Velocidade em range válido (0-120 km/h)
- Timestamps válidos
- Sem duplicatas

### **Testes Gold:**
- Integridade referencial
- Agregações corretas
- Particionamento funcional

---

## 📊 Resultados

### **Infraestrutura GCP Criada:**
- ✅ Projeto: `brt-pipeline-civitas`
- ✅ Bucket GCS: `brt-data-civitas`
- ✅ Dataset BigQuery: `brt_dataset`
- ✅ Service Account com permissões

### **Pipeline Funcional:**
- ✅ Captura automática (1 em 1 minuto)
- ✅ Agregação inteligente (10 minutos)
- ✅ Upload automatizado para GCS
- ✅ Transformações DBT executando
- ✅ Testes de qualidade passando

### **Monitoramento:**
- ✅ Prefect Server rodando
- ✅ Interface web em http://localhost:8080
- ✅ Logs detalhados
- ✅ Retry automático em falhas

---

## ⚠️ Desafios Encontrados

### **1. API BRT Instável**
- **Problema:** API do governo frequentemente indisponível
- **Solução:** 
  - Retry automático (3 tentativas)
  - Tratamento de erros com SKIP
  - Gerador de dados mockados para testes

### **2. Compatibilidade de Versões**
- **Problema:** pyarrow incompatível com Python 3.12
- **Solução:** Upgrade para pyarrow 14.0.2+

### **3. Prefect 1.x vs 2.x**
- **Problema:** Documentação misturada entre versões
- **Solução:** Ajustes específicos para v1.4.1

---

## 🚀 Como Executar

```powershell
# 1. Clonar repositório
cd desafio-civitas-brt

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar credenciais GCP
# Editar .env com PROJECT_ID e credenciais

# 4. Criar recursos GCP
python scripts/create_gcp_resources.py

# 5. Executar pipeline
python pipeline/brt_flow.py

# 6. (Opcional) Iniciar Prefect UI
prefect server start
# Acessar: http://localhost:8080
```

---

## 📈 Próximos Passos (Melhorias Futuras)

1. **Visualização:**
   - Dashboard no Looker Studio
   - Mapa de calor com posições dos ônibus
   - Gráficos de velocidade média por linha

2. **Alertas:**
   - Notificação de ônibus parados por muito tempo
   - Alerta de atrasos por linha
   - Monitoramento de falhas da API

3. **Otimizações:**
   - Streaming com Pub/Sub
   - Processamento em tempo real com Dataflow
   - Cache de dados para reduzir chamadas à API

4. **Deploy Produção:**
   - Cloud Run para executar pipeline
   - Cloud Scheduler para agendamento
   - Cloud Monitoring para observabilidade

---

## 📚 Documentação

- `README.md` - Visão geral do projeto
- `ARCHITECTURE.md` - Arquitetura detalhada
- `GUIA_EXECUCAO.md` - Instruções de execução
- `docs/GCP_SETUP.md` - Configuração GCP
- `CHANGELOG.md` - Histórico de mudanças

---

## 🎓 Aprendizados

1. **Orquestração:** Prefect oferece ótima visibilidade do pipeline
2. **DBT:** Excelente para transformações SQL versionadas
3. **GCP:** Integração nativa com BigQuery facilita muito
4. **Resiliência:** Retry automático é essencial para APIs instáveis
5. **Testes:** DBT tests garantem qualidade desde o início

---

## ✨ Conclusão

Pipeline completo implementado com sucesso, seguindo todas as especificações:
- ✅ Captura automatizada de dados
- ✅ Armazenamento em Cloud Storage
- ✅ Transformação em camadas (Medallion)
- ✅ Testes de qualidade
- ✅ Orquestração com Prefect
- ✅ Documentação completa

O pipeline está pronto para produção, aguardando apenas a estabilização da API BRT para captura de dados reais.

---

**Desenvolvido com ❤️ para o Desafio CIVITAS**
