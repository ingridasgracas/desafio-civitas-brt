#  Guia Completo: Prefect Server + Docker Agent

##  Requisito do Desafio

> "Instalar e configurar o Prefect Server localmente com um Docker Agent"

Este guia mostra como configurar **exatamente** conforme pedido no desafio CIVITAS.

---

##  Arquitetura

```

                  PREFECT SERVER                      
         (Docker containers via prefect CLI)          
                                                      
                  
   UI         API        Database            
   :8080      :4200      :5432               
                  

                     ↕

              PREFECT LOCAL AGENT                     
        (Executa flows no ambiente local)             
                                                      
  • Monitora servidor por novos runs                 
  • Executa tasks localmente                         
  • Reporta status ao servidor                       

                     ↕

                BRT PIPELINE FLOW                     
                                                      
  1. Captura API → 2. Buffer → 3. CSV                
  4. GCS → 5. BigQuery → 6. DBT                      

```

---

##  Pré-requisitos

- [x] Docker Desktop instalado e rodando
- [x] Python 3.12 com Prefect 1.4.1
- [x] Projeto GCP configurado
- [x] Credenciais JSON do GCP

---

##  Passo a Passo (3 Terminais)

### **TERMINAL 1: Prefect Server**

```powershell
# 1. Configura backend
prefect backend server

# 2. Inicia servidor (containers Docker)
prefect server start
```

**Aguarde até ver:**
```
WELCOME TO
   _____  _____  ______ ______ ______ _____ _______ 
  |  __ \|  __ \|  ____|  ____|  ____/ ____|__   __|
  ...
  
  Visit http://localhost:8080 to get started
```

 **Servidor rodando!** Deixe este terminal aberto.

---

### **TERMINAL 2: Registrar Flow**

```powershell
# Vai para diretório do projeto
cd desafio-civitas-brt

# Registra flow no servidor
python pipeline\brt_flow.py --register
```

**Resultado esperado:**
```
 Registrando flow no Prefect Server...
 Flow registrado com sucesso! ID: abc123...
 Acesse: http://localhost:8080/default
 Próximo passo: Inicie o Agent
```

 **Flow registrado!** Você pode fechar este terminal.

---

### **TERMINAL 3: Prefect Agent**

```powershell
# Inicia agent local
prefect agent local start
```

**Resultado esperado:**
```
[2025-10-25 00:00:00] INFO - Agent | Starting LocalAgent
[2025-10-25 00:00:01] INFO - Agent | Agent successfully started!
[2025-10-25 00:00:02] INFO - Agent | Agent ID: agent-xyz
```

 **Agent rodando!** Deixe este terminal aberto.

---

##  Acessar Dashboard

1. Abra navegador: **http://localhost:8080**

2. Menu lateral → **Flows**

3. Você verá: **"BRT Data Pipeline - Medallion Architecture"**

4. Clique no flow

5. Clique em **"Quick Run"** para executar

6. Veja execução em tempo real na aba **"Runs"**

---

##  Executar o Pipeline

### **Opção A: Via Dashboard (Manual)**

1. Acesse http://localhost:8080/default
2. Flows → "BRT Data Pipeline"
3. Botão **"Quick Run"**
4. Acompanhe execução na aba "Runs"

### **Opção B: Automático (Schedule)**

O flow tem schedule configurado para **1 minuto**.

- Executa automaticamente a cada 1 minuto
- Agent pega a execução e roda
- Logs aparecem no dashboard e no terminal do Agent

---

##  O Que Acontece

```

 1. SCHEDULE (1 min) → Cria run no servidor    
 2. AGENT detecta novo run                      
 3. AGENT executa flow localmente               
 4. FLOW captura dados BRT                      
 5. FLOW processa e envia para GCS              
 6. FLOW executa DBT transformações             
 7. AGENT reporta sucesso ao servidor           
 8. DASHBOARD atualiza status                   

```

---

##  Verificar Logs

### **No Dashboard:**
- Flow → Run → Clique no run ID
- Veja logs de cada task
- Timeline visual de execução

### **No Terminal (Agent):**
```
[INFO] - Agent | Submitting flow run...
[INFO] - Agent | Completed flow run
```

---

##  Parar Tudo

**TERMINAL 1 (Server):**
```
Ctrl + C
```

**TERMINAL 3 (Agent):**
```
Ctrl + C
```

---

##  Troubleshooting

###  Problema: Server não inicia (Docker)

**Erro:**
```
hasura-1 exited with code 1
duplicate key value violates unique constraint
```

**Solução:**
```powershell
# Limpa volumes Docker
docker-compose down --volumes

# Remove containers antigos
docker system prune -a

# Tenta novamente
prefect server start
```

---

###  Problema: Flow não aparece no dashboard

**Verificar:**

1. Servidor está rodando?
   - Abra http://localhost:8080
   - Deve mostrar interface Prefect

2. Backend está configurado?
   ```powershell
   prefect backend server
   ```

3. Re-registre o flow:
   ```powershell
   python pipeline\brt_flow.py --register
   ```

---

###  Problema: Agent não pega o run

**Verificar:**

1. Agent está rodando?
   - Terminal 3 deve estar aberto
   - Logs: "Agent successfully started"

2. Reinicie o agent:
   ```powershell
   Ctrl + C
   prefect agent local start
   ```

---

##  Confirmação de Sucesso

Você configurou corretamente quando:

-  Dashboard abre em http://localhost:8080
-  Flow "BRT Data Pipeline" aparece na lista
-  Agent está "Active" (indicador verde)
-  Consegue fazer "Quick Run" e vê execução
-  Logs aparecem em tempo real
-  Dados chegam no BigQuery

---

##  Screenshots Esperados

**Dashboard - Flows:**
```

 Flows                                     
                                           
  BRT Data Pipeline - Medallion...       
   Schedule: Every 1 minute                
   Last run: Success (2 minutes ago)       

```

**Dashboard - Flow Run:**
```

 Flow Run: bright-kangaroo               
 State: Success                           
                                           
 Tasks:                                    
  Capturar dados BRT API                 
  Adicionar ao buffer                    
 ⊝ Gerar CSV (Skipped)                    

```

---

##  Diferença: Local vs Server

| Aspecto | Execução Local | Prefect Server |
|---------|---------------|----------------|
| **Dashboard** |  Não |  Sim |
| **Docker** |  Não precisa |  Obrigatório |
| **Agent** |  Não |  Obrigatório |
| **Logs** | Terminal | Dashboard + Terminal |
| **Schedule** | Manual | Automático |
| **Histórico** | Não | Sim |
| **Requisito Desafio** |  Não atende |  Atende |

---

##  Resumo para Apresentação

**Para demonstrar que atende o requisito do desafio:**

1. Mostre Terminal 1: Prefect Server rodando
2. Mostre Terminal 3: Agent ativo
3. Abra Dashboard: http://localhost:8080
4. Mostre Flow registrado
5. Execute "Quick Run"
6. Mostre logs em tempo real
7. Mostre dados no BigQuery

 **Requisito atendido:** "Prefect Server localmente com Docker Agent"

---

##  Referências

- [Prefect Server Docs](https://docs.prefect.io/core/concepts/server.html)
- [Local Agent Guide](https://docs.prefect.io/orchestration/agents/local.html)
- [Registering Flows](https://docs.prefect.io/core/concepts/flows.html#registration)
