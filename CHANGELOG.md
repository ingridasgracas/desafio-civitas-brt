# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-10-24

### 🎉 Lançamento Inicial

Primeira versão completa do Pipeline BRT CIVITAS seguindo arquitetura Medallion.

### ✨ Features

#### Pipeline & Orquestração
- **feat**: implementa pipeline Prefect v1.4.1 completo
- **feat**: adiciona captura de dados da API BRT minuto a minuto
- **feat**: implementa agregação de 10 minutos de dados em CSV
- **feat**: adiciona upload automático para Google Cloud Storage
- **feat**: integra execução de modelos DBT no pipeline

#### Arquitetura Medallion
- **feat**: implementa camada Bronze com tabelas externas GCS
- **feat**: implementa camada Silver com validações e limpeza
- **feat**: implementa camada Gold com métricas agregadas
- **feat**: adiciona particionamento por data na camada Gold
- **feat**: adiciona clustering por linha e período

#### Qualidade de Dados
- **feat**: implementa testes de schema DBT
- **feat**: adiciona validação de coordenadas GPS
- **feat**: implementa deduplicação de registros
- **feat**: adiciona testes de relacionamento entre tabelas
- **feat**: implementa testes de valores esperados

#### Documentação
- **feat**: adiciona documentação automática com DBT docs
- **feat**: implementa persist_docs para BigQuery
- **feat**: adiciona descrições detalhadas de tabelas e colunas
- **feat**: cria lineage de dados automático

#### DevOps & Infraestrutura
- **feat**: adiciona Docker Compose para Prefect Server
- **feat**: implementa Docker Agent para execução de flows
- **feat**: adiciona variáveis de ambiente configuráveis
- **feat**: implementa logging estruturado com Loguru

### 📚 Documentação

- **docs**: adiciona README completo com instruções
- **docs**: cria guia de início rápido (QUICKSTART.md)
- **docs**: adiciona documentação de arquitetura detalhada
- **docs**: cria guia de configuração GCP
- **docs**: adiciona exemplos de CSV de dados
- **docs**: documenta todos os modelos DBT
- **docs**: adiciona troubleshooting guide

### 🏗️ Estrutura

- **build**: configura estrutura de diretórios do projeto
- **build**: adiciona .gitignore para Python, DBT e GCP
- **build**: cria requirements.txt com dependências
- **build**: adiciona .env.example para configuração

### 🧪 Testes

- **test**: adiciona testes de qualidade DBT
- **test**: implementa validação de coordenadas GPS
- **test**: adiciona testes de unicidade e not_null
- **test**: implementa testes de valores aceitos
- **test**: adiciona testes de relacionamento

### 🔧 Scripts

- **feat**: adiciona script de captura da API (brt_api_capture.py)
- **feat**: implementa agregador de dados (brt_data_aggregator.py)
- **feat**: adiciona gerenciador GCS (gcs_manager.py)
- **feat**: cria script de setup automatizado (setup.py)
- **feat**: adiciona script PowerShell de inicialização rápida

### 📊 Modelos DBT

#### Bronze
- **feat**: adiciona source para tabela externa GCS
- **feat**: implementa schema de 8 colunas
- **feat**: adiciona configuração de external_location

#### Silver
- **feat**: cria modelo stg_brt_gps_cleaned
- **feat**: implementa validação de coordenadas do Rio de Janeiro
- **feat**: adiciona campos derivados (data, hora, dia da semana)
- **feat**: implementa categorização de velocidade
- **feat**: adiciona identificação de período do dia
- **feat**: implementa hash MD5 para deduplicação

#### Gold
- **feat**: cria modelo fct_brt_line_metrics
- **feat**: implementa agregações por linha e período
- **feat**: adiciona métricas de velocidade (média, min, max, stddev)
- **feat**: implementa distribuição de velocidades
- **feat**: adiciona KPIs percentuais
- **feat**: implementa coordenadas médias (centro de operação)

### 🔐 Segurança

- **security**: adiciona .gitignore para credenciais GCP
- **security**: implementa uso de variáveis de ambiente
- **security**: documenta princípio do menor privilégio
- **security**: adiciona guia de boas práticas de segurança

### ⚡ Performance

- **perf**: implementa particionamento de tabelas por data
- **perf**: adiciona clustering por linha e período
- **perf**: utiliza tabelas externas para reduzir custos
- **perf**: implementa views para camada Silver

### 🎨 Melhorias

- **style**: adiciona logging colorido com Loguru
- **style**: implementa mensagens de progresso no pipeline
- **style**: adiciona emojis para melhor visualização de logs
- **style**: formata código seguindo PEP 8

### 📦 Dependências

```
prefect==1.4.1
google-cloud-storage==2.10.0
google-cloud-bigquery==3.11.4
dbt-core==1.5.0
dbt-bigquery==1.5.0
dbt-external-tables==0.8.0
requests==2.31.0
pandas==2.0.3
pyarrow==12.0.1
python-dotenv==1.0.0
schedule==1.2.0
loguru==0.7.0
```

### 🐛 Correções

Nenhuma (primeira versão)

### 🗑️ Removido

Nenhum (primeira versão)

### ⚠️ Deprecado

Nenhum (primeira versão)

### 🔒 Segurança

Nenhum vulnerabilidade conhecida

---

## Tipos de Commits Utilizados

Este projeto segue [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, ponto e vírgula faltando, etc
- `refactor`: Refatoração de código
- `perf`: Melhoria de performance
- `test`: Adição ou correção de testes
- `build`: Mudanças no sistema de build ou dependências
- `ci`: Mudanças em arquivos de CI/CD
- `chore`: Outras mudanças que não modificam src ou test
- `revert`: Reverte um commit anterior
- `security`: Correção de vulnerabilidade de segurança

---

**Desenvolvido para CIVITAS - Desafio Técnico Engenheiro de Dados**
