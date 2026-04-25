# DocIntel AI Platform

An AI-powered document intelligence platform for semantic search, intelligent chunking, and interactive Q&A over documents using Retrieval-Augmented Generation (RAG).

![DocIntel Overview](https://via.placeholder.com/800x400?text=DocIntel+AI+Platform) <!-- Optional: replace with your actual app screenshot -->

## 🌟 Features
- **🧠 AI-Powered Q&A:** Converse directly with your documents and ask questions using Retrieval-Augmented Generation.
- **🔍 Semantic Search:** Fast, meaning-based vector search powered by Gemini embeddings and Qdrant.
- **📄 Intelligent Document Processing:** Automated chunking and analysis of uploaded files (PDFs, text, etc.).
- **🔐 Secure Access:** Built-in authentication to ensure your documents remain private.
- **⚡ Modern Stack:** Built with a FastAPI backend, a responsive React (Vite) frontend, and Tailwind CSS for styling.

## 🏗️ Architecture & Tech Stack
- **Frontend:** React (Vite), Tailwind CSS
- **Backend:** Python, FastAPI, SQLAlchemy
- **AI & Embeddings:** Google Gemini API
- **Vector Database:** Qdrant
- **Deployment:** Docker & Docker Compose

## 🚀 Getting Started

The easiest way to get started is by running the entire stack via Docker Compose.

### Prerequisites
- [Docker](https://www.docker.com/get-started) and Docker Compose installed.
- A Gemini API Key (get one from [Google AI Studio](https://aistudio.google.com/)).

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/docintel-ai-platform.git
cd docintel-ai-platform
```

### 2. Environment Setup
Navigate to the `backend/` directory and create a `.env` file:
```bash
cd backend
# Create a .env file based on an example if available, or add the following:
```

Add your Gemini API Key and database configurations to `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_HOST=qdrant
QDRANT_PORT=6333
# Add any other required DB strings or JWT secrets here
```

### 3. Run the application
Go back to the root directory and start the services using Docker Compose:
```bash
cd ..
docker-compose up --build
```

### 4. Access the platform
Once all containers are running successfully, you can access the different services at:
- **Frontend (Web App):** http://localhost:5173
- **Backend (API Docs):** http://localhost:8000/docs
- **Qdrant (Vector DB):** http://localhost:6333/dashboard

## 🛠️ Local Development (Without Docker)

If you prefer to run the components individually without Docker:

**1. Qdrant Vector DB**
```bash
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

**2. Backend (FastAPI)**
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # On Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**3. Frontend (React)**
```bash
cd frontend
npm install
npm run dev
```

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!
Feel free to check [issues page](https://github.com/yourusername/docintel-ai-platform/issues).

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
