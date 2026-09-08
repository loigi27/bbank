# 🏦 BBank 2026

<p align="center">
  <strong>Sistema de consulta de saldo, notas e aquisições para alunos.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Google%20Sheets-GViz-34A853?style=for-the-badge&logo=google-sheets&logoColor=white" alt="Google Sheets">
  <img src="https://img.shields.io/badge/Status-Ativo-22c55e?style=for-the-badge" alt="Status">
</p>

<p align="center">
  <img src="https://dummyimage.com/1000x400/19182d/ffffff&text=BBank+2026" alt="BBank 2026" width="90%">
</p>

---

## 📖 Sobre o projeto

O **BBank 2026** é uma aplicação web desenvolvida em Python para consultar informações dos alunos diretamente de uma planilha do Google Sheets.

O sistema permite consultar:

* 💰 **Saldo**
* 📊 Informações semanais do saldo
* 🎓 **Notas**
* 📈 Dashboard de desempenho
* 🛍️ **Aquisições**
* 🔐 Privilégios de alunos Blindados
* 📧 Solicitações de aquisição enviadas por e-mail

A aplicação foi desenvolvida para funcionar de forma simples, sem necessidade de Google Cloud ou de uma API autenticada do Google.

---

## ✨ Principais recursos

### 💰 Consulta de saldo

Digite a matrícula do aluno e o BBank consulta automaticamente os dados disponíveis na planilha.

São exibidos:

* Nome
* Ano
* Turma
* Matrícula
* Saldo atual
* Saldo do 1º semestre
* Valores semanais
* MC$
* Status

---

### 🎓 Sistema de notas

O BBank possui uma área específica para consulta das notas.

Atualmente são suportadas:

* P1
* P2
* P3
* P4

Além das notas, o sistema apresenta um pequeno dashboard com:

* 📊 Média
* 📝 Quantidade de avaliações cadastradas
* 🏆 Maior nota
* 📉 Menor nota
* 📈 Percentual de avaliações lançadas

---

### 🛍️ Aquisições

Alunos elegíveis podem solicitar benefícios diretamente pelo site.

Exemplos:

| Aquisição                      | Descrição                        |  Custo |
| ------------------------------ | -------------------------------- | -----: |
| 🪑 Lugar alternativo           | Mudar de lugar por uma aula      |  B$ 50 |
| 👥 Cadeira ao lado de um amigo | Sentar ao lado de um amigo       | B$ 100 |
| 🪙 Maker Coin                  | Comprar MC$ conforme a TC do mês |    TC* |

Quando uma aquisição é solicitada, o sistema envia um e-mail para o administrador contendo:

* Nome do aluno
* Matrícula
* Ano e turma
* Benefício escolhido
* Descrição
* Custo
* Saldo
* Status

> ℹ️ A compra não altera automaticamente a planilha nesta versão. O administrador recebe a solicitação e realiza a confirmação.

---

# 🔐 Regras de acesso às aquisições

Existem duas versões do sistema.

### 🟢 `bbank.py` — versão oficial

Somente alunos com status **Blindado** podem realizar aquisições.

```text
Blindado      → ✅ Pode comprar
Estressado    → ❌ Não pode comprar
Outros        → ❌ Não pode comprar
```

A verificação é feita no servidor, e não apenas escondendo o botão na interface.

---

### 🧪 `bbank_teste.py` — versão de testes

Na versão de testes, tanto **Blindados** quanto **Estressados** podem realizar aquisições.

```text
Blindado      → ✅ Pode comprar
Estressado    → ✅ Pode comprar
Outros        → ❌ Não pode comprar
```

Isso permite testar o sistema de aquisições sem precisar alterar o status de um aluno para Blindado.

---

# 🗂️ Estrutura do projeto

```text
BBank-2026/
│
├── bbank.py
├── bbank_teste.py
├── requirements.txt
├── .env.example
└── README.md
```

### `bbank.py`

Versão oficial do BBank.

Utilizada para o sistema real, com aquisições restritas aos alunos Blindados.

### `bbank_teste.py`

Versão de testes.

Permite que usuários Blindados e Estressados testem as aquisições.

### `requirements.txt`

Lista de dependências necessárias para o projeto.

### `.env.example`

Modelo das variáveis de ambiente utilizadas pelo sistema.

### `README.md`

Documentação do projeto.

---

# ⚡ Quickstart

## 1. Instalar o Python

O BBank foi desenvolvido para Python 3.

Verifique se o Python está instalado:

```powershell
python --version
```

Recomenda-se utilizar uma versão moderna do Python.

---

## 2. Criar o ambiente virtual

No Windows:

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Depois de ativado, o terminal deverá mostrar algo semelhante a:

```text
(.venv) PS C:\...\BBank-2026>
```

---

## 3. Instalar as dependências

Com o ambiente virtual ativado:

```powershell
python -m pip install -r requirements.txt
```

---

# 🔑 Configuração da senha do e-mail

O BBank **não salva a senha do e-mail dentro do código Python**.

A senha é lida através da variável de ambiente:

```text
SMTP_PASSWORD
```

Isso permite utilizar uma **App Password** sem colocar a senha diretamente no `bbank.py` ou `bbank_teste.py`.

## Windows PowerShell

Antes de executar o BBank:

```powershell
$env:SMTP_PASSWORD="SUA_APP_PASSWORD"
```

Depois:

