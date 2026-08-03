<div>

# Production Ready RAG Application 

<!-- One-line tagline: what it does and who it's for -->

> A modular RAG backend for document ingestion, vector search, and LLM-powered answers.

<!-- Shields / badges -->

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)
![Build](https://img.shields.io/github/actions/workflow/status/[username]/[repo]/ci.yml)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)


</div>

---

## Table of contents

- [Overview](#overview)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Project structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview
MiniRAG is a FastAPI-based retrieval-augmented generation backend built for document search, knowledge extraction, and answer generation.
It combines document processing, embeddings, vector storage, and configurable LLM providers behind a clean API.
The project is designed to run locally or in Docker with a production-friendly stack for storage, observability, and deployment.


---

## Features

- ✅ Document ingestion and chunking for knowledge-base workflows.
- ✅ Vector search using pgvector or Qdrant.
- ✅ Multi-provider LLM support for generation and embeddings.
- ✅ Async database access with PostgreSQL.
- ✅ Metrics and service monitoring for operational visibility.
- 🚧 Extended evaluation and retrieval tooling _(in progress)_
- 📋 Search and ingestion workflow hardening _(planned)_

---

## Tech stack

| Layer             | Technology                                                                | Why                                                      |
| ----------------- | ------------------------------------------------------------------------- | -------------------------------------------------------- |
| API layer         | FastAPI, Uvicorn, Starlette                                               | Async HTTP API for ingestion, retrieval, and NLP routes. |
| Language          | Python 3.12                                                               | Primary application runtime.                             |
| Data access       | SQLAlchemy, Alembic                                    | Async PostgreSQL access and schema migrations.           |
| Vector storage    | pgvector, Qdrant                                                          | Similarity search and retrieval storage backends.        |
| LLM providers     | OpenAI, Cohere, Google GenAI                                              | Configurable generation and embedding providers.         |
| RAG orchestration | LangChain, langchain-community                                            | Document and model integration helpers.                  |
| Document parsing  | PyMuPDF, python-multipart, aiofiles                                       | File upload and PDF/document extraction.                 |
| Configuration     | python-dotenv, pydantic-settings                                          | Environment-driven application settings.                 |
| Observability     | Prometheus, starlette_exporter, Grafana  | Metrics collection and dashboarding.                     |
| Edge / proxy      | Nginx                                                                     | Reverse proxy and HTTP entrypoint in Docker.             |
| Containerization  | Docker, Docker Compose                                                    | Local and production-style service orchestration.        |
|


## Getting started

### Prerequisites

Make sure you have the following installed before proceeding:

- Python 3.12 or later
- Docker and Docker Compose
- PostgreSQL with pgvector support, or Qdrant
- One LLM provider account if you plan to use hosted generation or embeddings

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Bosha-a/mini_rag.git
cd mini_rag

# 2. Install dependencies
pip install -r src/requirements.txt

# 3. Set up environment variables
# → Create the environment files used by Docker and the app

# 4. Run database migrations (if applicable)
alembic upgrade head

# 5. Start the development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The app will be running at `http://localhost:8000`.

---

## Project structure

```
mini_rag/
├── docker/
│   ├── docker-compose.yaml
│   ├── minirag/
│   ├── nginx/
│   └── prometheus/
├── src/
│   ├── controllers/
│   ├── helpers/
│   ├── models/
│   ├── routes/
│   ├── stores/
│   ├── utils/
│   └── main.py
├── tests/
├── LICENSE
└── README.md
```

---

## Roadmap

- [x] Building RAG Pipeline
- [x] Building scalable backend system 
- [ ] Building website for interaction

---

## Contributing

Contributions are what make open source great — any contribution is **genuinely appreciated**.

1. Fork the repo
2. Create your feature branch: `git checkout -b feat/new-feature`
3. Commit your changes: `git commit -m 'feat: add new feature'`
4. Push to the branch: `git push origin feat/new-feature`
5. Open a Pull Request

---

## License

Distributed under the **APACHE License**. See [LICENSE](LICENSE) for more information.

