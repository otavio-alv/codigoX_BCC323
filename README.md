# Plataforma Jornada Código X

Trabalho prático de Programação Web (UFOP). A plataforma transforma a cartilha
"Primeiros Passos no Digital" da ONG Código X numa trilha interativa para meninas
que estão começando no computador: Pré-Trilha com 13 desafios-tutorial, Trilha com
7 desafios de construção de telas, simuladores, pontos, medalhas e um painel para
as mentoras.

Feito com Django 5.2, PostgreSQL 16 e Tailwind CSS v3.

## O que você precisa ter instalado

- [Python 3.12](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (roda o PostgreSQL)
- [Node.js 20 ou mais novo](https://nodejs.org/) (gera o CSS com o Tailwind)

## Instalação passo a passo

Os comandos abaixo funcionam no terminal do VS Code. Quando o comando for diferente
no Windows, as duas versões aparecem.

1. **Clone o repositório e entre na pasta**

   ```bash
   git clone <endereço-do-repositório>
   cd codigox
   ```

2. **Crie o arquivo `.env`** a partir do exemplo

   ```bash
   cp .env.example .env          # Linux e macOS
   copy .env.example .env        # Windows
   ```

   Abra o `.env` e troque o `SECRET_KEY` por qualquer frase longa.

3. **Suba o banco PostgreSQL** (o Docker Desktop precisa estar aberto)

   ```bash
   docker compose up -d
   docker compose ps             # espere aparecer "healthy"
   ```

   Se a porta 5432 já estiver em uso no seu computador, troque `DB_PORTA` no `.env`
   (por exemplo, para 5433) e troque a porta no `DATABASE_URL` também.

4. **Crie o ambiente virtual do Python e instale as dependências**

   ```bash
   python -m venv .venv
   source .venv/bin/activate     # Linux e macOS
   .venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```

5. **Instale o Tailwind e gere o CSS**

   ```bash
   npm install
   npm run build:css
   ```

   Enquanto estiver mexendo nas telas, deixe `npm run watch:css` rodando num
   terminal separado.

6. **Crie as tabelas e uma conta de administração**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

7. **Rode o servidor** e abra http://localhost:8000

   ```bash
   python manage.py runserver
   ```

## Verificação antes de cada pull request

```bash
python manage.py makemigrations --check
python manage.py test
npm run build:css
```

Os três precisam passar. O GitHub Actions roda a mesma coisa em cada push e em cada
pull request, com um PostgreSQL 16 de verdade (o projeto não usa SQLite).

## Estrutura

| Pasta | O que tem |
| --- | --- |
| `config/` | `settings.py`, `urls.py`, `wsgi.py` |
| `core/` | Layout comum e páginas de erro |
| `contas/` | `Usuaria`, login, logout e permissões por perfil |
| `templates/` | `base.html`, `components/` e páginas 403, 404 e 500 |
| `static/` | `src/input.css` (fonte do Tailwind), `js/` e `img/` |
| `docs/` | Decisões do projeto |

Regras de negócio ficam sempre em `services.py`; as views só chamam os services.

## Como contribuir

- Branch a partir de `develop`: `<tipo>/<issue>-<descricao>`, por exemplo
  `feat/14-concluir-desafio`.
- Commits no formato `<tipo>(<app>): <descrição no imperativo> (#<issue>)`, com os
  tipos `feat`, `fix`, `docs` ou `refactor`. Nunca "update", "ajustes" ou "wip".
- Pull request para `develop` com `Closes #<issue>` na descrição.

As decisões tomadas durante o projeto estão em [`docs/decisoes.md`](docs/decisoes.md).