```powershell
python bbank.py
```

Ou, para a versão de testes:

```powershell
python bbank_teste.py
```

### ⚠️ Importante

Não coloque a App Password diretamente no código:

```python
SMTP_PASSWORD = "senha-aqui"
```

O correto é:

```python
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
```

Assim, a senha fica fora do código-fonte.

---

# 📧 Configuração SMTP

O sistema utiliza variáveis de ambiente para configurar o servidor de e-mail.

Variáveis disponíveis:

```text
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SMTP_FROM
```

Exemplo no PowerShell:

```powershell
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="465"
$env:SMTP_USER="seu-email@example.com"
$env:SMTP_PASSWORD="SUA_APP_PASSWORD"
$env:SMTP_FROM="seu-email@example.com"
```

Depois execute:

```powershell
python bbank.py
```

> 🔒 Nunca publique sua App Password no GitHub, README, screenshots ou código-fonte.

---

# 📊 Google Sheets

O BBank busca os dados diretamente do Google Sheets utilizando o endpoint **GViz CSV**.

A planilha precisa estar disponível para visualização de acordo com a configuração utilizada pelo projeto.

A aplicação utiliza duas abas:

```text
B$
notas
```

### Aba `B$`

Contém informações como:

```text
Matrícula
Nome
Ano
Turma
Saldo 1°S
04/08
11/08
18/08
25/08
MC$
Saldo
status
```

### Aba `notas`

Contém:

```text
Matrícula
Nome
Ano
Turma
P1
P2
P3
P4
```

---

# 🔄 Atualização dos dados

Para evitar fazer várias requisições seguidas ao Google Sheets, o BBank possui um pequeno sistema de cache.

Por padrão:

```text
Cache: 3 segundos
```

O valor pode ser alterado através da variável:

```powershell
$env:CACHE_SEGUNDOS="5"
```

---

# 🌐 Executando o BBank

## Versão oficial

```powershell
python bbank.py
```

O servidor será iniciado normalmente em:

```text
http://localhost:8000
```

O navegador é aberto automaticamente.

---

## Versão de testes

```powershell
python bbank_teste.py
```

A versão de testes possui a mesma interface, mas permite aquisições para:

```text
Blindados + Estressados
```

---

# ⚙️ Alterando a porta

A porta padrão é:

```text
8000
```

Para utilizar outra porta:

```powershell
$env:PORTA="8080"
python bbank.py
```

O sistema ficará disponível em:

```text
http://localhost:8080
```

---

# 🧪 Ambiente de testes

Use `bbank_teste.py` quando precisar testar:

* Botões de aquisição
* Envio de e-mail
* Mensagens de sucesso
* Mensagens de erro
* Permissões de compra
* Integração SMTP

Depois que os testes forem concluídos, utilize:

```text
bbank.py
```

para a versão oficial.

---

# 🛡️ Segurança

O BBank foi desenvolvido para evitar colocar credenciais diretamente no código.

### Nunca faça:

```python
SMTP_PASSWORD = "minha-senha"
```

### Faça:

```python
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
```

Também não publique arquivos que contenham:

```text
SMTP_PASSWORD
App Password
senha
tokens
credenciais
```

O arquivo `.env.example` deve conter apenas exemplos, nunca credenciais reais.

---

# 🧹 Arquivos desnecessários

O projeto deve manter somente os arquivos necessários para executar e documentar o sistema.

Estrutura recomendada:

```text
📁 BBank-2026
│
├── 🐍 bbank.py
├── 🧪 bbank_teste.py
├── 📦 requirements.txt
├── 🔑 .env.example
└── 📖 README.md
```

Arquivos temporários, correções antigas, cópias duplicadas e arquivos de teste que não fazem parte do funcionamento atual devem ser removidos.

---

# 🛠️ Tecnologias

O projeto utiliza principalmente:

* 🐍 Python
* 🌐 HTML
* 🎨 CSS
* ⚡ JavaScript
* 📊 Google Sheets / GViz
* 📧 SMTP
* 🔒 Variáveis de ambiente

A aplicação utiliza principalmente a biblioteca padrão do Python.

---

# 🧭 Fluxo do sistema

```text
             ┌─────────────────┐
             │     Usuário     │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Digita matrícula│
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │    BBank        │
             │    Python       │
             └────────┬────────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
      ┌──────────────┐  ┌──────────────┐
      │ Google Sheets│  │ SMTP / E-mail│
      └──────────────┘  └──────────────┘
             │                 ▲
             ▼                 │
      ┌──────────────┐         │
      │ Saldo / Notas│         │
      │ / Status     │─────────┘
      └──────────────┘
```

---

# 📌 Status do projeto

**BBank 2026 — em desenvolvimento**

O projeto continua sendo evoluído com melhorias de:

* 🎨 Interface
* ⚡ Desempenho
* 🔐 Segurança
* 🛍️ Aquisições
* 📊 Dashboard
* 📧 Sistema de notificações
* 📱 Responsividade

---

# 👨‍💻 Desenvolvimento

O BBank 2026 foi desenvolvido como um projeto web em Python, com foco em uma interface simples, rápida e fácil de utilizar.

A versão oficial é:

```text
bbank.py
```

A versão destinada a testes é:

```text
bbank_teste.py
```

---

<p align="center">
  <strong>🏦 BBank 2026</strong>
  <br>
  Sistema de saldo, notas e aquisições
</p>
