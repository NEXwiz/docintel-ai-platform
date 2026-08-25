# DocIntel AI Platform ⚡

An enterprise-grade document intelligence and Retrieval-Augmented Generation (RAG) platform designed for semantic search, advanced format-aware chunking, and interactive grounded Q&A over complex documents.

---

## 🌟 Key Features

- **🧠 Interactive Grounded Q&A:** Query single or multiple documents with high-precision semantic retrieval and source chunk citations.
- **📄 Advanced Format-Aware Chunking:**
  - **PDF Layout Parsing:** Multi-column layout awareness, table preservation, and page boundary handling.
  - **HTML Extraction:** Semantic tag traversal via BeautifulSoup, stripping script/style noise.
  - **Markdown Structure:** Heading hierarchy preservation (`#`, `##`, `###`), frontmatter stripping, and atomic code block handling.
- **⚡ Dynamic & Semantic Chunking:**
  - **Auto Dynamic Sizing:** Automatically adjusts token chunk size based on document length.
  - **Semantic Splitting:** Uses local sentence-transformer similarity boundaries to divide topic transitions.
  - **Parent-Child Retrieval:** Indexes small child chunks for retrieval precision while passing larger parent contexts to the LLM.
- **🔍 Vector Search Engine:** High-dimensional vector indexing (3072 dimensions) with Qdrant, filtered by document and tenant boundaries.
- **📊 RAGAS Evaluation Suite:** Built-in automated evaluation pipeline checking Faithfulness, Answer Relevancy, Context Precision, and Context Recall.
- **💻 Ultra-Fast Streamlit UI:** Modern glassmorphic dark interface with 0ms cache-backed page transitions.

---

## 🏗️ Architecture & Tech Stack

```
   ┌────────────────────────────────────────────────────────┐
   │                  Streamlit Web UI                      │
   │               (http://localhost:8501)                  │
   └───────────────────────────┬────────────────────────────┘
                               │ HTTP REST
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │                  FastAPI Backend                       │
   │               (http://localhost:8000)                  │
   ├───────────────────────────┬────────────────────────────┤
   │  • Ingestion & Parsers    │  • Gemini Embedding Engine │
   │  • Format Chunkers        │  • Gemini Generative LLM   │
   │  • Retrieval & Rerank     │  • Evaluation Router       │
   └─────────────┬─────────────────────────────┬────────────┘
                 │                             │
                 ▼                             ▼
   ┌───────────────────────────┐ ┌──────────────────────────┐
   │      Qdrant Vector DB     │ │    PostgreSQL / SQLite   │
   │    (Vectors: 3072-dim)    │ │   (Document Metadata)    │
   └───────────────────────────┘ └──────────────────────────┘
```

- **Frontend:** Streamlit with custom CSS design system
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Pydantic
- **AI & Embeddings:** Google Gemini (`gemini-embedding-001`, `gemini-1.5-flash`)
- **Vector Database:** Qdrant
- **Evaluation:** RAGAS, LangChain, Datasets
- **Deployment:** Docker & Docker Compose

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose installed.
- A Google Gemini API Key (get one from [Google AI Studio](https://aistudio.google.com/)).

---

### 1. Clone the Repository

```bash
git clone https://github.com/NEXwiz/docintel-ai-platform.git
cd docintel-ai-platform
```

---

### 2. Configure Environment Variables

Create your environment configuration file in `backend/.env`:

```bash
# In backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./docintel.db  # or your PostgreSQL / Supabase connection string
QDRANT_HOST=localhost                 # use 'qdrant' if running inside Docker Compose
QDRANT_PORT=6333
```

---

### 3. Run with Docker Compose

To start the full stack (FastAPI Backend + Streamlit UI + Qdrant):

```bash
docker-compose up --build
```

Access the services:
- **Streamlit Web App:** [http://localhost:8501](http://localhost:8501)
- **FastAPI Interactive Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Qdrant Dashboard:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## 🛠️ Local Development (Without Docker)

If you prefer to run services individually in a Python virtual environment:

### 1. Start Qdrant Vector DB
```bash
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 2. Setup Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# Activate virtual environment:
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Run FastAPI Backend
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Run Streamlit UI (in a new terminal)
```bash
# From project root directory
streamlit run streamlit_app.py --server.port 8501
```

---

## 🧪 RAG Evaluation Suite (RAGAS)

Run automated RAG quality benchmarks against the golden dataset:

```bash
# Install eval dependencies
pip install -r evals/requirements.txt

# Execute evaluation benchmark
python evals/run_eval.py
```

The harness computes four core metrics:
- **Faithfulness:** Grounding of the answer in retrieved context.
- **Answer Relevancy:** Relevance of the response to the user query.
- **Context Precision:** Signal-to-noise ratio of retrieved chunks.
- **Context Recall:** Coverage of ground-truth knowledge in retrieved chunks.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to open an issue or submit a pull request on GitHub.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
