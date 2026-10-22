# 🛒 AgenticMerchant

**AgenticMerchant** is a 3-sided AI-powered e-commerce platform that connects merchants, consumers, and intelligent agents to create a next-generation shopping experience.

## Overview

AgenticMerchant brings together three distinct interfaces:

| Side | Description |
|------|-------------|
| **Merchant Portal** | Dashboard for merchants to register, manage products, and monitor AI-driven analytics on their catalog. |
| **LLM API** | RESTful + WebSocket API layer that exposes product knowledge graphs and vector search to AI agents and integrations. |
| **Consumer Agent Chatbot** | Conversational shopping assistant powered by local LLMs (Gemma 2 via Ollama) that helps consumers discover, compare, and purchase products through natural language. |

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI (Python 3.11) |
| **Database** | PostgreSQL 16 (relational data) |
| **Knowledge Graph** | Neo4j 5 + APOC (product relationships) |
| **Vector Store** | ChromaDB (semantic embeddings) |
| **LLM Runtime** | Ollama with Gemma 2 9B |
| **Graph Builder** | Graphifyy (automated knowledge graph construction) |
| **Auth** | JWT (python-jose + passlib) |
| **Scraping** | httpx + BeautifulSoup4 + lxml |
| **Containerization** | Docker & Docker Compose |

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Ollama](https://ollama.com/) (for local LLM inference)

### 1. Clone & configure

```bash
git clone https://github.com/your-org/AgenticMerchant.git
cd AgenticMerchant
cp .env.example .env
# Edit .env if you need to change any defaults
```

### 2. Pull the Gemma 2 model

```bash
ollama pull gemma2:9b
```

### 3. Start all services

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL** on port `5432`
- **Neo4j** on ports `7474` (browser) and `7687` (bolt)
- **ChromaDB** on port `8000`
- **Backend API** on port `8080`

### 4. Verify

```bash
curl http://localhost:8080/health
```

## Project Structure

```
AgenticMerchant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── core/                # Config, security, database setup
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── api/                 # API route handlers
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── merchants.py     # Merchant portal endpoints
│   │   │   ├── products.py      # Product CRUD endpoints
│   │   │   ├── chat.py          # Consumer chatbot WebSocket
│   │   │   └── llm.py           # LLM API endpoints
│   │   └── services/            # Business logic layer
│   │       ├── scraper.py       # Web scraping service
│   │       ├── graph.py         # Neo4j knowledge graph service
│   │       ├── vector.py        # ChromaDB vector store service
│   │       └── agent.py         # LLM agent orchestration
│   ├── alembic/                 # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
├── .env
└── README.md
```

## API Documentation

Once the backend is running, interactive API documentation is available at:

- **Swagger UI**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **ReDoc**: [http://localhost:8080/redoc](http://localhost:8080/redoc)

## Development

### Running locally (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

> [!NOTE]
> When running locally, ensure PostgreSQL, Neo4j, and ChromaDB are accessible at the URLs specified in your `.env` file.

### Running migrations

```bash
cd backend
alembic upgrade head
```

## License

This project is licensed under the [MIT License](LICENSE).
