#  Como Usar o Prefect Dashboard

##  Objetivo

Visualizar a execução do pipeline BRT no dashboard web do Prefect Server.

---

##  Problema Atual com Docker

O Prefect Server via Docker (`prefect server start`) **está com problemas** de inicialização devido a conflitos de banco de dados. Por isso, recomendamos usar o **modo local** sem dashboard.

---

##  Duas Opções Disponíveis

### **Opção 1: Modo Local (RECOMENDADO)**

 **Vantagens:**
- Não precisa de Docker
- Execução imediata
- Sem problemas de configuração
- Logs claros e detalhados

 **Desvantagens:**
- Sem dashboard visual
- Logs apenas no terminal

**Como executar:**
```powershell
cd desafio-civitas-brt
python scripts\run_pipeline.py
```

---

### **Opção 2: Prefect Server com Dashboard (EXPERIMENTAL)**

 **Vantagens:**
- Dashboard visual em http://localhost:8080
- Visualização de runs
- Logs centralizados
- Histórico de execuções

 **Desvantagens:**
- Requer Docker funcionando
- Problemas de inicialização conhecidos
- Configuração mais complexa

**Passo a passo:**

#### 1. Inicie o Prefect Server (Terminal 1)
```powershell
# Configura backend
prefect backend server

# Inicia servidor
prefect server start
```

**Aguarde até ver:**
```
Visit http://localhost:8080 to get started
```

#### 2. Registre o Flow (Terminal 2)
```powershell
cd desafio-civitas-brt
python scripts\register_flow.py
```

**Resultado esperado:**
```
 FLOW REGISTRADO COM SUCESSO!
Flow ID: abc123...
 Acesse: http://localhost:8080/default
```

#### 3. Acesse o Dashboard

1. Abra navegador: http://localhost:8080/default
2. Menu lateral: **Flows**
3. Encontre: **"BRT Data Pipeline - Medallion Architecture"**
4. Clique no flow
5. Botão **"Quick Run"** para executar manualmente

---

##  Troubleshooting

### Problema: Prefect Server não inicia (Docker)

**Sintomas:**
```
hasura-1 exited with code 1
graphql-1: duplicate key value violates unique constraint
```

**Solução temporária:**
```powershell
# Limpa volumes Docker
docker-compose down --volumes

# Tenta novamente
prefect server start
```

**Solução definitiva:**
Use **Opção 1** (modo local) que funciona perfeitamente.

---

### Problema: Flow não aparece no dashboard

**Causas possíveis:**
1. Backend não configurado para servidor
2. Flow não foi registrado
3. Servidor Prefect offline

**Verificação:**
```powershell
# Verifica backend
prefect backend server

# Verifica servidor
# Deve abrir http://localhost:8080
```

**Solução:**
```powershell
# Re-registra flow
python scripts\register_flow.py
```

---

##  Comparação de Modos

| Característica | Modo Local | Prefect Server |
|---|---|---|
| **Complexidade** | Baixa | Alta |
| **Dashboard** |  |  |
| **Docker** | Não precisa | Obrigatório |
| **Logs** | Terminal | Dashboard + Terminal |
| **Histórico** | Não | Sim |
| **Debugging** | Fácil | Médio |
| **Produção** | Não recomendado | Recomendado |
| **Status atual** |  Funcionando |  Problemas Docker |

---

##  Recomendação

Para **demonstração e testes**: Use **Opção 1** (modo local)

Para **produção real**: Migre para **Prefect Cloud** (SaaS, sem Docker)
- Gratis até 20.000 execuções/mês
- Dashboard profissional
- Sem problemas de infraestrutura
- Cadastro: https://cloud.prefect.io

---

##  Nota Final

O pipeline **funciona perfeitamente** em ambos os modos. A diferença é apenas na **visualização**:

- **Modo Local**: Logs no terminal
- **Prefect Server**: Logs no dashboard web

A **lógica do pipeline é idêntica** nos dois casos.
