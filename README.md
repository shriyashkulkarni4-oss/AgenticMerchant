# 🛒 AgenticMerchant (AgenticBuy)

> **Next-Generation Autonomous 3-Sided E-Commerce Platform** powered by **Google Gemma 2**, **Graphify Knowledge Graphs**, and **Neo4j**.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google Gemma](https://img.shields.io/badge/LLM-Gemma%202-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/gemma)
[![Neo4j](https://img.shields.io/badge/Graph_DB-Neo4j%205-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2016-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![React](https://img.shields.io/badge/Frontend-React%2018%20+%20Vite-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Docker](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)

---

## 💡 Problem Statement

Traditional e-commerce platforms (Shopify, Amazon, WooCommerce) are designed exclusively for **human eyes clicking web buttons**. 

As personal AI assistants (Claude, GPT, Gemini) evolve into autonomous **buying agents**, today's e-commerce ecosystem faces fundamental bottlenecks:
1. **Unstructured Data for Agents**: Webpages are cluttered with HTML banners, dynamic scripts, and visual ads rather than machine-readable entity relationship graphs.
2. **Inflexible, Rigid Pricing**: Merchants cannot dynamically negotiate prices at scale with AI agents without manually intervening or sacrificing profit margins.
3. **Siloed Merchant Catalogs**: There is no universal, unified API that autonomous shopping agents can query across multiple independent merchants simultaneously.

---

## 🚀 The Solution: AgenticMerchant

**AgenticMerchant** transforms any store into an **agent-ready merchant** in minutes. It connects three key stakeholders through a unified autonomous layer:

```
                  ┌──────────────────────────────────────────────┐
                  │          🏪 1. MERCHANT PORTAL               │
                  │  • Website Ingestion & Graphify Parser       │
                  │  • Autonomous Bargaining Rules (Floor/Auto)  │
                  │  • Interactive Visual Entity Graph (Neo4j)   │
                  └──────────────────────┬───────────────────────┘
                                         │ Ingests & Sets Rules
                                         ▼
   ┌───────────────────────────────────────────────────────────────────────────┐
   │                       ⚡ CENTRAL AGENTIC PLATFORM                         │
   │  • Neo4j Knowledge Graph       • PostgreSQL Relational Store              │
   │  • Graphify Deterministic AST   • Dynamic Inventory Context (Active Rows) │
   └───────────────────┬───────────────────────────────────┬───────────────────┘
                       │                                   │
      Direct Bargaining│                                   │ Traversal & Purchases
                       ▼                                   ▼
┌───────────────────────────────────────────┐ ┌────────────────────────────────────────┐
│        🛍️ 2. CONSUMER AGENT CHAT         │ │        🌐 3. UNIFIED LLM API           │
│  • Local Google Gemma 2 Agent (via Ollama)│ │  • Standardized REST / WebSocket API   │
│  • Real-time Live Price Negotiation       │ │  • Machine-Readable Graph Traversal    │
│  • Instant Order Placement & Persistence  │ │  • Autonomous External Agent Orders    │
└───────────────────────────────────────────┘ └────────────────────────────────────────┘
```

---

## ✨ Key Features & Capabilities

### 1. 🕷️ Dynamic Website Ingestion & Graphify
- **One-Click Store Onboarding**: Enter any store URL. The background crawler parses pages, extracts products, pricing, and category structures.
- **Graphify Deterministic Knowledge Graph**: Converts raw scraped HTML into deterministic entity-relationship graphs (`Store` $\rightarrow$ `Category` $\rightarrow$ `Product`) synced directly into **Neo4j**.
- **Interactive Visual Graph Inspector**: Explore store connections with pan/zoom 2D SVG canvas and inspect node thresholds directly.

### 2. 🤝 Autonomous Multi-Round Price Negotiation Engine
Merchants set mathematical guardrails per product:
- **Listed Price**: Standard catalogue price.
- **Auto-Accept Threshold**: Any offer at or above this threshold is accepted instantly.
- **Minimum Floor Price**: The absolute lowest price the merchant will tolerate.
- **Max Negotiation Rounds**: Limits the back-and-forth counter-offers.

### 3. 🧠 Powered by Local Google Gemma 2
- **Zero API Cost & Data Privacy**: Runs local open-weight **Gemma 2** via **Ollama**.
- **Dynamic Live Inventory Injection**: Every user query queries active database items and injects real-time merchant bargaining rules into Gemma's system context.
- **Natural Conversational Sales**: Gemma evaluates shopper offers, counter-offers intelligently between the offer and list price, and seals the deal.

### 4. 📦 100% Dynamic & Persistent Database Storage
- Crawled products, manual additions, and negotiated orders are stored directly in **PostgreSQL**.
- Decrements stock quantities live and retains full transaction history visible even after page reloads.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **LLM Agent Brain** | Google Gemma 2 (`gemma2:2b` / `gemma2:9b`) | Local open-weight intelligence hosted via Ollama |
| **Backend Framework** | FastAPI (Python 3.11) | High-performance asynchronous REST & WebSocket API |
| **Knowledge Graph** | Neo4j 5 + APOC | Graph database storing product hierarchies and relationships |
| **Knowledge Parser** | Graphify (`graphifyy`) | Deterministic structural knowledge graph extraction |
| **Relational DB** | PostgreSQL 16 (asyncpg + SQLAlchemy) | Catalog items, merchants, users, orders, and sessions |
| **Vector Search** | ChromaDB | Semantic embeddings for natural language search |
| **Frontend UI** | React 18, Vite, Tailwind CSS, Lucide | Responsive multi-page sidebar dashboard |
| **Containerization** | Docker & Docker Compose | Containerized microservices setup |

---

## 🚀 Quick Start Guide

### Prerequisites
1. **Docker & Docker Compose** installed and running.
2. **Ollama** installed on your host machine: [Download Ollama](https://ollama.com/)

---

### Step 1: Start Local Gemma via Ollama

Open a terminal on your host machine and pull the model:
```bash
ollama run gemma2:2b
```
*(Verify it is running on `http://localhost:11434`)*

---

### Step 2: Clone & Configure

```bash
git clone https://github.com/shriyashkulkarni4-oss/AgenticMerchant.git
cd AgenticMerchant
cp .env.example .env
```

---

### Step 3: Launch with Docker Compose

Start the database, knowledge graph, and backend services:
```bash
docker compose up -d
```

Verify running containers:
```bash
docker compose ps
```
You should see 4 active healthy containers:
- `agenticbuy-backend` on port `8080`
- `agenticbuy-postgres` on port `5433` (internal 5432)
- `agenticbuy-neo4j` on ports `7474` (browser) and `7687` (bolt)
- `agenticbuy-chromadb` on port `8000`

---

### Step 4: Launch the Frontend

```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser!

---

## 📖 Interactive Walkthrough

### 1. Merchant Dashboard
1. Log in using **1-Click Demo Merchant** (or register as a new merchant).
2. Go to **Website Ingestion**, enter a store domain, and click **Start Ingestion**.
3. Watch the real-time BFS crawler and Graphify extract products and sync them into Neo4j and PostgreSQL.
4. Go to **Knowledge Graph** to visually inspect your store's interconnected nodes.
5. In **Product Catalog**, adjust your **Auto-Accept** and **Floor Minimum** prices.

### 2. Consumer Shopping Chat
1. Log in using **1-Click Demo Consumer** (or register as a consumer).
2. Chat with the **Gemma Shopping Agent**:
   - Ask: *"What products do you have available?"*
   - Make an offer: *"I want to buy the Pro Wireless Headphones. Can I get them for $125?"*
3. Watch Gemma check the merchant's rules in real time, evaluate your offer, and accept or counter!
4. Click **Accept & Complete Purchase** — the order is saved into PostgreSQL, stock is updated, and the order receipt appears in your order history!

---

## 📡 API Endpoints

Interactive Swagger UI documentation is available at: **[http://localhost:8080/docs](http://localhost:8080/docs)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/crawl/` | Trigger website crawler & Graphify pipeline |
| `GET` | `/api/v1/crawl/jobs/{id}` | Poll background crawler status |
| `GET` | `/api/v1/products/` | Filter and retrieve active products |
| `POST` | `/api/v1/products/` | Add a product with price bargaining rules |
| `GET` | `/api/v1/graph/mine` | Fetch full merchant knowledge graph |
| `POST` | `/api/v1/chat/` | Conversational shopping & negotiation with Gemma |
| `GET` | `/api/v1/orders/` | Retrieve order history for merchant/consumer |
| `POST` | `/api/v1/orders/` | Place a verified purchase order |

---

## 👥 Contributors

- **Shriyash Kulkarni** — [@shriyashkulkarni4-oss](https://github.com/shriyashkulkarni4-oss)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
