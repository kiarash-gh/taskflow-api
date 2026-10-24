
# TaskFlow API

A task management REST API built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- Create, list, retrieve, update, and delete tasks
- Filter tasks by completion status
- Paginate task lists
- Validate requests using Pydantic
- Persist data with PostgreSQL
- Automated API tests with pytest

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- pytest
- Docker Compose

## Local Development

### 1. Start PostgreSQL

```bash
docker compose up -d db
```

### 2. Set up Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file using `.env.example` as a template and configure your local database credentials.

### 3. Create database tables

```bash
python -m app.create_tables
```

### 4. Run the API

```bash
fastapi dev app/main.py
```

API documentation: http://127.0.0.1:8000/docs

### 5. Run tests

```bash
python -m pytest -v
```
