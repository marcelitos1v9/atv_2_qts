# Biblioteca API

> Tarefa 2.1 — Qualidade e Testes de Software | DSM6 2026-01

API REST para gerenciamento de livros desenvolvida com **Flask**. O projeto cobre todo o ciclo de qualidade de software: testes unitários, de integração, funcionais e E2E com Selenium, pipeline CI/CD via GitHub Actions, e uma funcionalidade implementada com **TDD**.

---

## Sumário

- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Executar a aplicação](#executar-a-aplicação)
- [Qualidade de código](#qualidade-de-código)
- [Testes](#testes)
- [Endpoints da API](#endpoints-da-api)
- [Exemplos de uso](#exemplos-de-uso)
- [TDD — Test Driven Development](#tdd--test-driven-development)
- [CI/CD — GitHub Actions](#cicd--github-actions)
- [Estrutura do projeto](#estrutura-do-projeto)

---

## Tecnologias

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.11+ | Linguagem principal |
| Flask | 3.0+ | Framework web / API REST |
| pytest | 7.4+ | Executor de testes |
| black | 24.0+ | Formatação de código |
| flake8 | 7.0+ | Análise estática (linting) |
| Selenium | 4.20+ | Testes E2E via navegador |
| GitHub Actions | — | Pipeline CI/CD |

---

## Pré-requisitos

- **Python 3.11+** instalado
- **Google Chrome** instalado (apenas para testes E2E)
- Git

---

## Instalação

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd atv_2_qts

# 2. Crie e ative o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## Executar a aplicação

```bash
python run.py
```

Acesse a interface web em: **http://127.0.0.1:5000**

A interface permite listar, adicionar, pesquisar, emprestar e devolver livros diretamente pelo navegador.

---

## Qualidade de código

O projeto deve passar sem erros nos três comandos abaixo:

```bash
# Formatar o código automaticamente
black .

# Verificar se o código está formatado corretamente
black --check .

# Verificar estilo e boas práticas
flake8 .
```

Configurações:
- `black` e `flake8` usam limite de **88 caracteres** por linha (definido em `pyproject.toml` e `.flake8`)
- `flake8` ignora `E203` e `W503` para compatibilidade com `black`

---

## Testes

### Executar todos os testes

```bash
pytest
```

### Executar por tipo

```bash
# Testes unitários
pytest tests/test_unit.py -v

# Testes de integração
pytest tests/test_integration.py -v

# Testes funcionais
pytest tests/test_functional.py -v

# Testes E2E — requer Google Chrome instalado
pytest tests/test_e2e.py -v
```

### Executar sem os testes E2E

```bash
pytest tests/test_unit.py tests/test_integration.py tests/test_functional.py -v
```

### Resumo dos testes

| Arquivo | Tipo | Quantidade | O que testa |
|---|---|---|---|
| `test_unit.py` | Unitário | 40 testes | Modelo `Book` e funções de `services.py` em isolamento |
| `test_integration.py` | Integração | 28 testes | Endpoints HTTP da API (request → response) |
| `test_functional.py` | Funcional | 6 testes | Fluxos completos de negócio (CRUD, empréstimo, estatísticas) |
| `test_e2e.py` | E2E | 3 testes | Interação real via navegador com Selenium |
| **Total** | | **77 testes** | |

> Os testes E2E iniciam um servidor Flask real em background na porta 5099 e usam o Chrome em modo headless (sem abrir janela).

---

## Endpoints da API

### Livros

| Método | Rota | Descrição | Status de sucesso |
|---|---|---|---|
| `GET` | `/` | Interface web | 200 |
| `GET` | `/books` | Listar todos os livros | 200 |
| `GET` | `/books?q=termo` | Pesquisar por título ou autor | 200 |
| `GET` | `/books/<id>` | Obter livro pelo ID | 200 |
| `POST` | `/books` | Criar novo livro | 201 |
| `PUT` | `/books/<id>` | Atualizar livro (parcial) | 200 |
| `DELETE` | `/books/<id>` | Excluir livro | 200 |
| `GET` | `/books/stats` | Estatísticas da biblioteca | 200 |

### Empréstimo (funcionalidade TDD)

| Método | Rota | Descrição | Status de sucesso |
|---|---|---|---|
| `POST` | `/books/<id>/borrow` | Emprestar livro | 200 |
| `POST` | `/books/<id>/return` | Devolver livro | 200 |

### Códigos de erro

| Código | Significado |
|---|---|
| `400` | Dados inválidos ou ausentes |
| `404` | Livro não encontrado |
| `409` | Conflito (ex: livro já emprestado) |
| `415` | Content-Type incorreto |

---

## Exemplos de uso

### Criar um livro

```bash
curl -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code", "author": "Robert Martin", "year": 2008, "genre": "Tecnologia"}'
```

Resposta:
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert Martin",
  "year": 2008,
  "genre": "Tecnologia",
  "available": true
}
```

### Listar todos os livros

```bash
curl http://127.0.0.1:5000/books
```

### Pesquisar livros

```bash
curl "http://127.0.0.1:5000/books?q=clean"
```

### Emprestar um livro

```bash
curl -X POST http://127.0.0.1:5000/books/1/borrow
```

### Devolver um livro

```bash
curl -X POST http://127.0.0.1:5000/books/1/return
```

### Ver estatísticas

```bash
curl http://127.0.0.1:5000/books/stats
```

Resposta:
```json
{
  "total": 5,
  "available": 3,
  "unavailable": 2,
  "average_year": 2010.4
}
```

---

## TDD — Test Driven Development

A funcionalidade de **Empréstimo e Devolução de Livros** foi desenvolvida seguindo rigorosamente o ciclo **RED → GREEN → REFACTOR**.

---

### Fase RED — Testes escritos antes da implementação

Os testes foram criados antes de qualquer linha de código funcional existir. Ao rodar o pytest neste momento, todos falhavam com `404 Not Found` pois os endpoints e funções não existiam.

```python
# tests/test_integration.py

def test_borrow_book(client, sample_book):
    response = client.post(f"/books/{sample_book['id']}/borrow")
    assert response.status_code == 200          # FALHOU: 404
    assert response.get_json()["available"] is False

def test_return_book(client, sample_book):
    client.post(f"/books/{sample_book['id']}/borrow")
    response = client.post(f"/books/{sample_book['id']}/return")
    assert response.status_code == 200          # FALHOU: 404
    assert response.get_json()["available"] is True

def test_borrow_unavailable_book_returns_409(client, sample_book):
    book_id = sample_book["id"]
    client.post(f"/books/{book_id}/borrow")
    response = client.post(f"/books/{book_id}/borrow")
    assert response.status_code == 409          # FALHOU: 404
```

**Resultado:** `FAILED` — commit `test(RED)`

---

### Fase GREEN — Implementação mínima para passar nos testes

Foram adicionadas as funções em `services.py`:

```python
def borrow_book(book_id):
    book = _books.get(book_id)
    if not book:
        return None, "Book not found"
    if not book.available:
        return None, "Book is not available for borrowing"
    book.available = False
    return book, None

def return_book(book_id):
    book = _books.get(book_id)
    if not book:
        return None, "Book not found"
    if book.available:
        return None, "Book was not borrowed"
    book.available = True
    return book, None
```

E as rotas em `routes.py`:

```python
@books_bp.route("/books/<int:book_id>/borrow", methods=["POST"])
def borrow_book(book_id):
    book, error = services.borrow_book(book_id)
    if error:
        status = 404 if "not found" in error else 409
        return jsonify({"error": error}), status
    return jsonify(book.to_dict())
```

**Resultado:** `PASSED` — commit `feat(GREEN)`

---

### Fase REFACTOR — Melhoria do código sem quebrar os testes

Com os testes passando, o código foi melhorado:

- Tratamento de HTTP **409 Conflict** para livro já emprestado
- Tratamento de HTTP **409 Conflict** para devolução de livro não emprestado
- Tratamento de HTTP **404 Not Found** para livro inexistente
- Toda a lógica de negócio centralizada na camada `services.py`, mantendo as rotas limpas

**Resultado:** `PASSED` (todos os testes continuaram passando) — commit `refactor(REFACTOR)`

---

### Evidência no histórico de commits

```
d7b5c6d refactor(REFACTOR): melhora tratamento de erros no emprestimo/devolucao
6155858 feat(GREEN): implementa borrow_book e return_book - testes passam
2fd5fd2 test(RED): testes de emprestimo/devolucao falham - endpoints nao existem ainda
```

---

## CI/CD — GitHub Actions

O pipeline está em `.github/workflows/ci.yml` e executa automaticamente a cada `push` ou `pull request`.

### Etapas do pipeline

```
1. Checkout do código
2. Configurar Python 3.11
3. Instalar dependências (pip install -r requirements.txt)
4. black --check .          → verifica formatação
5. flake8 .                 → verifica estilo
6. pytest (unit + integração + funcional)
7. pytest tests/test_e2e.py (Chrome headless)
```

### Como verificar

Após subir o repositório para o GitHub, acesse a aba **Actions** para ver o histórico de execuções do pipeline.

---

## Estrutura do projeto

```
atv_2_qts/
│
├── app/                        # Pacote principal da aplicação
│   ├── __init__.py             # Factory create_app()
│   ├── models.py               # Classe Book (modelo + validação)
│   ├── routes.py               # Endpoints da API REST
│   ├── services.py             # Lógica de negócio (CRUD, busca, stats, empréstimo)
│   └── templates/
│       └── index.html          # Interface web
│
├── tests/                      # Suite de testes
│   ├── conftest.py             # Fixtures compartilhadas (app, client, sample_book)
│   ├── test_unit.py            # 40 testes unitários
│   ├── test_integration.py     # 28 testes de integração
│   ├── test_functional.py      # 6 testes funcionais
│   └── test_e2e.py             # 3 testes E2E com Selenium
│
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline GitHub Actions
│
├── .flake8                     # Configuração do flake8
├── .gitignore                  # Arquivos ignorados pelo git
├── pyproject.toml              # Configuração do black
├── pytest.ini                  # Configuração do pytest
├── requirements.txt            # Dependências do projeto
├── run.py                      # Entry point da aplicação
└── README.md                   # Este arquivo
```

---

## Autor

Desenvolvido como parte da disciplina **Qualidade e Testes de Software** — DSM6, Fatec Registro, 2026-01.
