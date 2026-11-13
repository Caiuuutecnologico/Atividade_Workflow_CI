# Tasks API — Workflow CI

Aplicação escolhida para a atividade: uma API REST de tarefas feita em FastAPI, com persistência SQL em PostgreSQL.

## Executar localmente

Requer Python 3.12+ e PostgreSQL. Crie um banco e exporte a URL de conexão:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://tasks:tasks@localhost:5432/tasks"
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

A API fica em `http://localhost:8000`; a documentação interativa está em `/docs`.
O serviço cria a tabela `tasks` ao iniciar.

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/health` | Verifica a aplicação |
| `POST` | `/tasks` | Cria tarefa |
| `GET` | `/tasks` | Lista tarefas |
| `GET` | `/tasks/{id}` | Consulta tarefa |
| `PATCH` | `/tasks/{id}` | Atualiza tarefa |
| `DELETE` | `/tasks/{id}` | Remove tarefa |

## Rodar com Docker

O Compose inicia o PostgreSQL e a API na mesma rede e aguarda o banco ficar saudável antes de iniciar a aplicação:

```sh
docker compose up --build
```

A API fica em `http://localhost:8000` e o PostgreSQL fica disponível na porta interna `5432` para os serviços do Compose. Para encerrar, use `Ctrl+C` e execute `docker compose down`.

## Workflow de CI

O arquivo `.github/workflows/ci.yml` executa em pull requests para `main` ou `develop`, em pushes para `main` e manualmente. Os jobs cobrem:

1. Análise estática e formatação com Ruff.
2. Segurança estática com Bandit e auditoria de dependências com pip-audit.
3. Build do pacote Python.
4. Testes unitários.
5. Testes de integração da API usando um serviço PostgreSQL temporário.
6. Build da imagem Docker, sem publicar em registry.

A imagem só é criada se todas as verificações anteriores passarem. O gatilho de pull request permite que o CI seja executado antes do merge.
