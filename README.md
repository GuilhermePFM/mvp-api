# Controle Financeiro API
Este é o repositório do back-end do projeto **Controle Financeiro**, desenvolvido como parte do MVP (Minimum Viable Product) para a Pós-Graduação em Engenharia de Software da PUC Rio. O objetivo do projeto é fornecer uma interface intuitiva e funcional para gerenciar finanças pessoais e familiares, permitindo o controle de transações, categorias, e usuários de forma eficiente.

O repositório do Front-end deste projeto é [https://github.com/GuilhermePFM/mvp-front-end](https://github.com/GuilhermePFM/mvp-front-end).

---
## Índice
- [Controle Financeiro API](#controle-financeiro-api)
  - [Índice](#índice)
  - [Descrição](#descrição)
  - [Estrutura de Arquivos do Projeto](#estrutura-de-arquivos-do-projeto)
    - [**Descrição dos Arquivos**](#descrição-dos-arquivos)
      - [**`apis/`**](#apis)
      - [**`model/`**](#model)
      - [**`schemas/`**](#schemas)
      - [**`app.py`**](#apppy)
      - [**`logger.py`**](#loggerpy)
      - [**`requirements.txt`**](#requirementstxt)
      - [**`config.py`**](#configpy)
      - [**`README.md`**](#readmemd)
  - [Como Instalar as Dependências](#como-instalar-as-dependências)
  - [Como Executar o Código](#como-executar-o-código)

---

## Descrição

A **API ControleFinanceiro** é um sistema de gerenciamento financeiro desenvolvido para ajudar os usuários a rastrear suas transações, gerenciar categorias e organizar suas finanças. Construída com Python e Flask, a API utiliza SQLAlchemy para gerenciamento de banco de dados e Pydantic para validação de esquemas. Ela oferece endpoints para gerenciar usuários, transações e categorias de transações, garantindo uma solução robusta e escalável para o controle financeiro.

---

## Estrutura de Arquivos do Projeto

Abaixo está a estrutura de arquivos do projeto, com uma breve descrição de cada arquivo:

```
ControleFinanceiro/
├── apis/
│   ├── transactions_category.py
│   ├── transactions_type.py
│   ├── transactions.py
│   ├── users.py
├── model/
│   ├── base.py
│   ├── transaction_category.py
│   ├── transaction_type.py
│   ├── transaction.py
│   ├── user.py
├── schemas/
│   ├── error.py
│   ├── transaction_category.py
│   ├── transaction_type.py
│   ├── transaction.py
│   ├── user.py
├── app.py
├── config.py
├── logger.py
├── requirements.txt
└── README.md
```

### **Descrição dos Arquivos**

#### **`apis/`**
- **`transactions.py`**: Contém os endpoints para gerenciar transações, incluindo adicionar, listar e excluir transações.
- **`transactions_category.py`**: Fornece endpoints para gerenciar categorias de transações, como criar, listar e excluir categorias.
- **`transactions_type.py`**: Fornece endpoints para gerenciar tipos de transações, como criar, listar e excluir tipos.
- **`users.py`**: Gerencia operações relacionadas a usuários, incluindo adicionar, recuperar, listar e excluir usuários.

#### **`model/`**
- **`base.py`**: Define a classe base para os modelos do SQLAlchemy.
- **`transaction.py`**: Define o modelo `Transaction`, que representa transações financeiras.
- **`transaction_category.py`**: Define o modelo `TransactionCategory`, que representa categorias de transações.
- **`transaction_type.py`**: Define o modelo `TransactionType`, que representa tipos de transações (ex.: receita, despesa).
- **`user.py`**: Define o modelo `User`, que representa os usuários do sistema.

#### **`schemas/`**
- **`error.py`**: Define os esquemas Pydantic para retorno de erros.
- **`transaction_category.py`**: Define os esquemas Pydantic para validação de dados relacionados a categorias de transações.
- **`transaction_type.py`**: Define os esquemas Pydantic para validação de dados relacionados a tipos de transações.
- **`transaction.py`**: Define os esquemas Pydantic para validação de dados relacionados a transações.
- **`user.py`**: Define os esquemas Pydantic para validação de dados relacionados a usuários.

#### **`app.py`**
- Configura o aplicativo Flask e registra as rotas da API.

#### **`logger.py`**
- Configura o sistema de logs para a aplicação.

#### **`requirements.txt`**
- Lista todas as dependências Python necessárias para o projeto.

#### **`config.py`**
- Configura o SWAGGER.

#### **`README.md`**
- Fornece uma visão geral do projeto, incluindo instruções de instalação e uso.

---

## Como Instalar as Dependências

Siga os passos abaixo para instalar as dependências do projeto:

1. **Clone o Repositório**:
   ```bash
   git clone https://github.com/GuilhermePFM/mvp-api
   cd mvp-api
   ```

2. **Crie um Ambiente Virtual**:
   ```bash
   python -m venv venv
   ```

3. **Ative o Ambiente Virtual**:
   - No Windows:
     ```bash
     venv\Scripts\activate
     ```
   - No macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Instale as Dependências**:
   ```bash
   pip install -r requirements.txt
   ```
   Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

---

## Como Executar o Código

1. **Execute a Aplicação**:
   ```bash
   python -m flask run --no-debugger --no-reload
   ```

2. **Acesse a API**:
   - A API estará disponível em: [http://127.0.0.1:5000](http://127.0.0.1:5000).

3. **Teste os Endpoints**:
   - Use ferramentas como Postman ou o SWAGGER [http://127.0.0.1:5000/openapi/swagger](http://127.0.0.1:5000/openapi/swagger) disponibilizado para testar os endpoints da API.

