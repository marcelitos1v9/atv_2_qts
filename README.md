# Biblioteca API — Tarefa 2.1 (Qualidade e Testes de Software)

API REST para gerenciamento de livros, desenvolvida com Flask. Inclui testes unitários, de integração, funcionais e E2E (Selenium), além de pipeline CI/CD via GitHub Actions.

---

## Pré-requisitos

- Python 3.11+
- Google Chrome (para testes E2E)

---

## Instalação

```bash
# Crie e ative um ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS

# Instale as dependências
pip install -r requirements.txt
```

---

## Executar a aplicação

```bash
python run.py
```

Acesse em: http://127.0.0.1:5000

---

## Qualidade de código

```bash
# Formatar com black
black .

# Verificar estilo com flake8
flake8 .
```

---

## Testes

```bash
# Todos os testes (exceto E2E)
pytest tests/test_unit.py tests/test_integration.py tests/test_functional.py -v

# Testes E2E (requer Chrome instalado)
pytest tests/test_e2e.py -v

# Todos os testes
pytest
```

---

## Endpoints da API

| Método | Rota                        | Descrição                  |
|--------|-----------------------------|----------------------------|
| GET    | `/`                         | Interface web              |
| GET    | `/books`                    | Listar todos os livros     |
| GET    | `/books?q=termo`            | Pesquisar livros           |
| GET    | `/books/<id>`               | Obter livro por ID         |
| POST   | `/books`                    | Criar novo livro           |
| PUT    | `/books/<id>`               | Atualizar livro            |
| DELETE | `/books/<id>`               | Excluir livro              |
| GET    | `/books/stats`              | Estatísticas da biblioteca |
| POST   | `/books/<id>/borrow`        | Emprestar livro            |
| POST   | `/books/<id>/return`        | Devolver livro             |

---

## TDD — Test Driven Development

A funcionalidade de **Empréstimo e Devolução de Livros** foi implementada seguindo o ciclo TDD:

### Fase RED (Vermelho) — Testes falhando

Primeiro, foram escritos os testes para os endpoints `/borrow` e `/return` antes de qualquer implementação:

```python
def test_borrow_book(client, sample_book):
    response = client.post(f"/books/{sample_book['id']}/borrow")
    assert response.status_code == 200
    assert response.get_json()["available"] is False

def test_return_book(client, sample_book):
    client.post(f"/books/{sample_book['id']}/borrow")
    response = client.post(f"/books/{sample_book['id']}/return")
    assert response.status_code == 200
    assert response.get_json()["available"] is True
```

Resultado: `FAILED` — os endpoints e funções não existiam.

### Fase GREEN (Verde) — Implementação mínima

Foram adicionadas as funções `borrow_book()` e `return_book()` em `services.py` e as rotas correspondentes em `routes.py`, com o mínimo necessário para os testes passarem.

Resultado: `PASSED`

### Fase REFACTOR (Refatoração) — Melhoria sem quebrar testes

- Adicionado tratamento de erro para livro já emprestado → HTTP **409 Conflict**
- Adicionado tratamento de erro para devolução de livro não emprestado → HTTP **409 Conflict**
- Adicionado tratamento de livro não encontrado → HTTP **404 Not Found**
- Lógica de negócio centralizada na camada de serviço

Resultado: `PASSED` (todos os testes continuam passando)

---

## Estrutura do projeto

```
├── app/
│   ├── __init__.py        # Factory da aplicação Flask
│   ├── models.py          # Classe Book
│   ├── routes.py          # Rotas da API
│   ├── services.py        # Lógica de negócio
│   └── templates/
│       └── index.html     # Interface web
├── tests/
│   ├── conftest.py        # Fixtures compartilhadas
│   ├── test_unit.py       # Testes unitários (40+ testes)
│   ├── test_integration.py# Testes de integração (20+ testes)
│   ├── test_functional.py # Testes funcionais (5 testes)
│   └── test_e2e.py        # Testes E2E com Selenium (3 testes)
├── .github/
│   └── workflows/
│       └── ci.yml         # Pipeline GitHub Actions
├── .flake8
├── pyproject.toml
├── pytest.ini
├── requirements.txt
└── run.py
```
