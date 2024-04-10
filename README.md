# fasb-onboard

# FastAPI + Alembic + SQLModel + Authentication/Authorization Onboarding

Configure to use Postgresql and Auth0

Uses PDM as package manager

## Installation

1. Get github repository

   ```bash
   git clone https://github.com/gmartindelcye/fasb-onboard.git
   ```

2. Create virtual environment and activate it

   ```bash
   python -m venv .venv
   source.venv/bin/activate
   ```

3. Install dependencies

   ```bash
   pdm install
   ```

4. Copy `env-example` to `.env` and fill it with your data

5. Create database in RDBMS

6. Run alembic migrations

   ```bash
   pdm run alembic upgrade head
   ```

7. Run App
   ```bash
   pdm run uvicorn app.main:app --reload
   ```
