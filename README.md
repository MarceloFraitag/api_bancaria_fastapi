# 🚀 API Bancária Assíncrona com FastAPI & PostgreSQL

Fala aí! Beleza? Esse é o repositório de uma API Bancária assíncrona robusta que desenvolvi utilizando **FastAPI** e **PostgreSQL**. O objetivo principal deste projeto foi aplicar conceitos avançados de desenvolvimento back-end, focando em alta performance, segurança de dados e auditoria de requisições.

A API simula operações financeiras essenciais (como criação de contas, autenticação segura e gerenciamento de transações), tudo rodando em cima de queries assíncronas com o SQLAlchemy.

---

## 🛠️ Tecnologias Utilizadas

* **FastAPI:** Framework moderno, rápido (alta performance) e pronto para código assíncrono (`async/await`).
* **PostgreSQL:** Banco de dados relacional para persistência segura dos dados das contas e movimentações.
* **SQLAlchemy (Async):** ORM utilizado para mapear as tabelas e rodar queries de forma não-bloqueante.
* **Pydantic:** Validação de dados rigorosa no corpo das requisições (garantindo que depósitos negativos sejam barrados, por exemplo).
* **Passlib & Bcrypt:** Ferramentas para hashing e criptografia segura de senhas antes de salvar no banco de dados.
* **Uvicorn:** Servidor ASGI para rodar a aplicação localmente.

---

## 🔥 Principais Funcionalidades

### 🔐 Autenticação & Segurança (OAuth2 + JWT)
* **Cadastro Seguro:** Rota para criação de novas contas (`POST /cadastro`) salvando apenas a `senha_hash`.
* **Login Integrado:** Geração de tokens de acesso baseados no padrão OAuth2 (`POST /login`) para proteger os endpoints sensíveis.
* **Rotas Trancadas:** Endpoints de transações e extratos exigem que o cabeçalho de autenticação (`Bearer Token`) seja enviado e validado.

### 💰 Operações Financeiras Avançadas
* **Transações Inteligentes:** Suporte a depósitos, saques e transferências com validações do Pydantic para evitar fraudes ou valores inconsistentes.
* **Paginação e Filtros:** Rota de extrato otimizada contendo paginação (`limite` e `offset`) para não sobrecarregar o banco de dados.

### 📊 Middleware de Auditoria (Logs em Tempo Real)
* Criado um middleware personalizado que intercepta cada requisição feita à API. Ele calcula o tempo exato de execução e printa um log de auditoria limpo e padronizado no terminal:
  `LOG BANCÁRIO | GET /extrato | Status: 200 | Tempo: 1.96ms`

---

## 🛠️ Desafio Técnico Superado: O Bug do Bcrypt 🐛

Durante os testes de integração das rotas de autenticação, enfrentei um clássico `500 Internal Server Error` gerado por uma falha silenciosa de compatibilidade entre as versões mais recentes do pacote `bcrypt` e a biblioteca `passlib` (que parou de reconhecer a propriedade interna `__about__`). Isso gerava um comportamento inesperado disparando a exceção:
> `ValueError: password cannot be longer than 72 bytes, truncate manually if necessary`

**Como resolvi:** 
Identifiquei a raiz do problema analisando o Traceback do terminal e apliquei um downgrade estratégico do pacote no ambiente virtual para o `bcrypt==4.0.1`, restaurando perfeitamente a comunicação nativa da biblioteca de criptografia sem precisar comprometer as regras de negócio da API.

---

## 🚀 Como Rodar o Projeto Localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/MarceloFraitag/api_bancaria_fastapi.git](https://github.com/MarceloFraitag/api_bancaria_fastapi.git)
   cd api_bancaria_fastapi